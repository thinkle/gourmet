import pygst
pygst.require("0.10")
import gst

class Player:
    def __init__ (self):
        self.player = gst.element_factory_make('playbin','player')

    def play_file (self,path):
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri','file://'+path)
        self.player.set_state(gst.STATE_PLAYING)

    def stop_play (self,path):
        self.player.set_state(gst.STATE_NULL)
