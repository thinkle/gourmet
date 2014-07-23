import convertGui
import gtk

from gourmet.plugin import ToolPlugin

class ConverterPlugin (ToolPlugin):
    menu_items = '''<placeholder name="StandaloneTool">
    <menuitem action="UnitConverter"/>
    </placeholder>'''

    def setup_action_groups (self):
        self.action_group = gtk.ActionGroup('ConverterPluginActionGroup')
        self.action_group.add_actions([
            ('UnitConverter',None,_('_Unit Converter'),
             None,_('Calculate unit conversions'),self.show_unit_converter)
            ]
                                      )
        self.action_groups.append(self.action_group)

    def show_unit_converter (self, *args):
        try:
            umodel = self.pluggable.umodel
        except AttributeError:
            try:
                umodel = self.pluggable.rg.umodel
            except:
                umodel = None
        convertGui.ConvGui(unitModel=umodel)
        
plugins = [ConverterPlugin]
