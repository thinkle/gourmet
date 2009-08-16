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
from gettext import gettext as _
import threading, gtk, pango, gobject, time
gobject.threads_init()

# _IdleObject etc. based on example John Stowers
# <john.stowers@gmail.com>

class _IdleObject(gobject.GObject):
    """
    Override gobject.GObject to always emit signals in the main thread
    by emmitting on an idle handler
    """
    def __init__(self):
        gobject.GObject.__init__(self)

    def emit(self, *args):
        if args[0]!='progress': print 'emit',args
        gobject.idle_add(gobject.GObject.emit,self,*args)

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
        'completed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        'progress' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                     [gobject.TYPE_FLOAT, gobject.TYPE_STRING]), #percent complete, progress bar text
        'error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_INT, # error number
                                                                gobject.TYPE_STRING, # error name
                                                                gobject.TYPE_STRING # stack trace
                                                                ]),
        'stopped': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []), # emitted when we are stopped
        'pause': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []), # emitted when we pause
        'resume': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []), # emitted when we resume
        'done': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []), # emitted when/however we finish
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

    def __init__ (self, max_concurrent_threads = 2):
        if ThreadManager.__single:
            raise ThreadManager.__single
        self.max_concurrent_threads = max_concurrent_threads
        self.thread_queue = []
        self.count = 0
        self.active_count = 0
        self.threads = []

    def add_thread (self, thread):
        try:
            assert(isinstance(thread,SuspendableThread))
        except AssertionError:
            print 'Class',thread,type(thread),'is not a SuspendableThread'
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
    try:
        return ThreadManager()
    except ThreadManager, tm:
        return tm

class ThreadManagerGui:

    __single__ = None
    paused_text = ' (' + _('Paused') + ')'

    def __init__ (self, parent=None):
        if ThreadManagerGui.__single__:
            raise ThreadManagerGui.__single__
        else:
            ThreadManagerGui.__single__ = self
        self.tm = get_thread_manager()
        self.threads = {}
        if not parent:
            from GourmetRecipeManager import get_application
            parent = get_application().window
        self.dialog = gtk.Dialog(parent=parent,
                                 buttons=(gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE))
        self.dialog.set_title(_('Gourmet Import/Export'))
        self.dialog.connect('response',self.close)
        self.dialog.connect('delete-event',self.delete_event_cb)
        self.sw = gtk.ScrolledWindow()
        self.pbtable = gtk.Table()
        self.last_row = 0
        self.sw.add_with_viewport(self.pbtable); self.pbtable.set_border_width(6)
        self.sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.sw.show_all()
        self.dialog.vbox.add(self.sw)
        self.to_remove = [] # a list of widgets to remove when we close...

    def response (self, dialog, response):
        if response==gtk.RESPONSE_CLOSE:
            self.close()
        
    def register_thread_with_dialog (self, description, thread):
        pb = gtk.ProgressBar(); pb.set_ellipsize(pango.ELLIPSIZE_MIDDLE); pb.set_size_request(300,-1)
        pause_button = gtk.ToggleButton();
        lab = gtk.Label(_('Pause'))
        pause_button.add(lab); pause_button.show_all()
        dlab = gtk.Label(description); dlab.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.pbtable.attach(dlab,0,3,self.last_row,self.last_row+1,xoptions=gtk.FILL,yoptions=gtk.SHRINK)
        self.pbtable.attach(pb,0,1,self.last_row+1,self.last_row+2,xoptions=gtk.FILL,yoptions=gtk.SHRINK)
        self.pbtable.attach(cancel_button,1,2,self.last_row+1,self.last_row+2,xoptions=gtk.SHRINK,yoptions=gtk.SHRINK)
        self.pbtable.attach(pause_button,2,3,self.last_row+1,self.last_row+2,xoptions=gtk.SHRINK,yoptions=gtk.SHRINK)
        # Create an object for easy reference to our widgets in callbacks
        class ThreadBox: pass
        threadbox = ThreadBox()
        threadbox.pb = pb
        threadbox.buttons = [pause_button,cancel_button]
        threadbox.label = dlab
        threadbox.pb.show(); threadbox.label.show()
        threadbox.widgets = [threadbox.pb, threadbox.label] + threadbox.buttons
        threadbox.row = self.last_row
        for b in threadbox.buttons: b.show()
        thread.connect('completed',self.thread_done,threadbox)
        thread.connect('error',self.thread_error,threadbox)
        thread.connect('stopped',self.thread_stopped,threadbox)        
        thread.connect('pause',self.thread_pause,threadbox)
        thread.connect('resume',self.thread_resume,threadbox)
        thread.connect('progress',self.progress_update,threadbox.pb)        
        pause_button.connect('clicked',self.pause_cb,thread)
        cancel_button.connect('clicked',self.cancel_cb,thread)
        self.last_row += 2

    def pause_cb (self, b, thread):
        if b.get_active():
            thread.suspend()
        else:
            self.tm.resume_thread(thread)

    def cancel_cb (self, b, thread):
        thread.terminate()

    def thread_done (self, thread, threadbox):
        for b in threadbox.buttons: b.hide()
        self.to_remove.append(threadbox)
        txt = threadbox.pb.get_text()
        if txt:
            threadbox.pb.set_text(txt + ' ('+_('Done')+')')
        else:
            threadbox.pb.set_text('Done')
        threadbox.pb.set_percentage(1)

    def progress_update (self, thread, perc, txt, pb):
        if perc >= 0.0:
            pb.set_fraction(perc)
        else:
            pb.pulse()
        pb.set_text(txt)

    def thread_error (self, thread, errno, errname, trace, threadbox):
        for b in threadbox.buttons: b.hide()
        threadbox.pb.set_text(_('Error: %s')%errname)
        b = gtk.Button(_('Details'))
        b.connect('clicked',self.show_traceback,errno,errname,trace)
        self.pbtable.attach(b,2,3,threadbox.row+1,threadbox.row+2,xoptions=gtk.SHRINK,yoptions=gtk.SHRINK)
        threadbox.widgets.append(b)
        b.show()
        self.to_remove.append(threadbox)

    def thread_stopped (self, thread, threadbox):
        txt = threadbox.pb.get_text()
        txt += (' ('+_('cancelled') + ')')
        threadbox.pb.set_text(txt)

    def thread_pause (self, thread, threadbox):
        txt = threadbox.pb.get_text()
        txt += self.paused_text
        threadbox.pb.set_text(txt)

    def thread_resume (self, thread, threadbox):
        txt = threadbox.pb.get_text()
        if txt.find(self.paused_text):
            txt = txt[:-len(self.paused_text)]
            threadbox.pb.set_text(txt)
        
    def show (self, *args):
        self.dialog.set_size_request(475,
                                     350)
        self.dialog.present()

    def delete_event_cb (self, *args):
        self.dialog.hide()
        return True

    def close (self, *args):
        while self.to_remove:
            box_to_remove = self.to_remove.pop()
            for w in box_to_remove.widgets:
                w.hide()
                self.pbtable.remove(w)
        self.dialog.hide()

    def show_traceback (self, button, errno, errname, traceback):
        import gourmet.gtk_extras.dialog_extras as de
        de.show_message(label=_('Error'),
                        sublabel=_('Error %s: %s')%(errno,errname),
                        expander=(_('Traceback'),traceback),
                        )

def get_thread_manager_gui ():
    try:
        return ThreadManagerGui()
    except ThreadManagerGui, tmg:
        return tmg

if __name__ == '__main__':
    import gtk
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
    def quit (*args): gtk.main_quit()
    tmg.dialog.connect('delete-event',quit)
    tmg.show()
    gtk.main()
