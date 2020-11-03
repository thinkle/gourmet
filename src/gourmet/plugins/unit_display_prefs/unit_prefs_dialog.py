from gettext import gettext as _

from gourmet.gtk_extras import dialog_extras as de
from gourmet.prefs import Prefs


class UnitPrefsDialog:

    options = [
        (_("Display units as written for each recipe (no change)"),[]),
        (_('Always display U.S. units'),['imperial volume','imperial weight']),
        (_('Always display metric units'),['metric volume','metric mass']),
        ]

    def __init__ (self, reccards):
        self.reccards = reccards
        self.prefs = Prefs.instance()

    def run (self):
        old_pref = self.prefs.get('preferred_unit_groups',[])
        option = de.getRadio(label=_("Automatically adjust units"),
                             sublabel="Choose how you would like to adjust units for display and printing. The underlying ingredient data stored in the database will not be affected.",
                             options=self.options,
                             default=old_pref)
        self.prefs['preferred_unit_groups'] = option
        if option != old_pref:
            for rc in self.reccards:
                rc.ingredientDisplay.display_ingredients()
