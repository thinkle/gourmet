# This library provides a pluggable that lets plugins that *use* our
# key editor to provide extra information based on the ingredient
# key. This will be used to show info in both the key editor and
# recipe card view and possibly to allow editing etc.

from gourmet.plugin_loader import Pluggable
from gourmet.plugin import PluginPlugin
from gourmet import gdebug

# Here's our template -- those implementing will have to take this as
# boilerplate code rather than subclassing it, since it's not possible
# to reliably access one plugin's module from another.

# Begin boilerplate...
#
# For a fuller example, see shopping_associations
class KeyEditorPlugin (PluginPlugin):

    target_pluggable = 'KeyEditorPlugin'

    selected_ingkeys = []

    def setup_treeview_column (self, ike, key_col, instant_apply=False):
        '''Set up a treeview column to display your data.

        The key_col is the column in the treemodel which will contain
        your data in the model. It\'s your responsibility to get
        whatever other data you need yourself.

        If you make this editable, it\'s up to you to apply the
        changes as well to the database. If instant_apply is True,
        then apply them instantly; if False, apply them when this
        class\'s save method is called.
        '''
        raise NotImplementedError

    def save (self):
        '''Save any data the user has entered in your treeview column.
        '''
        pass

    def offers_edit_widget (self):
        '''Return True if this plugin provides an edit button for
        editing data (if you need more than an editable cellrenderer
        to let users edit your data, or would like to act on multiple
        rows.
        '''
        return False

    def setup_edit_widget (self):
        '''Return an edit button to let users edit your data.
        '''
        raise NotImplementedError

    def selection_changed (self, ingkeys):
        '''Selected ingkeys have changed -- currently ingkeys are
        selected (and should be acted on by our edit_widget
        '''
        self.selected_ingkeys = ingkeys

# End boilerplate

class KeyEditorPluginManager (Pluggable):

    '''Manage plugins that provide users the ability to edit extra
    associations, such as nutritional information, shopping list
    categories, etc.'''

    title = 'Title of Whatever we Do'
    targets = ['KeyEditorPlugin']

    __single = None

    @classmethod
    def instance(cls):
        if KeyEditorPluginManager.__single is None:
            KeyEditorPluginManager.__single = cls()

        return KeyEditorPluginManager.__single

    def __init__ (self):
        Pluggable.__init__(self,[PluginPlugin])

    def get_treeview_columns (self, ike, key_col, instant_apply=False):
        return [p.setup_treeview_column(ike, key_col,instant_apply) for p in self.plugins]

    def get_edit_buttons (self, ike):
        buttons = []
        for p in self.plugins:
            if p.offer_edit_button():
                try:
                    buttons.append(p.setup_edit_button())
                except:
                    'Trouble initializing edit button for plugin',p
                    import traceback; traceback.print_exc()
        return buttons

def get_key_editor_plugin_manager ():
    return KeyEditorPluginManager.instance()
