# Copyright (c) 2002 Juri Pakaste
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from __future__ import print_function

import gglobals
import defaults.defaults as defaults
import convert
import keymanager
import shopping
import os.path
import ImageExtras

from OptionParser import args

def thread_debug ():
    print('THREADING DEBUG INFO: ',threading.enumerate())
    t=threading.Timer(args.thread_debug_interval,thread_debug)
    print('(starting timer: ', t, ')')
    t.terminate = lambda *args: t.cancel()
    t.start()

if args.thread_debug:
    import threading
    thread_debug()
elif args.psyco:
    try:
        import psyco
        psyco.full()
    except ImportError:
        # ignore
        pass
