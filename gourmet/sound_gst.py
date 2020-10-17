from gi import require_version
try:
    require_version('Gst', '1.0')
except ValueError as e:
    # gourmet.sound catches ImportError
    raise ImportError("Gst not available") from e
from gi.repository import Gst

class Player:
    def __init__ (self):
        self.player = Gst.ElementFactory.make('playbin2','player')

    def play_file (self,path):
        self.player.set_state(Gst.State.NULL)
        self.player.set_property('uri','file://'+path)
        self.player.set_state(Gst.State.PLAYING)

    def stop_play (self,path):
        self.player.set_state(Gst.State.NULL)
