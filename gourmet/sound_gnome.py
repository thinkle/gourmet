import pygst
pygst.require("0.10")
import gst
#import gnome

class Player:
    def __init__ (self):
        self.player = gst.element_factory_make('playbin','player')
        #gnome.sound_init('localhost')

    def play_file (self,path):
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri','file://'+path)
        self.player.set_state(gst.STATE_PLAYING)
        #gnome.sound_play(path)

    def stop_play (self,path):
        self.player.set_state(gst.STATE_NULL)
        #pass
