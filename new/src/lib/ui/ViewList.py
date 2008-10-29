import gtk
import gtk.gdk as gdk
import gobject
import pango

from gourmet.ui.CellRendererExpander import CellRendererExpander

COL_DIC = { "active"     : 6,
            "pixbuf"     : 0,
            "name"       : 1,
            "view"       : 2,
            "visibility" : 3,
            "is_group"   : 4,
            "category"   : 5 
          }

class ViewListModel(gtk.TreeStore):
    
    __gsignals__ = {
        'drop-received':(gobject.SIGNAL_RUN_LAST,
                          gobject.TYPE_STRING,
                          [gobject.TYPE_STRING]),
        }
    
    def __init__ (self):
        gobject.GObject.__init__(self)
        gtk.TreeStore.__init__(self, 
                               gtk.gdk.Pixbuf,
                               gobject.TYPE_STRING,
                               gobject.TYPE_OBJECT,
                               gobject.TYPE_BOOLEAN,
                               gobject.TYPE_BOOLEAN,
                               gobject.TYPE_STRING,
                               gobject.TYPE_BOOLEAN,)

class ViewList(gtk.TreeView):

    __gsignals__ = {
        'drop-received':(gobject.SIGNAL_RUN_LAST,
                          gobject.TYPE_STRING,
                          [gobject.TYPE_STRING]),
        'view-changed':(gobject.SIGNAL_RUN_LAST,
                          gobject.TYPE_STRING,
                          [gobject.TYPE_OBJECT]),
        }
        
    def __init__ (self):    
        self.real_model = ViewListModel()
        self.filter_model = self.real_model.filter_new()
        self.real_model.connect('drop-received', self.drop_received_cb)
        
        gtk.TreeView.__init__(self, self.filter_model)
        self.set_headers_visible(False)
        self.set_reorderable(True)
        self.set_enable_search(False)
        self.selection = self.get_selection()
        self.set_property('show-expanders', False)
        
        # Main column
        self.main_column = gtk.TreeViewColumn('S_ources')
        self.append_column(self.main_column)
        self.main_column.set_clickable(False)
        
        # Indent columns
        renderer = gtk.CellRendererText()
        renderer.set_properties(xpad=0, visible=False)
        self.main_column.pack_start(renderer, False)
        self.main_column.set_cell_data_func(renderer, self.cell_indent_root)

        renderer = gtk.CellRendererText()
        renderer.set_properties(xpad=0, visible=False)
        self.main_column.pack_start(renderer, False)
        self.main_column.set_cell_data_func(renderer, self.cell_indent_level)
        
        # Pixbuf column
        renderer = gtk.CellRendererPixbuf()
        renderer.set_properties(xpad=8, ypad=1, visible=True)
        self.main_column.pack_start(renderer, False)
        self.main_column.set_cell_data_func(renderer, self.cell_pixbuf)

        # Title column
        renderer = gtk.CellRendererText()
        renderer.set_properties(ellipsize=pango.ELLIPSIZE_END)
        renderer.connect('edited', self.view_name_edited_cb)
        self.main_column.pack_start(renderer, True)
        self.main_column.set_cell_data_func(renderer, self.cell_title)

        # Expander column
        renderer = CellRendererExpander()
        self.main_column.pack_end(renderer, False)
        self.main_column.set_cell_data_func(renderer, self.cell_expander)
        
        self.connect('popup-menu', self.popup_menu_cb)
        self.connect('button-press-event', self.button_press_cb)
        self.connect('key-release-event', self.key_release_cb)
        self.get_selection().connect('changed', self.selection_changed_cb)
        
        self.set_size_request(175, 100)
    
    def popup_menu_cb (self, *args):
        self.emit_popup_menu()

    def drop_received_cb (self, *args):
        self.emit('drop-received', *args)
        
    def button_press_cb (self, widget, event):
        if event.button != 3: return False
        path, col, x, y = self.get_path_at_pos(int(event.x), int(event.y))
        if path is None:
            #rb_gtk_action_popup_menu (uimanager, "/ViewListPopup");
            return True
        iter = self.filter_model.get_iter(path)
        if iter:
            self.selection.select_iter(iter)
        self.emit_popup_menu()
        
    def emit_popup_menu (self):
        w, iter = self.selection.get_selected()
        if not iter: return
        view = self.filter_model.get(iter, COL_DIC["view"])
        if view is not None:
            view[0].show_popup()
        
    def key_release_cb (self, *args):
        pass

    def selection_changed_cb (self, *args):
        model, iter = self.selection.get_selected()
        if model is None: return
        is_group, view = model.get(iter, COL_DIC['is_group'], COL_DIC['view'])
        if view is not None and not is_group:
            self.emit('view-changed', view)

    def view_name_edited_cb (self, *args):
        pass

    def cell_set_background (self, cell, is_group):
        if is_group:
            style = self.get_style()
            color = style.text_aa[gtk.STATE_INSENSITIVE]
            color.red = (color.red + (style.white).red) / 2;
            color.green = (color.green + (style.white).green) / 2;
            color.blue = (color.blue + (style.white).blue) / 2;        
            cell.set_property('cell-background-gdk', color)
        else:
            cell.set_property('cell-background-gdk', None)

    def cell_indent_root (self, column, cell, model, iter): self.cell_indent_level(column, cell, model, iter, 2)
    def cell_indent_level (self, column, cell, model, iter, min_depth=1):
        is_group = model.get(iter, COL_DIC["is_group"])
        path = model.get_path(iter)
        cell.set_properties(text=" ", visible=(len(path) > min_depth))
        self.cell_set_background(cell, is_group[0])

    def cell_pixbuf (self, column, cell, model, iter):
        is_group, pixbuf = model.get(iter, COL_DIC["is_group"], COL_DIC["pixbuf"])
        cell.set_properties(visible=(not is_group), pixbuf=pixbuf)
        self.cell_set_background(cell, is_group)
        
    def cell_title (self, column, cell, model, iter):
        is_group, name = model.get(iter, COL_DIC["is_group"], COL_DIC["name"])
        cell.set_properties(text=name)
        self.cell_set_background(cell, is_group)
        
    def cell_expander (self, column, cell, model, iter):
        is_group = model.get(iter, COL_DIC["is_group"])
        if model.iter_has_child(iter):
            path = model.get_path(iter)
            if self.row_expanded(path):
                style = gtk.EXPANDER_EXPANDED
            else:
                style = gtk.EXPANDER_COLLAPSED
            cell.set_properties(visible=True, expander_style=style)
        else:
            cell.set_property('visible', False)
        self.cell_set_background(cell, is_group[0])

    def view_to_iter (self, view):
        def match_view (model, path, iter, data):
            view = model.get(iter, COL_DIC['view'])
            if view is data[0]:
                data[1] = path
                return True
            return False
        
        data = [view, None]
        self.real_model.foreach(match_view, data)
        if data[1] is not None:
            return self.real_model.get_iter(data[1])
        return None

    def find_group_iter (self, group):
        def match_group (model, path, iter, data):
            if len(path) != 1: return False
            name, is_group = model.get(iter, COL_DIC['name'], COL_DIC['is_group'])
            if is_group and name == data[0]:
                data[1] = iter
                return True
            return False

        data = [group.display_name, None]
        self.real_model.foreach(match_group, data)
        return data[1]

    def get_group (self, group):
        iter = self.find_group_iter(group)
        if iter is None:
            row = [None, group.display_name, None, True, True, group.category, False]
            iter = self.real_model.append(None, row)
            return iter, True
        else:
            return iter, False

    def append (self, view, parent=None):
        expand_path = None
        if parent is not None:
            parent_iter = self.view_to_iter(parent)
        else:
            parent_iter,created = self.get_group(view.group)
            self.real_model.set(parent_iter, COL_DIC['visibility'], True)
            path = self.real_model.get_path(parent_iter)
            expand_path = self.filter_model.convert_child_path_to_path(path)
        row = [view.pixbuf, view.display_name, view, view.visibility, False, view.group.category, False]
        self.real_model.append(parent_iter, row)
        # TODO connect notify
        if expand_path is not None:
            self.expand_row(expand_path, True)
        self.columns_autosize()
        
        
    def remove (self, view):
        pass
