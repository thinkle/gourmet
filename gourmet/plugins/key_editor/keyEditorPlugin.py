from __future__ import print_function

import gtk
import gourmet.plugin
import gourmet.GourmetRecipeManager
import keyEditor
from gettext import gettext as _

class KeyEditorPlugin (gourmet.plugin.ToolPlugin):
    menu_items = '''
        <placeholder name="DataTool">
        <menuitem action="KeyEditor"/>
        </placeholder>
    '''

    def setup_action_groups (self):
        self.action_group = gtk.ActionGroup('KeyEditorActionGroup')        
        self.action_group.add_actions([
            ('KeyEditor',None,_('Ingredient _Key Editor'),
             None,_('Edit ingredient keys en masse'),self.show_key_editor)
            ])
        self.action_groups.append(self.action_group)

    def show_key_editor (self, *args):
        gourmet_app = gourmet.GourmetRecipeManager.get_application()
        ke = keyEditor.KeyEditor(rd=gourmet_app.rd,rg=gourmet_app)
