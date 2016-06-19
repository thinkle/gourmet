from __future__ import print_function

from gourmet.plugin import RecEditorModule, RecEditorPlugin, IngredientControllerPlugin
from gourmet.plugin_loader import PRE,POST
import gtk, gobject, pango
from gourmet.reccard import IngredientEditorModule, RecRef
import keyEditorPluggable
from gettext import gettext as _

ING = 0
ITM = 1
KEY = 2

class IngredientKeyEditor (RecEditorModule):

    name = 'keyeditor'
    label = _('Ingredient Keys')
    ui_string = '''
    <menubar name="RecipeEditorMenuBar">
      <menu name="Edit" action="Edit">
        <placeholder name="EditActions">
          <menuitem name="GuessKeys" action="GuessKeys"/>
          <menuitem name="EditAssociations" action="EditAssociations"/>          
        </placeholder>
      </menu>
    </menubar>
    <toolbar name="RecipeEditorEditToolBar">
      <toolitem name="GuessKeys" action="GuessKeys"/>
      <toolitem name="EditAssociations" action="EditAssociations"/>                
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
        self.extra_widget_table = gtk.Table()
        ew_index = 1
        self.main.pack_start(self.extra_widget_table,expand=False,fill=False)
        self.tv = gtk.TreeView()
        self.tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.tv.get_selection().connect('changed',
                                        self.treeselection_changed_cb)
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
        # Set up extra widgets
        plugin_manager = keyEditorPluggable.get_key_editor_plugin_manager()
        apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        for plugin in plugin_manager.plugins:
            if plugin.offers_edit_widget():
                title_label = gtk.Label(plugin.title)
                widget = plugin.setup_edit_widget()
                self.extra_widget_table.attach(title_label,0,1,ew_index,ew_index+1)
                self.extra_widget_table.attach(widget,1,2,ew_index,ew_index+1)
                title_label.show(); widget.show()
                apply_button.connect('clicked',lambda *args: plugin.apply_widget_val())
                ew_index += 1
        if ew_index > 1:
            self.extra_widget_table.attach(apply_button,1,2,ew_index,ew_index+1)
            apply_button.show()
            self.extra_widget_table.hide()
            self.edit_associations_action.set_visible(True)
            apply_button.connect('clicked',
                                 lambda *args: self.tv.queue_draw())
            
    def setup_action_groups(self):
        self.keyEditorActionGroup = gtk.ActionGroup('RecKeyEditorActionGroup')
        self.keyEditorActionGroup.add_actions([
            ('GuessKeys',None,_('Guess keys'),
             None,_('Guess best values for all ingredient keys based on values already in your database'),
             self.guess_keys_cb),
            ])
        self.keyEditorActionGroup.add_toggle_actions([
            ('EditAssociations',None,_('Edit Key Associations'),
             None,_('Edit associations with key and other attributes in database'),
             self.edit_associations_cb, False),
            ])
        self.edit_associations_action = self.keyEditorActionGroup.get_action('EditAssociations')
        self.edit_associations_action.set_visible(False)
        self.action_groups.append(self.keyEditorActionGroup)
        
    def setup_tree (self):
        item_renderer = gtk.CellRendererText();
        item_renderer.set_property('editable',True)
        item_col = gtk.TreeViewColumn(_('Item'),item_renderer,text=1)
        item_col.set_expand(True)
        key_renderer = gtk.CellRendererCombo()
        key_renderer.set_property('editable',True)
        key_renderer.connect('editing-started',self.start_keyedit_cb)
        key_renderer.connect('edited',self.key_edited_cb)
        key_renderer.set_property('mode',gtk.CELL_RENDERER_MODE_EDITABLE)
        key_renderer.set_property('sensitive',True)
        key_col = gtk.TreeViewColumn(_('Key'),key_renderer,text=2)
        key_col.set_expand(True)
        self.renderers = [key_renderer,item_renderer]
        self.tv.append_column(item_col)
        self.tv.append_column(key_col)
        for r in  key_renderer,item_renderer:
            r.set_property('wrap-mode',pango.WRAP_WORD)
            r.set_property('wrap-width',200)
        self.tv.connect('check-resize',self.resize_event_cb)
        self.tv.connect('size-allocate',self.tv_size_allocate_cb)
        plugin_manager = keyEditorPluggable.get_key_editor_plugin_manager()
        for tvc in plugin_manager.get_treeview_columns(self,
                                                       key_col=2,
                                                       instant_apply=False):
            self.tv.append_column(tvc)


    def auto_wrap_columns (self):
        for col in self.tv.get_columns():
            renderers = col.get_cell_renderers()
            for r in renderers:
                if isinstance(r,gtk.CellRendererText):
                    r.set_property('wrap-mode',pango.WRAP_WORD)
                    r.set_property('wrap-width',col.get_width())

    def resize_event_cb (self, widget, event):
        self.auto_wrap_columns()
        
    def tv_size_allocate_cb (self, widget, allocation):
        self.auto_wrap_columns()
        
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

    def get_key_for_object (self, obj):
        for row in self.model:
            if row[0] == obj:
                return row[2]
        return False

    def treeselection_changed_cb (self, ts):
        keys = []
        def do_foreach (tm, p, i):
            keys.append(tm[p][2])
        ts.selected_foreach(do_foreach)
        plugin_manager = keyEditorPluggable.get_key_editor_plugin_manager()
        for p in plugin_manager.plugins:
            p.selection_changed(keys)
        
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
            row[2] = self.rg.rd.km.get_key(item,1)
            changed = True
        if changed: self.edited = True

    def edit_associations_cb (self, action, *args):
        if action.get_active():
            self.extra_widget_table.show()
        else:
            self.extra_widget_table.hide()
        
    def update_from_ingredient_editor_cb (self, ie, edited):
        #if not edited:
        #    self.update_from_database()
        if edited:
            # Update based on current ingredients...
            ITM = ie.ingtree_ui.ingController.ITEM_COL
            def process_row (row):
                obj = row[0]
                item = row[ITM]
                already_there = False
                if isinstance(obj,RecRef):
                    return
                if item == None: # if this is a group..
                    for child in row.iterchildren():
                        process_row(child)
                    return
                for myrow in self.model:
                    if obj==myrow[0]:
                        already_there = True
                        if item != myrow[1]:
                            myrow[1] = item
                if not already_there:
                    if hasattr(row[0],'ingkey'):
                        ingkey = row[0].ingkey
                    else:
                        ingkey = self.rg.rd.km.get_key(item.split(';')[0],1.0)
                    self.model.append((row[0],item,ingkey))
            for row in ie.ingtree_ui.ingController.imodel:
                process_row(row)
                
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
