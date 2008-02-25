import plugin_loader
import gtk, gobject
from xml.sax.saxutils import escape

class PluginChooser:

    def __init__ (self):
        self.loader = plugin_loader.get_master_loader()
        self.window = gtk.Dialog()
        self.notebook = gtk.Notebook()
        for cat,plugins in self.categorize_plugins().items():
            #self.make_treeview(self.loader.active_plugin_sets)
            plugin_view = self.make_treeview(plugins)
            lab = gtk.Label(cat); lab.show()
            self.notebook.append_page(plugin_view,lab)
            plugin_view.show_all()
        self.add_labels()
        self.window.vbox.add(self.notebook); self.notebook.show()
        self.window.add_buttons(
            #gtk.STOCK_ABOUT,1
            gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE
            )
        self.window.set_default_size(375,400)
        self.window.connect('response',self.response_cb)
        
    def add_labels (self):
        head = gtk.Label()
        head.set_markup(
            '<b><span size="large">'+_('Plugins')+'</span></b>'
            )
        desc = gtk.Label()
        desc.set_markup('<i>Plugins add extra functionality to Gourmet.</i>')
        head.set_alignment(0.0,0.0); desc.set_alignment(0.0,0.0)
        self.window.vbox.pack_start(head,expand=False)
        self.window.vbox.pack_start(desc,expand=False)
        self.window.vbox.set_border_width(12)
        head.show(); desc.show()        

    def categorize_plugins (self):
        categorized = {}
        for module_name,plugin_set in self.loader.available_plugin_sets.items():
            try:
                cat = plugin_set.category
            except AttributeError:
                cat = 'Main'
            if not categorized.has_key(cat): categorized[cat]=[]
            categorized[cat].append((module_name,plugin_set))
        return categorized
    
    def make_list_store (self, plugin_list):
        ls = gtk.ListStore(bool, # activated
                                gobject.TYPE_PYOBJECT, # the plugin-set object with all other info
                                )
        for module_name,plugin_set in plugin_list: #self.loader.available_plugin_sets.items():
            ls.append(
                (module_name in self.loader.active_plugin_sets,
                 plugin_set)
                )
        return ls

    def make_treeview (self, plugin_list):
        tv = gtk.TreeView()        
        toggle_renderer = gtk.CellRendererToggle()
        toggle_renderer.set_property('activatable',True)
        toggle_renderer.set_property('sensitive',True)        
        toggle_renderer.connect('toggled',self.toggled_cb,tv)
        active_col = gtk.TreeViewColumn('Active',toggle_renderer,active=0)
        text_renderer = gtk.CellRendererText()
        text_renderer.set_property('wrap-width',350)
        plugin_col = gtk.TreeViewColumn('Plugin',text_renderer)
        def data_fun (col,renderer,mod,itr):
            plugin_set = mod[itr][1]
            renderer.set_property('markup',
                                  ('<b>'+escape(plugin_set.name)+ '</b>' +
                                   '\n<span size="smaller"><i>' + escape(plugin_set.comment) + '</i></span>')
                                  )
        plugin_col.set_cell_data_func(text_renderer,data_fun)
        plugin_col.set_property('expand',True)
        plugin_col.set_property('min-width',250)
        tv.append_column(plugin_col)
        tv.append_column(active_col)
        ls = self.make_list_store(plugin_list)
        tv.set_model(ls)
        sw = gtk.ScrolledWindow(); sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        sw.add(tv)
        return sw

    def toggled_cb (self, renderer, path, tv):
        ls == tv.get_model()
        print 'Toggled work!'
        plugin_set = ls[path][1]
        prev_state = ls[path][0]
        state = not prev_state
        try:
            if state:
                print 'activate: ',plugin_set
                self.loader.activate_plugin_set(plugin_set)
            else:
                print 'deactivate: ',plugin_set                
                self.loader.deactivate_plugin_set(plugin_set)
        except:
            import gtk_extras.dialog_extras as de
            if state:
                de.show_message(message_type=gtk.MESSAGE_ERROR,
                                label=_('An error occurred activating plugin.'))
            else:
                de.show_message(message_type=gtk.MESSAGE_ERROR,
                                label=_('An error occurred deactivating plugin.'))
            raise
        else:
            ls[path][0] = state

    def response_cb (self, window, response):
        if response==gtk.RESPONSE_CLOSE: self.window.hide()
            
def show_plugin_chooser ():
    pc = PluginChooser()
    pc.window.show()
    return pc
    
if __name__ == '__main__':
    pc = show_plugin_chooser()
    pc.window.connect('delete-event',gtk.main_quit)
    gtk.main()
