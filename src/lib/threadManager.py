# This module is designed to handle all multi-threading processes in
# Gourmet. Separate threads are limited to doing the following things
# with respect to the GUI:
#
#   1. Start a notification dialog with a progress bar
#   2. Update the progress bar
#   3. Finish successfully
#   4. Stop with an error.
#
# If you need to get user inpu in the middle of your threaded process,
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

import threading, gtk, gobject, time
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

class SuspendableThread (threading.Thread, _IdleObject):


    """A class for long-running processes that shouldn't interrupt the
    GUI.

    runnerClass will handle the actual process. runnerClass cannot
    touch the GUI. To interact with the GUI, emit a signal.
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
        self.name = name
        self.suspended = False
        self.terminated = False
        _IdleObject.__init__(self)
        threading.Thread.__init__(self, name=self.name)

    def initialize_thread (self):
        self.initialized = True
        self.start()

    def run (self):
        try:
            print self,'run!'
            self.do_run()
            print self,'Done!'
        except Terminated:
            self.emit('stopped')
        except:
            import traceback
            self.emit('error',
                      'Error during %s'%self.name,
                      traceback.format_exc())
        else:
            self.emit('completed')
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
            print 'suspended!'
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
        assert(isinstance(thread,SuspendableThread))
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
        print thread,'done'
        self.threads.remove(thread)
        self.active_count -= 1
        self.start_queued_threads()        

    def register_thread_paused (self, thread):
        print thread,'paused'        
        self.active_count -= 1
        self.start_queued_threads()

    def register_thread_resume (self, thread):
        print thread,'resume'                
        self.active_count += 1

    def resume_thread (self, thread):
        print 'resuming thread...'
        if self.active_count < self.max_concurrent_threads:
            print 'resume right away!'
            thread.resume()
            self.active_count += 1
        else:
            print 'add to queue'
            self.thread_queue.append(thread)
    
    def start_queued_threads (self):
        print 'Check queue'
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


if __name__ == '__main__':
    class TestThread (SuspendableThread):

        def do_run (self):
            for n in range(1000):
                time.sleep(0.01)
                self.emit('progress',n/1000.0,'%s of 1000'%n)
                self.check_for_sleep()

    class TestInterminable (SuspendableThread):

        def do_run (self):
            while 1:
                time.sleep(0.1)
                self.emit('progress',-1,'Working interminably')
                self.check_for_sleep()
                
    tm = get_thread_manager()
    tm.add_thread(TestInterminable())
    tm.add_thread(TestThread())
    tm.add_thread(TestThread())
    tm.add_thread(TestThread())
    tm.add_thread(TestInterminable())
    tm.threads[0].suspend()
    
    w = gtk.Window()
    vb = gtk.VBox(); w.add(vb)
    vb.add(gtk.Label('Threads Test'))
    
    def progress_cb (thread_obj,perc,msg,pb):
        if perc < 0:
            pb.pulse()
        else:
            pb.set_fraction(perc)
        pb.set_text(msg)

    for t in tm.threads:
        print 'Add pb'
        hb = gtk.HBox()
        pb = gtk.ProgressBar()
        t.connect('progress',progress_cb,pb)
        hb.add(pb)
        b = gtk.ToggleButton('Pause')
        def toggle_pause (b, t):
            if b.get_active(): t.suspend()
            else: tm.resume_thread(t)
        b.connect('toggled',toggle_pause,t)
        hb.add(b)
        vb.add(hb)
    w.show_all()
    def quit ():
        tm.thread_queue = []
        for thr in tm.threads:
            if thr.initialized: thr.terminate()
        gtk.main_quit()
    w.connect('delete-event',quit)
    gtk.main()
