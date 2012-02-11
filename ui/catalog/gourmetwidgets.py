#import os, sys
#execpath = os.path.dirname(__file__)
#sys.path.insert (0, os.path.join(execpath, "../../src/lib"))
#print sys.path

#from gtk_extras import timeEntry, ratingWidget, timeEntry
#import timeScanner

import gtk

class TimeEntry (gtk.Entry):
    __gtype_name__ = 'TimeEntry'

class StarButton (gtk.Button):
    __gtype_name__ = 'StarButton'

class StarImage (gtk.Image):
    __gtype_name__ = 'StarImage'

class LinkedTextView (gtk.TextView):
    __gtype_name__ = 'LinkedTextView'

class LinkedTimeView (LinkedTextView):
    __gtype_name__ = 'LinkedTimeView'
