# This is a shitty workaround to the fact that threading and gtk
# are broken on some OS's. As a temporary solution -- to avoid recoding
# threading stuff -- we implement GourmetFauxThreads, which basically
# presents our own threading style routines go Gourmet but doesn't actually
# do any threading.

import dialog_extras as de
import GourmetThreads, gtk
from gdebug import *
from gettext import gettext as _
debug('Using GourmetFauxThreads',0)

Terminated = GourmetThreads.Terminated

class SuspendableThread (GourmetThreads.SuspendableThread):
    """A SuspendableThread.

    We take a runnerClass which must have a run, suspend, terminate,
    and resume method. We then launch our thread and provide methods
    by the same name that interface with our runnerClass.  Before
    running the run() method, we call pre_hooks. Afterward we call any
    post_hooks. (Pre and post hooks get called with this instance as
    their only argument).
    """

    def initialize_thread (self): pass

    def start (self):
        # I don't think we want this dialog anymore.
        if True:
           #de.getBoolean(
           # label=_('Gourmet will be busy for a while.'),
           # sublabel=_('This may take a long time. Gourmet will be unresponsive while it works. Proceed anyway?'),

           # custom_yes=_('Proceed'),
           # custom_no=gtk.STOCK_CANCEL,
           # cancel=False):
            self.target_func()
        else:
            raise "Action cancelled by user"

    def target_func (self):
        GourmetThreads.SuspendableThread.target_func(self)
        
    def run_hooks (self, hooks):
        GourmetThreads.SuspendableThread.run_hooks(self,hooks)
            
    def suspend (self):
        debug("Can't suspend a faux thread",0)
        self.c.suspend()
    
    def resume (self):
        debug("Can't resume a faux thread",0)
        self.c.resume()

    def terminate (self):
        debug("Can't terminate a faux thread",0)
        self.c.terminate()

    def _threads_enter (self):
        pass

    def _threads_leave (self):
        pass

SuspendableDeletions = GourmetThreads.SuspendableDeletions
get_lock = GourmetThreads.get_lock

class get_lock:
    def __init__ (self):
        pass

    def acquire (self):
        return True

    def release (self):
        return True

    def locked_lock (self):
        return False

def gtk_update ():
    """Update the GUI"""
    while gtk.events_pending():
        gtk.main_iteration()

def gtk_leave ():
    gtk_update()

def gtk_enter ():
    pass

def gtk_threads_init ():
    # Initialize threads anyways -- there's some things (like fetching
    # images from web pages) that really only work in threads but
    # won't risk any GTK badness (anything that's risky will use our
    # FauxThreads anyway)
    import sys
    if sys.platform != 'win32':
        gtk.threads_init()

