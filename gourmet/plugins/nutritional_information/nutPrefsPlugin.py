from gourmet.plugin import PrefsPlugin
from gourmet.prefs import get_prefs
import gtk

partialp = 'include_partial_nutritional_info'
includep = 'include_nutritional_info_in_export'

class NutritionPrefs (PrefsPlugin):

    label = _("Nutritional Information")

    def __init__ (self, *args, **kwargs):
        # Create main widget
        self.widget = gtk.VBox()
        self.prefs = get_prefs()
        label = gtk.Label('Hello world')
        self.include_tb = gtk.CheckButton('Include nutritional information in print-outs and exports')
        self.partial_tb = gtk.CheckButton('Include partial nutritional information in print-outs and exports?')
        self.include_tb.set_active(self.prefs.get(includep,True))
        self.partial_tb.set_active(self.prefs.get(partialp,False))
        self.include_tb.connect('toggled',self.toggle_cb)
        self.partial_tb.connect('toggled',self.toggle_cb)        
        self.widget.pack_start(self.include_tb, expand=False, fill=False)
        self.widget.pack_start(self.partial_tb, expand=False, fill=False)
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
