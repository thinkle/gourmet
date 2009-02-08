from gourmet.plugin import RecEditorModule, RecEditorPlugin, IngredientControllerPlugin
from gourmet.plugin_loader import PRE,POST
import gtk, gobject
from gourmet.reccard import IngredientEditorModule
import keyEditorPluggable

ING = 0
ITM = 1
KEY = 2

class IngredientKeyEditor (RecEditorModule):

    name = 'keyeditor'
    label = _('Ingredient Keys')
    ui = '''
    <menubar name="RecipeEditorMenuBar">
      <menu name="Edit" action="Edit">
        <placeholder name="EditActions">
          <menuitem name="GuessKeys" action="GuessKeys"/>
        </placeholder>
      </menu>
    </menubar>
    <toolbar name="RecipeEditorEditToolBar">
      <toolitem name="GuessKeys" action="GuessKeys"/>
    </toolbar>
    '''

    def setup (self):
        pass

    def setup_main_interface (self):
        self.main = gtk.VBox()
        l = gtk.Label()
        l.set_markup('''<b>%s</b>\n<i>%s</i>'''%(
            _('Ingredient Keys'),
            _('Ingredient Keys are normalized ingredient names used for shopping lists and for calculations.')
            )
                     )
        self.main.pack_start(l,expand=False,fill=False)
        sw = gtk.ScrolledWindow(); sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.main.pack_start(sw)
        self.tv = gtk.TreeView()
        self.setup_model()
        self.setup_tree()
        self.tv.set_model(self.model)
        sw.add(self.tv)
        self.main.show_all()
        self.update_from_database()
        ingredientEditorModule = filter(lambda m: isinstance(m,IngredientEditorModule), self.re.modules)[0]
        ingredientEditorModule.connect('saved',lambda *args: self.update_from_database())
        ingredientEditorModule.connect('toggle-edited', self.update_from_ingredient_editor_cb)
        self.setup_action_groups()
        
    def setup_action_groups(self):
        self.keyEditorActionGroup = gtk.ActionGroup('RecKeyEditorActionGroup')
        self.keyEditorActionGroup.add_actions([
            ('GuessKeys',None,_('Guess keys'),
             None,_('Guess best values for all ingredient keys based on values already in your database'),
             self.guess_keys_cb)
            ])
        self.action_groups.append(self.keyEditorActionGroup)
        
    def setup_tree (self):
        item_renderer = gtk.CellRendererText();
        item_renderer.set_property('editable',True)
        item_col = gtk.TreeViewColumn(_('Item'),item_renderer,text=1)
        key_renderer = gtk.CellRendererCombo()
        key_renderer.set_property('editable',True)
        key_renderer.connect('editing-started',self.start_keyedit_cb)
        key_renderer.connect('edited',self.key_edited_cb)
        key_renderer.set_property('mode',gtk.CELL_RENDERER_MODE_EDITABLE)
        key_renderer.set_property('sensitive',True)
        key_col = gtk.TreeViewColumn(_('Key'),key_renderer,text=2)
        self.tv.append_column(item_col)
        self.tv.append_column(key_col)
        plugin_manager = keyEditorPluggable.get_key_editor_plugin_manager()
        for tvc in plugin_manager.get_treeview_columns(self,
                                                       key_col=2,
                                                       instant_apply=False):
            self.tv.append_column(tvc)

    def start_keyedit_cb (self, renderer, cbe, path_string):
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        item = self.model[path][ITM]
        mod = gtk.ListStore(str)
        for key in self.rg.rd.key_search(item):
            mod.append((key,))
        renderer.set_property('model',mod)
        renderer.set_property('text-column',0)
        if isinstance(cbe,gtk.ComboBoxEntry):
            entry = cbe.child
            completion = gtk.EntryCompletion()
            completion.set_model(mod); completion.set_text_column(0)
            entry.set_completion(completion)
        #mod = renderer.get_property

    def key_edited_cb (self,cell, path, new_text):
        oldkey = self.model[path][2]
        if oldkey != new_text:
            self.emit('toggle-edited',True)
        self.model[path][2] = new_text
        # TODO

    def get_key_for_object (self, obj):
        for row in self.model:
            if row[0] == obj:
                return row[2]
        # TODO
        return False
        
    def setup_model (self):
        self.model = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str)
            
    def update_from_database (self):
        ings = self.rg.rd.get_ings(self.current_rec)
        self.setup_model()
        for i in ings:
            if i.refid:
                continue
            self.model.append((i,i.item,i.ingkey))
        self.tv.set_model(self.model)
        self.edited = False

    # Callbacks

    def guess_keys_cb (self, *args):
        changed = False
        for row in self.model:
            item = row[1]
            row[2] = self.rg.rd.km.get_key(item)
            changed = True
        if changed: self.edited = True
        
    def update_from_ingredient_editor_cb (self, ie, edited):
        #if not edited:
        #    self.update_from_database()
        if edited:
            # Update based on current ingredients...
            ITM = ie.ingtree_ui.ingController.ITEM_COL
            for row in ie.ingtree_ui.ingController.imodel:
                obj = row[0]
                item = row[ITM]
                already_there = False
                for row in self.model:
                    if obj==row[0]:
                        already_there = True
                        if item != row[1]:
                            row[1] = item
                if not already_there:
                    if hasattr(row[0],'ingkey'):
                        ingkey = row[0].ingkey
                    else:
                        ingkey = item.split(';')[0]
                    self.model.append((row[0],item,ingkey))
                
    def save (self, recdic):
        # save...
        plugin_manager = keyEditorPluggable.get_key_editor_plugin_manager()
        for p in plugin_manager.plugins:
            p.save()
        return recdic

class IngredientKeyEditorPlugin (RecEditorPlugin):

    moduleKlass = IngredientKeyEditor
    position = 2

class KeyEditorIngredientControllerPlugin (IngredientControllerPlugin):

    def activate (self, pluggable):
        pluggable.add_hook(POST,'get_extra_ingredient_attributes',
                           self.get_extra_ingattributes_post_hook)

    def get_extra_ingattributes_post_hook (self, retval, ic, ing_obj, ingdict):
        recipe_editor = ic.ingredient_editor_module.re
        key_editor = filter(lambda m: isinstance(m,IngredientKeyEditor), recipe_editor.modules)[0]
        ingkey = key_editor.get_key_for_object(ing_obj)
        if ingkey:
            ingdict['ingkey'] = ingkey
        return ingdict
