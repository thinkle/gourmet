import threading, gtk
from gdebug import *
import traceback

class Terminated (Exception):
    def __init__ (self, value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class SuspendableThread (threading.Thread):
    """A SuspendableThread. We take a runnerClass which must have a
    run, suspend, terminate, and resume method. We then launch our thread
    and provide methods by the same name that interface with our runnerClass.
    Before running the run() method, we call pre_hooks. Afterward we call any
    post_hooks. (Pre and post hooks get called with this instance as their only
    argument."""
    def __init__ (self, runnerClass, name=None, pre_hooks=[], post_hooks=[]):
        self.c = runnerClass
        self.pre_hooks=pre_hooks
        self.post_hooks=post_hooks
        self.name = name
        self.completed = False
        debug("SuspendableThread starting thread.",2)
        threading.Thread.__init__(self, target=self.target_func, name=name)

    def target_func (self):
        self.run_hooks(self.pre_hooks)
        try:
            debug('SuspendableThread Running %s'%self.c,3)
            self.c.run()
        except Terminated:
            dialog_extras.show_message(
                    label=_("%s stopped."%self.name),
                    sublabel=_("%s was interrupted by user request."%self.name)
                    )
        except:
            from StringIO import StringIO
            f = StringIO()
            traceback.print_exc(file=f)
            error_mess = f.getvalue()
            debug('Thread cancelled or failed: running post_hooks',1)
            import gtk,dialog_extras
            self._threads_enter()
            dialog_extras.show_message(
                label=_("%s interrupted"%self.name),
                sublabel=_("There was an error during %s."%self.name),
                expander=(_("_Details"),
                          error_mess),
                message_type=gtk.MESSAGE_ERROR
                )
            self._threads_leave()
            self.run_hooks(self.post_hooks)
            raise
        else:
            self.completed = True
            self.run_hooks(self.post_hooks)

    def run_hooks (self, hooks):
        """We hand all hooks ourselves as an argument"""
        for h in hooks:
            debug('Running %s'%h,3)
            h(self)
        
    def suspend (self):
        debug('suspending thread',0)
        self.c.suspend()

    def resume (self):
        debug('resuming thread',0)
        self.c.resume()

    def terminate (self):
        debug('terminating thread',0)
        self.c.terminate()

    def _threads_enter (self):
        gtk.threads_enter()

    def _threads_leave (self):
        gtk.threads_leave()

class SuspendableDeletions:
    def __init__ (self, rg, recs):
        self.suspended = False
        self.terminated = False
        self.recs = recs
        self.ids = map(lambda r: r.id, self.recs)
        self.rg = rg
        
    def check_for_sleep (self):
        if self.terminated:
            raise Terminated("Deletion Terminated!")
        while self.suspended:
            if self.terminated:
                raise "Deletion Terminated!"
            time.sleep(1)
    
    def run (self):
        debug('running GourmetThreads.py',0)
        rtot = len(self.recs)
        n = 0
        dlen = len(self.ids)
        for i in self.ids:
            self.check_for_sleep()
            r = self.rg.rd.get_rec(i)
            self.rg.set_progress_thr(float(n)/float(rtot),
                                     _("Deleting recipes from database... (%s of %s deleted)"%(n,dlen))
                                       )
            self.rg.delete_rec(r)
            n += 1
        if dlen==1: msg = _('Deleted 1 recipe.')
        else: msg = _('Deleted %s recipes')%len(self.ids)
        self.rg.reset_prog_thr(message=msg)
        self.rg.doing_multiple_deletions=False

    def suspend (self): self.suspended = True

    def terminate (self): self.terminated = True

    def resume (self): self.suspended = False

def get_lock ():
    return threading.Lock()

def gtk_enter ():
    gtk.threads_enter()

def gtk_leave ():
    gtk.threads_leave()

def gtk_threads_init ():
    gtk.threads_init()

def gtk_update ():
    """This is for FauxThreads to use to update the GUI periodically"""
    pass
