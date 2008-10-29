import gtk
from gourmet.dialogs.GladeDialog import GladeDialog

class CategoryEntry (gtk.HBox):

    def __init__ (self):
        gtk.HBox.__init__(self, spacing=6)
        self.build_ui()
        self.connect_signals()
        self.show_all()
        self.lock = False
        
    def build_ui (self):
        self.entry = gtk.Entry()
        self.button = gtk.Button('Select...')
        self.selector = Selector(self)
        self.selector.hide()
        self.pack_start(self.entry)
        self.pack_start(self.button, False)
        self.completion = gtk.EntryCompletion()
        self.entry.set_completion(self.completion)
        self.completion.set_text_column(1)
        self.completion.set_match_func(self.match_func)
    
    def connect_signals (self):
        self.button.connect('clicked', self.show_selector_cb)
        self.entry.connect('changed', self.update_database)
        self.entry.connect('notify::is-focus', self.update_widget)
        self.entry.connect('notify::cursor-position', self.update_key)
        self.entry.connect('notify::text', self.update_key)
        self.completion.connect('match-selected', self.match_selected_cb)
    
    def show_selector_cb (self, *args):
        self.selector.show()
    
    def set_recipe (self, recipe):
        self.recipe = recipe
        self.selector.recipe = recipe
        self.update_widget()

    def set_model (self, model):
        self.model = model
        self.selector.set_model(model)
        self.completion.set_model(model)
    
    def match_selected_cb (self, completion, model, iter):
        title = model.get_value(iter, 1)
        self.insert_text(title)
        return True

    def insert_text (self, text):
        txt = self.entry.get_text()
        midpoint = self.entry.get_position()
        start = txt.rfind(',', 0, midpoint)
        end = txt.find(',', midpoint)
        self.entry.delete_text(start+1, end)
        self.entry.insert_text(text + ',', start+1)
        self.entry.set_position(-1)
    
    def update_widget (self, *args):
        if self.lock: return
        self.lock = True
        self.entry.delete_text(0, -1)
        for cat in self.recipe.categories:
            self.entry.insert_text(cat.name + ',', -1)
        self.lock = False
        
    def update_database (self, entry):
        if self.lock: return
        self.lock = True
        
        text = entry.get_text()
        split = text.split(',')
            
        iter = self.model.get_iter_first()
        while iter is not None:
            cat = self.model.get_value(iter, 0)
            
            found = False
            for s in split:
                if s.strip() == cat.name: found = True

            if found and not cat in self.recipe.categories:
                self.recipe.categories.append(cat)
                self.model.row_changed(self.model.get_path(iter), iter)
            elif not found and cat in self.recipe.categories:
                self.recipe.categories.remove(cat)
                self.model.row_changed(self.model.get_path(iter), iter)
            iter = self.model.iter_next(iter)
        self.lock = False
    
    def update_key (self, entry, prop):
        text = entry.get_text()
        midpoint = entry.get_position()
        start = text.rfind(',', 0, midpoint)
        end = text.find(',', midpoint)
        if end > -1:
            self.key = text[start+1:end].strip()
        else:
            self.key = text[start+1:].strip()

    def match_func (self, completion, key_string, iter):
        model = completion.get_model()
        cat = model.get_value(iter, 0)
        if cat is None:
            return False
        elif self.recipe in cat.recipes:
            return self.key == cat.name
        else:
            return cat.name.find(self.key) == 0
        
class Selector (GladeDialog):
    glade_file = 'categoriesSelector.glade'
    
    def __init__ (self, m):
        GladeDialog.__init__(self)
        self.init_treeview()
        self.n = m
        
    def init_treeview (self):
        renderer = gtk.CellRendererToggle()
        renderer.set_property('activatable', True)
        renderer.connect('toggled', self.toggled_cb)
        self.widgets['treeview'].insert_column_with_data_func(0, 'Check', renderer, self.checkbox_cb)
        renderer = gtk.CellRendererText()
        self.widgets['treeview'].insert_column_with_attributes(1, 'text', renderer, text=1)
        
    def checkbox_cb (self, column, cell, model, iter):
        path = model.get_path(iter)
        cat = model[path][0]
        if cat in self.recipe.categories:
            cell.set_active(True)
        else:
            cell.set_active(False)
        self.n.update_widget()
        
    def set_model (self, model):
        self.model = model
        self.widgets['treeview'].set_model(model)
    
    def toggled_cb (self, renderer, path):
        cat = self.model[path][0]
        if renderer.get_active():
            self.recipe.categories.remove(cat)
        else:
            self.recipe.categories.append(cat)
    
    def close_cb (self, *args):
        self.hide()
