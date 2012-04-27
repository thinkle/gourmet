#!/usr/bin/env python
import gtk, gobject, os.path, time, os, sys, re, threading, gtk.gdk, Image, StringIO, pango, string, traceback
# THIS IS OUR NEW FREEZE TARGET

# UNCOMMENT THE FOLLOWING IMPORT STATEMENTS FOR CX_FREEZE
# stuff that shouldn't be necessary but may be:
#import pygtk, atk, gtk._gtk, pango #gtk stuff
#import Image #PIL stuff
# stuff that is definitely necessary:
import codecs, encodings #encoding basic stuff
import encodings.aliases, encodings.ascii, encodings.base64_codec, encodings.charmap, encodings.cp037, encodings.cp1006, encodings.cp1026, encodings.cp1140, encodings.cp1250, encodings.cp1251, encodings.cp1252, encodings.cp1253, encodings.cp1254, encodings.cp1255, encodings.cp1256, encodings.cp1257, encodings.cp1258, encodings.cp424, encodings.cp437, encodings.cp500, encodings.cp737, encodings.cp775, encodings.cp850, encodings.cp852, encodings.cp855, encodings.cp856, encodings.cp857, encodings.cp860, encodings.cp861, encodings.cp862, encodings.cp863, encodings.cp864, encodings.cp865, encodings.cp866, encodings.cp869, encodings.cp874, encodings.cp875, encodings.hex_codec, encodings.idna, encodings.iso8859_10, encodings.iso8859_13, encodings.iso8859_14, encodings.iso8859_15, encodings.iso8859_1, encodings.iso8859_2, encodings.iso8859_3, encodings.iso8859_4, encodings.iso8859_5, encodings.iso8859_6, encodings.iso8859_7, encodings.iso8859_8, encodings.iso8859_9, encodings.koi8_r, encodings.koi8_u, encodings.latin_1, encodings.mac_cyrillic, encodings.mac_greek, encodings.mac_iceland, encodings.mac_latin2, encodings.mac_roman, encodings.mac_turkish, encodings.mbcs, encodings.palmos, encodings.punycode, encodings.quopri_codec, encodings.raw_unicode_escape, encodings.rot_13, encodings.string_escape, encodings.undefined, encodings.unicode_escape, encodings.unicode_internal, encodings.utf_16_be, encodings.utf_16_le, encodings.utf_16, encodings.utf_7, encodings.utf_8, encodings.uu_codec, encodings.zlib_codec

import gourmet.prefs, gourmet.shopgui, gourmet.reccard, gourmet.convertGui, fnmatch
import gourmet.exporters, gourmet.importers
import gourmet.convert, gourmet.gtk_extras.WidgetSaver, gourmet.version
from gourmet.gdebug import *
from gourmet.gglobals import *
from gettext import gettext as _

sys.stdout = open(os.path.join(gourmetdir,"stdout.log"), "w")
sys.stderr = open(os.path.join(gourmetdir,"stderr.log"), "w")

def thread_debug ():
    print 'THREADING DEBUG INFO: ',threading.enumerate()
    t=threading.Timer(options.thread_debug_interval,thread_debug)
    print '(starting timer: ',t,')'
    t.terminate = lambda *args: t.cancel()
    t.start()
    
if options.thread_debug:
    import threading
    thread_debug()

import gourmet.GourmetRecipeManager
gourmet.GourmetRecipeManager.startGUI()
