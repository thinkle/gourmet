# Copyright (c) 2004, 2005 Tom Hinkle
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

#import sys
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)
import win32ui
import sys

import gtk
w = gtk.Dialog()
l = gtk.Label("Enter commandline arguments below")
w.vbox.pack_start(l)
l.show()
e = gtk.Entry(); e.show()
w.add_action_widget(e,gtk.RESPONSE_OK)
w.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
w.run()
w.hide()
txt = e.get_text()
print txt
sys.argv = [sys.argv[0]] + txt.split(' ')
print 'Args->',sys.argv

from gourmet.OptionParser import *

# Extra imports...
import gourmet.defaults_en,gourmet.defaults_en_GB,gourmet.defaults_es #stuff imported with __import__
import gourmet.prefs, gourmet.shopgui, gourmet.reccard, gourmet.convertGui, fnmatch
import gourmet.exporters, gourmet.importers
import gourmet.convert, gourmet.WidgetSaver, gourmet.version
from gourmet.gdebug import *
from gourmet.gglobals import *
from gettext import gettext as _

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
import gourmet.GourmetRecipeManager
gourmet.GourmetRecipeManager.startGUI()
