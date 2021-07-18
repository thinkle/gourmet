from gi.repository import Gtk

from gourmet.i18n import _
from gourmet.plugin import PrefsPlugin
from gourmet.prefs import Prefs

partialp = 'include_partial_nutritional_info'
includep = 'include_nutritional_info_in_export'

class NutritionPrefs (PrefsPlugin):

    label = _("Nutritional Information")

    def __init__ (self, *args, **kwargs):
        # Create main widget
        self.widget = Gtk.VBox()
        self.prefs = Prefs.instance()
        label = Gtk.Label(label='Hello world')
        self.include_tb = Gtk.CheckButton('Include nutritional information in print-outs and exports')
        self.partial_tb = Gtk.CheckButton('Include partial nutritional information in print-outs and exports?')
        self.include_tb.set_active(self.prefs.get(includep,True))
        self.partial_tb.set_active(self.prefs.get(partialp,False))
        self.include_tb.connect('toggled',self.toggle_cb)
        self.partial_tb.connect('toggled',self.toggle_cb)
        self.widget.pack_start(self.include_tb, False, False, 0)
        self.widget.pack_start(self.partial_tb, False, False, 0)
        self.widget.set_border_width(12)
        self.widget.set_spacing(6)
        self.widget.show_all()

    def toggle_cb (self, tb):
        if tb==self.include_tb:
            if tb.get_active():
                self.prefs[includep] = True
            else:
                self.prefs[includep] = False
                # Force false...
                self.partial_tb.set_active(False)
                self.prefs[partialp] = False
        if tb == self.partial_tb:
            self.prefs[partialp] = tb.get_active()
