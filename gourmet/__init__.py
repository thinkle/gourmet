# Copyright (c) 2002 Juri Pakaste
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import gglobals
import defaults.defaults as defaults
import convert
import keymanager
import shopping
import os.path
import ImageExtras
import OptionParser

from gourmet.OptionParser import *

def thread_debug ():
    print 'THREADING DEBUG INFO: ',threading.enumerate()
    t=threading.Timer(options.thread_debug_interval,thread_debug)
    print '(starting timer: ',t,')'
    t.terminate = lambda *args: t.cancel()
    t.start()

if options.thread_debug:
    import threading
    thread_debug()
elif options.psyco:
    try:
        import psyco
        psyco.full()
    except ImportError:
        # ignore
        pass
