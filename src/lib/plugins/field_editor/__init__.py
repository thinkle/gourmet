from gourmet.plugin import ToolPlugin
import fieldEditor
import gtk

class FieldEditorPlugin (ToolPlugin):

    menu_items = '''<placeholder name="DataTool">
    <menuitem action="FieldEditor"/>
    </placeholder>
    '''

    def setup_action_groups (self):
        self.action_group = gtk.ActionGroup('FieldEditorPluginActionGroup')
        self.action_group.add_actions([
            ('FieldEditor',None,_('Field Editor'),
             None,_('Edit fields across multiple recipes at a time.'),self.show_field_editor
            ),
            ])
        self.action_groups.append(self.action_group)

    def show_field_editor (self, *args):
        self.field_editor = fieldEditor.FieldEditor(self.pluggable.rd, self.pluggable)
        self.field_editor.valueDialog.connect('response',self.response_cb)
        self.field_editor.show()

    def response_cb (self, d, r):
        if r==gtk.RESPONSE_APPLY:
            self.pluggable.update_attribute_models()

    
                                                           

plugins = [FieldEditorPlugin]
