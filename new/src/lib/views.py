import gtk
import gobject
import pango
from gettext import gettext as _
from gettext import ngettext

from gourmet.gglobals import *
from gourmet.gdebug import *
from gourmet import converter
from gourmet.preferences import prefs
from gourmet.ui.CellRendererTime import CellRendererTime
from gourmet.ui.RatingWidget import CellRendererRating

class View (gtk.VBox):
    pixbuf = None
    icon_name = None
    stock_id = None
    display_name = ""
    visibility = False
    group = None
    
    def __init__(self):
        gtk.VBox.__init__(self)
        if self.stock_id is not None:
            pass
        elif self.icon_name is not None:
            icon_theme = gtk.icon_theme_get_default()
            self.pixbuf = icon_theme.load_icon(self.icon_name, 22, gtk.ICON_LOOKUP_USE_BUILTIN)

    def show_popup (self):
        raise NotImplementedError
    
class ViewGroup:
    category = "main"
    
    def __init__ (self, name=None, display_name=None):
        self.name = name
        self.display_name = display_name


###############################################################################
# INDEX VIEW
###############################################################################
class IndexView(View):
    """
    Index view TODO
    """

    ui = """<ui>
      <menubar name="MenuBar">
        <menu name="FileMenu" action="FileMenu">
          <placeholder name="FileActions">
                <menuitem name="New" action="New"/>
          </placeholder>
        </menu>
        <menu name="EditMenu" action="EditMenu">
          <placeholder name="EditActions">
            <menuitem name="Edit" action="Edit"/>
            <menuitem name="Delete" action="Delete"/>
            <menuitem name="Undelete" action="Undelete"/>
          </placeholder>
        </menu>
        <menu name="ViewMenu" action="ViewMenu">
        </menu>
        <menu name="ToolsMenu" action="ToolsMenu">
        </menu>
      </menubar>
      <toolbar name="ToolBar">
        <placeholder name="ToolbarActions">
            <toolitem name="New" action="New"/>
            <toolitem name="Edit" action="Edit"/>
            <toolitem name="Delete" action="Delete"/>
        </placeholder>
      </toolbar>
      <popup name="Popup">
        <menuitem name="Edit" action="Edit"/>
        <menuitem name="Delete" action="Delete"/>
        <menuitem name="Undelete" action="Undelete"/>
      </popup>
    </ui>
    """
  
    __gsignals__ = {
        'selection-changed':(gobject.SIGNAL_RUN_LAST,
                             gobject.TYPE_STRING,
                            [gobject.TYPE_BOOLEAN,]),
        }
  
    sensitive_actions = ['Edit', 'Delete']

    def __init__(self):
        View.__init__(self)

        # setup the interface
        self._build_ui()
        self._setup_search_views()
        self._setup_treeview()
        show_search_btn = not prefs.get('search_as_you_type', True)
        self.search_button.set_property('visible', show_search_btn)
        self.search_entry.grab_focus()

        # connect signals
        self.search_entry.connect('changed', self.do_search_as_you_type)
        self.search_button.connect('clicked', self.search)
        self.treeview.connect('start-interactive-search', lambda *args: self.search_entry.grab_focus())
        #self.treeview.connect('button-press-event', self.on_treeview_click)
        prefs.connect('changed::search_as_you_type', self.on_search_as_you_type_changed)
        prefs.connect('changed::search_regexp', self.on_search_regexp_changed)

    ###########################################################################
    # HOOKS
    ###########################################################################
           
    def attach_window(self, window):
        self.setup_actions(window)
                
    ###########################################################################
    # USER INTERFACE
    ###########################################################################

    def _build_ui(self):
        search_box = gtk.HBox(spacing=6)
        search_label = gtk.Label(_("Search :"))
        self.search_entry = gtk.Entry()
        self.search_button = gtk.Button(stock=gtk.STOCK_FIND)
        search_box.pack_start(search_label, False)
        search_box.pack_start(self.search_entry)
        search_box.pack_start(self.search_button, False)
        search_box.set_property('border-width', 6)
        self.pack_start(search_box, False)
        
        scrolled_wdw = gtk.ScrolledWindow()
        scrolled_wdw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_wdw.set_shadow_type(gtk.SHADOW_IN)
        self.treeview = gtk.TreeView()
        scrolled_wdw.add(self.treeview)
        self.pack_start(scrolled_wdw)
        
        self.show_all()

    def _setup_search_views(self):
        self.last_search = []
        self.view = [] #self.recipes.all()
        self.sort_by = []
        
    def _setup_treeview(self):
        """Create our recipe treemodel."""
        self.model = IndexModel()
        self.model.connect('sort-column-changed',self.on_model_sort)
        self.treeview.set_model(self.model)

        #self._setup_treeview_layout()
        self.treeview.connect('popup-menu', self.on_popup)
        self.treeview.connect('row-activated', self.select_recipe)
        self.treeview.set_rules_hint(True)
        self.treeview.expand_all()
        self.treeview.show()

        self.selection = self.treeview.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.on_selection_changed()
        self.selection.connect("changed",self.on_selection_changed)

    #FIXME
    def _setup_treeview_layout(self):
        """Setup the columns of our recipe index TreeView"""
        self.visible_columns = prefs.get('VISIBLE_COLUMNS', DEFAULT_VISIBLE_COLUMNS)
        n = 0
        for c,t,w in REC_ATTRS:
            n += 1
            title = '_%s' % t
            if c == 'rating':
                renderer = CellRendererRating()
                col = gtk.TreeViewColumn(title, renderer, rating=n)
            elif c in ['preptime','cooktime']:
                renderer = CellRendererTime()
                col = gtk.TreeViewColumn(title, renderer, text=n)
            else:
                renderer = gtk.CellRendererText()
                renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
                col = gtk.TreeViewColumn(title,renderer, text=n)
            pos = -1
            if c in self.visible_columns:
                pos = self.visible_columns.index(c)
            self.treeview.insert_column(col, pos)
            col.set_visible(c in self.visible_columns)
            col.set_clickable(True)
            col.set_property('reorderable',True)
            col.set_property('resizable',True)


    ###########################################################################
    # SEARCH FUNCTIONS
    ###########################################################################

    def do_search_as_you_type (self, *args):
        """If we're searching-as-we-type, search."""
        if prefs.get('search_as_you_type', True):
            self.search()

    def redo_search (self, *args):
        """Force to search again with the same criteras."""
        self.last_search = {}
        self.search()
    
    #TODO same search + regexp
    def search (self, *args):
        #prefs.get('search_regexp', True)
        txt = self.search_entry.get_text()
        search_by = ['title'] #FIXME
        gobject.idle_add(lambda *args: self.do_search(txt, search_by))

    def do_search (self, txt, search_by):
        if txt and search_by:
            self.results = self.recipes
            for by in search_by:
                self.results = self.results.filter(by+" LIKE '%"+txt+"%'")
            self.last_search = self.results
        else:
            self.last_search = None
            self.results = self.recipes
        view = self.results.all()
        self.model.change_view(view)

    def reset_search (self, *args):
        self.results = self.recipes
        self.last_search = None
        self.search()

    ###########################################################################
    # TREE CALLBACKS
    ###########################################################################

    def add_row (self, row):
        self.redo_search()

    def delete_row (self, row):
        self.redo_search()

    def update_row (self, row): 
        self.model.update_row(row)

    ###########################################################################
    # CALLBACKS
    ###########################################################################

    def on_search_as_you_type_changed(self, *args):
        """Toggle search-as-you-type option."""
        if prefs['search_as_you_type']:
            self.search_button.hide()
        else:
            self.search_button.show()

    def on_search_regexp_changed(self, *args):
        self.redo_search()

    def on_popup(self, event):
        def func (menu):
            return int(event.x_root),int(event.y_root),True
        self.popup.popup(None, None, func, event.button, event.time)

    def on_selection_changed(self, *args):
        """Callback on selection change."""
        selected = bool(self.selection.get_selected_rows()[1])
        self.emit('selection-changed', selected) #FIXME

    def on_model_sort(self, model, sorts):
        self.sort_by = sorts
        self.last_search = None
        self.search()        
  
    ###########################################################################
    # INTERFACE WITH MODEL
    ###########################################################################

    def get_selected_instances(self):
        def foreach(model, path, iter, instances):
            try:
                instances.append(model[path][0])
            except:
                debug("DEBUG: There was a problem with iter: %s path: %s"%(iter,path),1)
        instances = []
        if self.selection:
            self.selection.selected_foreach(foreach, instances)
        return recs

###############################################################################
# INDEX MODEL
###############################################################################

class IndexModel(gtk.ListStore):
    """
    A ListStore to hold our recipes in 'pages' so we don't load our
    whole database at a time.
    """

    def __init__(self, cols=[]):       
        cols = [('instance',gobject.TYPE_PYOBJECT,)] + cols
        self.columns = [c[0] for c in cols]
        self.column_types = [c[1] for c in cols]
        gtk.ListStore.__init__(self, *self.column_types)

        self.length = 0
        self.update_tree()

    def change_view(self, view):
        self.view = view
        self.update_tree()
        
    def update_tree(self):
        self.clear()
        self.length = 0
        #for instance in self.view:
        #    self.length += 1
        #    itr = self.append([self._get_value(instance, col) for col in self.columns])

    def _get_value(self, instance, attr):
        return getattr(instance, attr)

    def update_instance(self, instance):
        """Handed a recipe (or a recipe ID), we update its display if visible."""
        for n,row in enumerate(self):
            if row[0].id == instance.id:
                row[0].merge(instance)
                self.update_iter(row)
                break

    def update_iter(self, row):
        """Update an iter so it reflects our background."""
        for n,col in enumerate(self.columns):
            self.set(row.iter, n, self._get_value_(row[0], col))
            
    def __len__(self):
        return self.length
