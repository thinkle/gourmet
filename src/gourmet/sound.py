from gi.repository import Gst

class Player:
    def __init__(self):
        Gst.init()
        self.player = Gst.ElementFactory.make('playbin', 'player')

    def play_file(self, path: str):
        self.player.set_state(Gst.State.NULL)
        self.player.set_property('uri', 'file://' + path)
        self.player.set_state(Gst.State.PLAYING)
