from __future__ import print_function

from gourmet.plugin import PluginPlugin
from gourmet.recipeManager import get_recipe_manager
import gtk
from gettext import gettext as _

class KeyEditorPlugin (PluginPlugin):

    target_pluggable = 'KeyEditorPlugin'
    title = _('Shopping Category')
    tvcs = {}
    ingkeys_to_change = {}
    
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
        renderer = gtk.CellRendererCombo()
        renderer.connect('editing-started',self.start_edit_cb)
        renderer.connect('edited',self.key_edited_cb,(ike,key_col,instant_apply))
        # Build shopcat model...
        self.rd = get_recipe_manager()
        self.shopcat_model = gtk.ListStore(str)
        for val in self.rd.get_unique_values('shopcategory',table=self.rd.shopcats_table):
            if val: self.shopcat_model.append([val])
        renderer.set_property('model',self.shopcat_model)
        renderer.set_property('text-column',0)        
        renderer.set_property('editable',True)
        renderer.set_property('mode',gtk.CELL_RENDERER_MODE_EDITABLE)
        renderer.set_property('sensitive',True)        
        tvc = gtk.TreeViewColumn(self.title,renderer)
        tvc.set_cell_data_func(renderer,self.cell_data_func,key_col)
        self.tvcs[renderer] = tvc
        return tvc
        
    def cell_data_func (self, col, renderer, model, itr, key_col):
        if self.ingkeys_to_change.has_key(model[itr][key_col]):
            cat = self.ingkeys_to_change[model[itr][key_col]]
        else:
            shopcat_row = self.rd.fetch_one(self.rd.shopcats_table,
                                            ingkey=model[itr][key_col])
            if shopcat_row:
                cat = shopcat_row.shopcategory
            else:
                cat = ''
        renderer.set_property('text',cat)
        
    def start_edit_cb (self, renderer, cbe, path_string):
        if isinstance(cbe,gtk.ComboBoxEntry):
            entry = cbe.child
            completion = gtk.EntryCompletion()
            completion.set_model(self.shopcat_model)
            completion.set_text_column(0)
            entry.set_completion(completion)

    def key_edited_cb (self, renderer, path_string, new_text, extra_params):
        ike,ingkey_row,instant_apply = extra_params
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        tvc = self.tvcs[renderer]
        tv = tvc.get_tree_view()
        model = tv.get_model()
        row = model[path]
        ingkey = row[ingkey_row].decode('utf-8')
        renderer.set_property('text',new_text)
        self.ingkeys_to_change[ingkey]=new_text
        if instant_apply:
            self.save()
        elif ike:
            ike.emit('toggle-edited',True)

    def apply_association (self, ingkey,val):
        row = self.rd.shopcats_table.select(self.rd.shopcats_table.c.ingkey==ingkey).execute().fetchone()
        if row:
            origval = row.shopcategory
            self.rd.do_modify(self.rd.shopcats_table,
                              row,
                              {'ingkey':ingkey,
                               'shopcategory':val},
                              id_col='ingkey')
            return ingkey,origval
        else:
            self.rd.do_add(self.rd.shopcats_table,
                           {'ingkey':ingkey,
                            'shopcategory':val}
                           )
            return ingkey,None
        
    def save (self):
        '''Save any data the user has entered in your treeview column.
        '''
        for ingkey,val in self.ingkeys_to_change.items():
            self.apply_association(ingkey,val)
        self.ingkeys_to_change = {}

    def offers_edit_widget (self):
        '''Return True if this plugin provides an edit button for
        editing data in some other window (if you need more than an
        editable cellrenderer to let users edit your data. 
        '''
        return True

    def setup_edit_widget (self):
        '''Return an edit widget to let users edit your data.
        '''
        self.cb = cb = gtk.ComboBoxEntry()
        cb.set_model(self.shopcat_model)
        cb.set_text_column(0)
        entry = cb.child
        completion = gtk.EntryCompletion()
        completion.set_model(self.shopcat_model)
        completion.set_text_column(0)
        entry.set_completion(completion)
        return cb

    def get_widget_val (self):
        return self.cb.child.get_text()

    def apply_widget_val (self):
        val = self.get_widget_val()
        if val:
            for ingkey in self.selected_ingkeys:
                self.apply_association(ingkey,val)
                
                
    def selection_changed (self, ingkeys):
        '''Selected ingkeys have changed -- currently ingkeys are
        selected (and should be acted on by our edit_widget
        '''
        self.selected_ingkeys = ingkeys
