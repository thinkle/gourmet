from gourmet.prefs import get_prefs
from gourmet.gtk_extras import dialog_extras as de
from gettext import gettext as _

class UnitPrefsDialog:

    options = [
        (_("Display units as written for each recipe (no change)"),[]),
        (_('Always display U.S. units'),['imperial volume','imperial weight']),
        (_('Always display metric units'),['metric volume','metric mass']),
        ]

    def __init__ (self, reccards):
        self.reccards = reccards
        self.prefs = get_prefs()
        
    def run (self):
        option = de.getRadio(label=_("Automatically adjust units"),
                             sublabel="Choose how you would like to adjust units for display and printing. The underlying ingredient data stored in the database will not be affected.",
                             options=self.options,
                             default=self.prefs['preferred_unit_groups'])
        old_pref = self.prefs.get('preferred_unit_groups',[])
        self.prefs['preferred_unit_groups'] = option
        if option != old_pref:
            for rc in self.reccards:
                rc.ingredientDisplay.display_ingredients()
