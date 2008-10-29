import os
import gobject
import webbrowser
import time
import thread
import gtkmozembed

from gourmet import gglobals
from gourmet.gdebug import *

def get_profile_subdir(subdir):
    """
    Some webbrowsers need a profile dir. Make it if
    it doesnt exist
    """
    profdir = os.path.join(gglobals.gourmetdir, subdir)
    if not os.access(profdir, os.F_OK):
        os.makedirs(profdir)
    return profdir

class RecipeDisplay(gtkmozembed.MozEmbed):
    """
    Wraps the GTK embeddable Mozilla in the WebBrowser interface
    """
    #set_profile_path is here so it only gets called once
    gtkmozembed.set_profile_path(get_profile_subdir('mozilla'), 'default')

    def __init__(self):
        gtkmozembed.MozEmbed.__init__(self)
        self.url_load_request = False # flag to break load_url recursion
        self.location = ""

    def location_changed(self, location):
        self.location = location
        self.emit("location_changed",self.location)


    def source_changed_cb(self, widget, string):
        print string

    def __del__(self):
        print "---------IF WEIRD THINGS HAPPEN ITS BECAUSE I WAS GC'd TO EARLY-------------------------"
        

