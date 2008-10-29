import gtk
import gobject
from gourmet import converter

class CellRendererTime (gtk.CellRendererText):
    
    time = gobject.property(type=str)
    
    def __init__ (self):
        gtk.CellRendererText.__init__(self)
        self.connect("notify::time", self.notify_time_cb)
        
    def notify_time_cb (self, *args):
        self.props.text = converter.seconds_to_timestring(self.time)
