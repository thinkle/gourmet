from gettext import gettext as _

from gi.repository import Gtk

from gourmet.plugin import ToolPlugin

from . import fieldEditor


class FieldEditorPlugin (ToolPlugin):

    menu_items = '''<placeholder name="DataTool">
    <menuitem action="FieldEditor"/>
    </placeholder>
    '''

    def setup_action_groups (self):
        self.action_group = Gtk.ActionGroup(name='FieldEditorPluginActionGroup')
        self.action_group.add_actions([
            ('FieldEditor',None,_('Field Editor'),
             None,_('Edit fields across multiple recipes at a time.'),self.show_field_editor
            ),
            ])
        self.action_groups.append(self.action_group)

    def show_field_editor (self, *args):
        from gourmet.GourmetRecipeManager import get_application
        self.app = get_application()
        self.field_editor = fieldEditor.FieldEditor(self.app.rd, self.app)
        self.field_editor.valueDialog.connect('response',self.response_cb)
        self.field_editor.show()

    def response_cb (self, d, r):
        if r==Gtk.ResponseType.APPLY:
            self.app.update_attribute_models()




plugins = [FieldEditorPlugin]
