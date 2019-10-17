from gourmet.plugin import ToolPlugin, DatabasePlugin
from gourmet.reccard import RecCardDisplay
from gi.repository import Gtk
from gourmet.plugin_loader import PRE, POST
from . import unit_prefs_dialog
from gourmet.prefs import get_prefs
from gettext import gettext as _

class UnitDisplayPlugin (ToolPlugin):
    menu_items = '''<placeholder name="StandaloneTool">
                    <menuitem action="ShowUnitAdjusterDialog"/>
                  </placeholder>'''
    menu_bars = ['RecipeDisplayMenuBar']
    reccards = []

    def __init__ (self):
        ToolPlugin.__init__(self)

    def activate (self, pluggable):
        if isinstance (pluggable, RecCardDisplay):
            self.reccards.append(pluggable)
            self.add_to_uimanager(pluggable.ui_manager)

    def setup_action_groups (self):
        self.action_group = Gtk.ActionGroup('UnitAdjusterActionGroup')
        self.action_group.add_actions([
            ('ShowUnitAdjusterDialog',None,_('Set _unit display preferences'),
             None,_('Automatically convert units to preferred system (metric, imperial, etc.) where possible.'),
             self.show_converter_dialog),
            ])
        self.action_groups.append(self.action_group)

    def show_converter_dialog (self, *args):
        unit_prefs_dialog.UnitPrefsDialog(self.reccards).run()

class UnitDisplayDatabasePlugin (DatabasePlugin):

    def activate (self, db):
        db.add_hook(PRE,'get_amount_and_unit',self.get_amount_and_unit_hook)

    def get_amount_and_unit_hook (self, db, *args, **kwargs):
        kwargs['preferred_unit_groups'] = get_prefs().get('preferred_unit_groups',[])
        return args,kwargs


plugins = [UnitDisplayPlugin, UnitDisplayDatabasePlugin]
