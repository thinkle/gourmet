# This module is designed to handle all multi-threading processes in
# Gourmet. Separate threads are limited to doing the following things
# with respect to the GUI:
#
#   1. Start a notification dialog with a progress bar
#   2. Update the progress bar
#   3. Finish successfully
#   4. Stop with an error.
#
# If you need to get user input in the middle of your threaded process,
# you need to redesign so that it works as follows:
#
# 1. Run the first half of your process as a thread.
# 2. Upon completion of your thread, run your dialog to get your user
#    input
# 3. Run the second half of your process as a thread.
#
# In this module, we define the following base classes...
#
# A singleton ThreadingManager that tracks how many threads we have
# running, and allows a maximum number of threads to be run at any
# single time.
#
# A SuspendableThread base class for creating and running threaded
# processes.
#
#
import threading
import time
from typing import Any
import webbrowser

from gettext import gettext as _
from gettext import ngettext

from gi.repository import GObject, Gtk, Pango


# _IdleObject etc. based on example John Stowers
# <john.stowers@gmail.com>

class _IdleObject(GObject.GObject):
    """
    Override GObject.GObject to always emit signals in the main thread
    by emmitting on an idle handler
    """
    def __init__(self):
        GObject.GObject.__init__(self)

    def emit(self, *args):
        if args[0]!='progress': print('emit', *args)
        GObject.idle_add(GObject.GObject.emit,self,*args)

class Terminated (Exception):
    def __init__ (self, value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class SuspendableThread (threading.Thread, _IdleObject):


    """A class for long-running processes that shouldn't interrupt the
    GUI.
    """

    __gsignals__ = {
        'completed' : (GObject.SignalFlags.RUN_LAST, None, []),
        'progress' : (GObject.SignalFlags.RUN_LAST, None,
                     [GObject.TYPE_FLOAT, GObject.TYPE_STRING]), #percent complete, progress bar text
        'error' : (GObject.SignalFlags.RUN_LAST, None, [GObject.TYPE_INT, # error number
                                                                GObject.TYPE_STRING, # error name
                                                                GObject.TYPE_STRING # stack trace
                                                                ]),
        'stopped': (GObject.SignalFlags.RUN_LAST, None, []), # emitted when we are stopped
        'pause': (GObject.SignalFlags.RUN_LAST, None, []), # emitted when we pause
        'resume': (GObject.SignalFlags.RUN_LAST, None, []), # emitted when we resume
        'done': (GObject.SignalFlags.RUN_LAST, None, []), # emitted when/however we finish
        }

    def __init__(self, name=None):
        self.initialized = False
        #self.name = name
        self.suspended = False
        self.terminated = False
        self.done = False
        _IdleObject.__init__(self)
        threading.Thread.__init__(self, name=name)

    def initialize_thread (self):
        self.initialized = True
        self.start()

    def connect_subthread (self, subthread):
        '''For subthread subthread, connect to error and pause signals and
        and emit as if they were our own.'''
        subthread.connect('error',lambda st,enum,ename,strace: self.emit('error',enum,ename,strace))
        subthread.connect('stopped',lambda st: self.emit('stopped'))
        subthread.connect('pause',lambda st: self.emit('pause'))
        subthread.connect('resume',lambda st: self.emit('resume'))

    def run (self):
        try:
            self.do_run()
        except Terminated:
            self.emit('stopped')
        except:
            import traceback
            self.emit('error',1,
                      'Error during %s'%self.name,
                      traceback.format_exc())
        else:
            self.emit('completed')
        self.done = True
        self.emit('done')

    def do_run (self):
        # Note that sub-classes need to call check_for_sleep
        # periodically, otherwise pausing & cancelling won't work
        raise NotImplementedError

    def suspend (self):
        self.suspended = True

    def resume (self):
        self.suspended = False

    def terminate (self):
        self.terminated = True
        self.emit('stopped')

    def check_for_sleep (self):
        """Check whether we have been suspended or terminated.
        """
        paused_emitted = False
        emit_resume = False
        if self.terminated:
            raise Terminated('%s terminated'%self.name)
        if self.suspended:
            self.emit('pause')
            emit_resume = True
        while self.suspended:
            if self.terminated:
                raise Terminated('%s terminated'%self.name)
            time.sleep(1)
        if emit_resume:
            self.emit('resume')

    def __repr__ (self):
        try:
            return threading.Thread.__repr__(self)
        except AssertionError:
            return '<SuspendableThread %s - uninitialized>'%self.name

class NotThreadSafe:

    """Subclasses of this do things that are not thread safe. An error
    will be raised if an object that is an instance of this class is
    added to a thread manager.
    """
    pass

class ThreadManager:

    __single = None

    @classmethod
    def instance(cls):
        if ThreadManager.__single is None:
            ThreadManager.__single = cls()

        return ThreadManager.__single

    def __init__ (self, max_concurrent_threads = 2):
        self.max_concurrent_threads = max_concurrent_threads
        self.thread_queue = []
        self.count = 0
        self.active_count = 0
        self.threads = []

    def add_thread (self, thread):
        try:
            assert(isinstance(thread,SuspendableThread))
        except AssertionError:
            print('Class',thread,type(thread),'is not a SuspendableThread')
            raise
        if isinstance(thread,NotThreadSafe):
            raise TypeError("Thread %s is NotThreadSafe"%thread)
        self.threads.append(thread)
        thread.connect('pause',self.register_thread_paused)
        thread.connect('resume',self.register_thread_resume)
        thread.connect('done',self.register_thread_done)
        if self.active_count < self.max_concurrent_threads:
            self.active_count += 1
            thread.initialize_thread()
        else:
            self.thread_queue.append(thread)

    def register_thread_done (self, thread):
        if thread in self.threads:
            self.threads.remove(thread)
            self.active_count -= 1
            self.start_queued_threads()

    def register_thread_paused (self, thread):
        self.active_count -= 1
        self.start_queued_threads()

    def register_thread_resume (self, thread):
        self.active_count += 1

    def resume_thread (self, thread):
        if self.active_count < self.max_concurrent_threads:
            thread.resume()
            self.active_count += 1
        else:
            self.thread_queue.append(thread)

    def start_queued_threads (self):
        while self.active_count < self.max_concurrent_threads and self.thread_queue:
            thread_to_add = self.thread_queue.pop()
            self.active_count += 1
            if thread_to_add.initialized:
                thread_to_add.resume()
            else:
                thread_to_add.initialize_thread()

def get_thread_manager ():
    return ThreadManager.instance()


class ThreadManagerGui:

    __single = None
    paused_text = ' (' + _('Paused') + ')'
    PAUSE = 10

    @classmethod
    def instance(cls):
        if ThreadManagerGui.__single is None:
            ThreadManagerGui.__single = cls()

        return ThreadManagerGui.__single

    def __init__ (self, messagebox=None):
        self.tm = get_thread_manager()
        self.threads = {}

        if messagebox is None:
            # import done here to avoid cycling imports
            from gourmet.GourmetRecipeManager import RecGui
            self.messagebox = RecGui.instance().messagebox
        else:
            self.messagebox = messagebox

        self.to_remove = [] # a list of widgets to remove when we close...

    def response (self, dialog, response):
        if response==Gtk.ResponseType.CLOSE:
            self.close()

    def importer_thread_done(self, thread):
        # The following logic allows different messages to be displayed
        # depending on if a recipe was actually imported or if the user
        # cancelled the request.
        if (len(thread.added_recs) > 0):
            done_message = ngettext("Recipe successfully imported",
                                    "Recipes successfully imported",
                                    len(thread.added_recs))
        elif (len(thread.added_recs) == 0):
            done_message = _("Import Unsuccessful")
        self.notification_thread_done(thread, done_message)

    def notification_thread_done(self, thread, message):
        infobox = Gtk.InfoBar()
        infobox.set_message_type(Gtk.MessageType.INFO)
        infobox.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        infobox.connect('response', lambda ib, response_id: ib.hide())
        infobox.show_all()
        self.messagebox.pack_start(infobox, True, True, 0)

        l = Gtk.Label()
        l.set_markup(message)
        l.connect('activate-link',lambda lbl, uri: webbrowser.open(uri))
        l.show()
        infobox.get_content_area().add(l)
        self.messagebox.show()

    def register_thread_with_dialog (self, description, thread):
        threadbox = Gtk.InfoBar()
        threadbox.set_message_type(Gtk.MessageType.INFO)
        pb = Gtk.ProgressBar()
        pb.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        pause_button = Gtk.ToggleButton(label=_('Pause'))
        threadbox.add_action_widget(pause_button, self.PAUSE)
        dlab = Gtk.Label(label=description)
        dlab.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        cancel_button = threadbox.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        vbox = Gtk.VBox()
        vbox.pack_start(dlab, expand=True, fill=True, padding=0)
        vbox.pack_start(pb, expand=True, fill=True, padding=0)
        threadbox.get_content_area().add(vbox)
        threadbox.show_all()
        self.messagebox.pack_start(threadbox, True, True, 0)
        self.messagebox.show()

        #for b in threadbox.buttons: b.show()
        thread.connect('completed',self.thread_done,threadbox)
        thread.connect('error',self.thread_error,threadbox)
        thread.connect('stopped',self.thread_stopped,threadbox)
        thread.connect('pause',self.thread_pause,threadbox)
        thread.connect('resume',self.thread_resume,threadbox)
        thread.connect('progress',self.progress_update,pb)
        pause_button.connect('clicked',self.pause_cb,thread)
        cancel_button.connect('clicked',self.cancel_cb,thread)

    def pause_cb (self, b, thread):
        if b.get_active():
            thread.suspend()
        else:
            self.tm.resume_thread(thread)

    def cancel_cb (self, b, thread):
        thread.terminate()

    def thread_done (self, thread, threadbox):
        for b in threadbox.get_action_area().get_children(): b.hide()
        threadbox.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        threadbox.connect('response', lambda ib, response_id: ib.hide())
        self.to_remove.append(threadbox)
        pb = threadbox.get_content_area().get_children()[0].get_children()[1]
        txt = pb.get_text()
        if txt:
            pb.set_text(txt + ' ('+_('Done')+')')
        else:
            pb.set_text('Done')
        pb.set_fraction(.01)
        for widget in threadbox.get_content_area().get_children()[0]:
            widget.hide()
        threadbox.hide()

    def progress_update (self, thread, perc, txt, pb):
        if perc >= 0.0:
            pb.set_fraction(perc)
        else:
            pb.pulse()
        pb.set_text(txt)

    def thread_error (self, thread, errno, errname, trace, threadbox):
        threadbox.get_action_area().get_children()[1].hide() # Pause button
        pb = threadbox.get_content_area().get_children()[0].get_children()[1]
        pb.set_text(_('Error: %s')%errname)
        b = threadbox.add_button(_('Details'), 11)
        b.connect('clicked',self.show_traceback,errno,errname,trace)
        b.show()
        self.to_remove.append(threadbox)

    def thread_stopped(self, thread: Any, threadbox: Gtk.InfoBar):
        threadbox.hide()

    def thread_pause (self, thread, threadbox):
        pb = threadbox.get_content_area().get_children()[0].get_children()[1]
        txt = pb.get_text()
        txt += self.paused_text
        pb.set_text(txt)

    def thread_resume (self, thread, threadbox):
        pb = threadbox.get_content_area().get_children()[0].get_children()[1]
        txt = pb.get_text()
        if txt.find(self.paused_text):
            txt = txt[:-len(self.paused_text)]
            pb.set_text(txt)

    def show (self, *args):
        self.messagebox.show()

    def delete_event_cb (self, *args):
        self.messagebox.hide()
        return True

    def close (self, *args):
        while self.to_remove:
            box_to_remove = self.to_remove.pop()
            for w in box_to_remove.widgets:
                w.hide()
                self.pbtable.remove(w)
        self.messagebox.hide()

    def show_traceback (self, button, errno, errname, traceback):
        import gourmet.gtk_extras.dialog_extras as de
        de.show_message(label=_('Error'),
                        sublabel=_('Error %s: %s')%(errno,errname),
                        expander=(_('Traceback'),traceback),
                        )

def get_thread_manager_gui ():
    return ThreadManagerGui.instance()


if __name__ == '__main__':
    from gi.repository import Gtk
    class TestThread (SuspendableThread):

        def do_run (self):
            for n in range(1000):
                time.sleep(0.01)
                self.emit('progress',n/1000.0,'%s of 1000'%n)
                self.check_for_sleep()

    class TestError (SuspendableThread):

        def do_run (self):
            for n in range(1000):
                time.sleep(0.01)
                if n==100: raise AttributeError("This is a phony error")
                self.emit('progress',n/1000.0,'%s of 1000'%n)
                self.check_for_sleep()


    class TestInterminable (SuspendableThread):

        def do_run (self):
            while 1:
                time.sleep(0.1)
                self.emit('progress',-1,'Working interminably')
                self.check_for_sleep()

    tm = get_thread_manager()
    tmg = get_thread_manager_gui()
    for desc,thread in [
        ('Interminable 1',TestInterminable()),
        ('Linear 1',TestThread()),
        ('Linear 2',TestThread()),
        ('Interminable 2',TestInterminable()),
        ('Error 3',TestError())
        ]:
        tm.add_thread(thread)
        tmg.register_thread_with_dialog(desc,thread)
    def quit (*args): Gtk.main_quit()
    tmg.dialog.connect('delete-event',quit)
    tmg.show()
    Gtk.main()
