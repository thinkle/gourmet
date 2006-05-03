import winsound

class Player:
    def __init__ (self):
        #self.player = gst.element_factory_make('playbin','player')
        gnome.sound_init('localhost')

    def play_file (self,path):
        #self.player.set_state(gst.STATE_NULL)        
        #self.player.set_property('uri','file://'+path)
        #self.player.set_state(gst.STATE_PLAYING)
        winsound.PlaySound(path)

    def stop_play (self,path):
        #self.player.set_state(gst.STATE_NULL)
        pass
