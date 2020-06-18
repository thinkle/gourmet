# Copyright (c) 2002 Juri Pakaste
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

# from . import gglobals
# from .defaults import defaults as defaults
# from . import convert
# from . import keymanager
# from . import shopping
# import os.path
# from . import ImageExtras
#
# from .OptionParser import args
#
# def thread_debug ():
#     print('THREADING DEBUG INFO: ',threading.enumerate())
#     t=threading.Timer(args.thread_debug_interval,thread_debug)
#     print('(starting timer: ',t,')')
#     t.terminate = lambda *args: t.cancel()
#     t.start()
#
# if args.thread_debug:
#     import threading
#     thread_debug()

# specify the required GI namespaces version here.
# 'require_version' only needs to be called once to ensures the namespace gets loaded with the given version
from gi import require_version
require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
require_version("Pango", "1.0")
