#import os, sys
#execpath = os.path.dirname(__file__)
#sys.path.insert (0, os.path.join(execpath, "../../src/lib"))
#print sys.path

#from gtk_extras import timeEntry, ratingWidget, timeEntry
#import timeScanner

from gi.repository import Gtk


class TimeEntry (Gtk.Entry):
    __gtype_name__ = 'TimeEntry'

class StarButton (Gtk.Button):
    __gtype_name__ = 'StarButton'

class StarImage (Gtk.Image):
    __gtype_name__ = 'StarImage'

class LinkedTextView (Gtk.TextView):
    __gtype_name__ = 'LinkedTextView'

class LinkedTimeView (LinkedTextView):
    __gtype_name__ = 'LinkedTimeView'
