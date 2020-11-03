from urllib.request import pathname2url as _pathname_to_url

from gi.repository import Gst


class Player:

    def __init__(self):
        Gst.init()
        self.player = Gst.ElementFactory.make('playbin', 'player')


    def play_file(self, filepath: str) -> None:
        uri = _pathname_to_url(filepath)
        self.player.set_state(Gst.State.NULL)
        self.player.set_property('uri', f'file://{uri}')
        self.player.set_state(Gst.State.PLAYING)
