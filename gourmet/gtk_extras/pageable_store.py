import gtk, gobject
from sqlalchemy.types import Boolean, Integer, String, Text, Float
from gourmet.models import Recipe

sqlalchemy_type_map = {Boolean: bool,
                       Integer: int,
                       String: str,
                       Text: str,
                       Float: float,
                       }

def map_sqlalchemy_type(saType):
    for sa, py in sqlalchemy_type_map.iteritems():
        if isinstance(saType, sa):
            return py

class RecModel(gtk.GenericTreeModel):

    __gsignals__ = {
        'page-changed':(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE, #RETURN
                        () # PARAMS
                        ),
        'view-changed':(gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         ()
                         ),
        'view-sort':(gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_PYOBJECT,
                     (gobject.TYPE_PYOBJECT,)
                     ),
        }

    page = 0

    def __init__(self, recipes = list()):
        #self.__gobject_init__()
        gtk.GenericTreeModel.__init__(self)
        self.recipes = recipes
        #self.emit('page-changed')

    def on_get_flags(self):
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return len(Recipe.__table__.columns)

    def on_get_column_type(self, index):
        return map_sqlalchemy_type(list(Recipe.__table__.columns)[index].type)

    # alternatively, we could use the recipe id
    def on_get_iter(self, path):
        return self.recipes[path[0]]

    def on_get_path(self, rowref):
        return self.recipes.index(rowref)

    def get_column_names(self):
        return [i.name for i in list(Recipe.__table__._columns)]

    def on_get_value(self, rowref, column):
        return getattr(rowref, list(Recipe.__table__._columns)[column].name)

    def on_iter_next(self, rowref):
        try:
            i = self.recipes.index(rowref)+1
            return self.recipes[i]
        except IndexError:
            return None

    def on_iter_children(self, rowref):
        if rowref:
            return None
        return self.recipes[0]

    def on_iter_has_child(self, rowref):
        return False

    def on_iter_n_children(self, rowref):
        if rowref:
            return 0
        return len(self.recipes)

    def on_iter_nth_child(self, rowref, n):
        if rowref:
            return None
        try:
            return self.recipes[n]
        except IndexError:
            return None

    def on_iter_parent(self, child):
        return None


class PageableListStore (gtk.ListStore):
    """A ListStore designed to show bits of data at a time.

    We show chunks of data from our parent list in pages of a set size.

    parent_args and parent_kwargs get handed to setup_parent.

    It shouldn't be too hard to expand this to support TreeStores as well.
    """

    page = 0

    # convenient constants for sorting
    OFF = None
    FORWARD = gtk.SORT_ASCENDING
    REVERSE = gtk.SORT_DESCENDING

    __gsignals__ = {
        'page-changed':(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE, #RETURN
                        () # PARAMS
                        ),
        }
    
    def __init__ (self, types, parent_args=[], parent_kwargs={}, per_page=15):
        """
        types is handed to ListStore.__init__ and should be a list of
        types our treestore holds

        parent_args gets handed to setup_parent. In our simple self,
        this is a list of rows to be initiated.

        parent_kwargs are keyword arguments for setup_parent. In our
        simple self, this is unused.

        per_page is the default number of items we show at a time.
        """
        #gtk.ListStore.__init__(self,*types)
        self.__gobject_init__()
        gtk.ListStore.__init__(self, *types)
        self.per_page = per_page
        self._setup_parent_(*parent_args,**parent_kwargs)
        #self.grab_items()
        # a dictionary for tracking our sorting
        self.sort_dict = {}
        self.update_tree()

    def _setup_parent_ (self, *args, **kwargs):
        """By default, all we do is take parent_args as a list of rows to add."""
        self.parent_list = list(args)
        self.unsorted_parent = self.parent_list[0:]

    def _get_length_ (self):
        """Get the length of our full set of data."""
        return len(self.parent_list)

    def _get_slice_ (self,bottom,top):
        """Return a slice of our parent list from bottom to top"""
        return self.parent_list[bottom:top]

    def _get_item_ (self,indx):
        """Return an item for indx.

        By default, we use _get_slice_ to do this. This is somewhat
        counterintuitive, but allows subclasses to only bother writing
        a _get_slice_ method. they can implement the _get_item_ method
        if there is a reason to.
        """
        return self._get_slice_(indx,indx+1)[0]

    def showing (self):
        """Return information about the items we are currently showing.

        We return (bottom,top,total)
        """
        # Don't show an empty page -- if we find ourselves with no
        # recipes, back up a page automatically.
        if len(self)==0 and self.page!=0:
            self.goto_last_page()
        bottom = self.page*self.per_page + 1
        top = self.page*self.per_page+len(self)
        total = self._get_length_()
        return int(bottom),int(top),int(total)

    def set_page (self, n):
        """Set page to n and update our view accordingly"""
        self.page = n
        self.update_tree()
        self.emit('page-changed')
        
    def goto_first_page (self):
        if self.page!=0: self.set_page(0)

    def goto_last_page (self):
        last_page = self.get_last_page()
        if self.page != last_page:
            self.set_page(last_page)
    
    def next_page (self): 
        if (self.page+1)*self.per_page < self._get_length_():
            self.set_page(self.page + 1)
            
    def prev_page (self):
        if self.page > 0: self.set_page(self.page - 1)

    def get_last_page (self):
        """Return the number of our last page."""
        nrecs = int(self._get_length_())
        self.per_page = int(self.per_page)#just in case
        pages = (nrecs / self.per_page) - 1
        if nrecs % self.per_page: pages+=1
        return pages

    def change_items_per_page (self, n):
        current_indx = self.per_page * self.page
        self.per_page = n
        new_page = current_indx / self.per_page
        self.page = new_page
        self.update_tree()
        self.emit('page-changed')

    def update_iter (self, itr):
        """Update an iter so it reflects our background.

        itr can be a treeiter or a path"""
        # This will only work with ListStores -- if we update to
        # accomodate TreeStores, this is one of the things that must
        # change
        if type(itr)==tuple:
            path = itr
            itr=self.get_iter(path)
        else:
            path = self.get_path(itr)
        indx = path[0] + (self.page * self.per_page)
        # set takes column number, column value, column number, column value, etc.
        args = []
        for num_and_col in enumerate(self._get_item_(indx)): args.extend(num_and_col)
        self.set(itr,*args)
        

    def update_tree (self):
        """Update our tree based on current page, etc."""
        # clear the existing rows...
        for n in range(len(self)):
            self.remove(self.get_iter(0,))
        # and add the new ones...
        length = self._get_length_()
        start_at = self.page * self.per_page
        end_at = (self.page+1) * self.per_page
        if start_at > length: return # we're empty then...
        if end_at > length: end_at = length
        for row in self._get_slice_(int(start_at),int(end_at)):
            try: self.append(row)
            except TypeError:
                print 'columns          : ',self.columns
                print 'problem adding row ',row
                raise
            except ValueError:
                print 'columns          : ',self.columns
                print 'problem adding row ',row
                raise
    # Sorting functions

    def sort (self, column, direction=FORWARD):
        """Add new sort term in direction.

        Note -- to remove term we use direction=OFF
        """

        self.sort_dict[column]=direction
        if direction==self.OFF:
            self.parent_list = self.unsorted_parent
            return
        if direction==self.FORWARD: shift_by = 1
        elif direction==self.REVERSE: shift_by = -1
        self.parent_list.sort(lambda r1,r2: ((r1[column]>r2[column] and 1*shift_by) or
                                             (r1[column]<r2[column] and -1*shift_by) or
                                             0)
                              )
        self.update_tree()

    def toggle_sort (self, column):
        """Toggle sorting by column.

        We cycle through three positions: forward, backward, None,
        which is what standard gtk.TreeSort does as well!

        Return the direction we've toggled to (this allows our caller
        to be able to update the UI without having to know beforehand
        which direction the sort will end up in).
        """
        current = self.sort_dict.get(column,self.OFF)
        if current==self.OFF:
            toggle_to = self.FORWARD
        elif current==self.FORWARD:
            toggle_to = self.REVERSE
        else:
            toggle_to = self.OFF
        self.sort(column,toggle_to)
        return toggle_to

class PageableTreeStore (gtk.TreeStore, PageableListStore):
    """A TreeStore designed to show bits of data at a time.

    We show chunks of data from our parent in pages of a set size.

    Subclasses need to implement a setup_parent() method which can
    take args and kwargs.
    """

    __gsignals__ = {
        'page-changed':(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE, #RETURN
                        () # PARAMS
                        ),
        }

    page = 0

    # convenient constants for sorting
    OFF = None
    FORWARD = gtk.SORT_ASCENDING
    REVERSE = gtk.SORT_DESCENDING

    def __init__ (self, types, parent_args=[], parent_kwargs={}, per_page=15):
        """
        types is handed to TreeStore.__init__ and should be a list of
        types our treestore holds

        parent_args gets handed to setup_parent. In our simple self,
        this is a list of rows to be initiated.

        parent_kwargs are keyword arguments for _setup_parent_. In our
        simple self, this is unused.

        per_page is the default number of items we show at a time.

        We include all children by default -- subclasses can override
        update_tree to get fancier.
        """
        self.__gobject_init__()
        gtk.TreeStore.__init__(self, *types)        
        self.per_page = per_page
        self._setup_parent_(*parent_args,**parent_kwargs)
        self.update_tree()
        self.sort_dict = {}

    def update_tree (self):
        """Update our tree based on current page, etc."""
        # clear the existing rows...
        for n in range(len(self)):
            self.remove(self.get_iter(0,))
        # and add the new ones...
        length = self._get_length_()
        start_at = self.page * self.per_page
        end_at = (self.page+1) * self.per_page
        if start_at > length: return # we're empty then...
        if end_at > length: end_at = length
        for row in self._get_slice_(int(start_at),int(end_at)):
            itr=self.append(None,row)
            self.append_descendants(itr)
        self.emit('page-changed')

    def append_descendants (self, itr):
        for child in self._get_children_(itr):
            child_itr=self.append(itr,child)
            self.append_descendants(child_itr)

    def _get_children_ (self, itr):
        return []
    
class ColumnSortSetterUpper:
    """Make tree-column setting up easy for our custom models.

    Namely, sorting will simply involve

    cssu=ColumnSortSetterUpper(treemodel)
    cssu.setup_column_sort(tree_view_column,n)

    where n is the model column sorted on and tree_view_column is the
    column.

    This is necessary because sorting is a PITA with Custom models. 
    """
    def __init__ (self, treemod):
        self.mod = treemod

    def set_sort_column_id (self, tree_column, model_column):
        """Replace the built-in tree_column method with magic."""
        #tree_column.set_sort_column_id(model_column)
        tree_column.connect('clicked',self.sort_by_column_callback,model_column)
                                 
    def sort_by_column_callback (self,tree_column,model_column):
        toggle_to = self.mod.toggle_sort(model_column)
        if toggle_to==None:
            tree_column.set_sort_indicator(False)
        else:
            tree_column.set_sort_indicator(True)
            tree_column.set_sort_order(toggle_to)
        # stop propagation... (?)
        return True

class PageableViewStore (PageableListStore):

    __gsignals__ = {
        'view-changed':(gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         ()
                         ),
        'view-sort':(gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_PYOBJECT,
                     (gobject.TYPE_PYOBJECT,)
                     ),
        }

    def __init__ (self, view, columns=['foo','bar'],column_types=[int,str],per_page=15,
                  length=None
                  ):
        self.__sorts__ = []
        self.__length__ = length
        PageableListStore.__init__(self,column_types, parent_args=[view],parent_kwargs={'columns':columns},
                                   per_page=per_page)

    def _setup_parent_ (self, view, columns=[]):
        self.parent_list = self.view = view
        self.unsorted_parent = self.unsorted_view = self.view
        self.columns = columns

    def _get_slice_ (self,bottom,top):
        return [[getattr(r,col) for col in self.columns] for r in self.view[bottom:top]]

    def _get_length_ (self):
        if self.__length__: return self.__length__
        else: return PageableListStore._get_length_(self)

    def sort (self, col, direction):
        attr = self.columns[col]
        self.sort_dict[col]=direction
        # Remove previous sorts by this attribute
        if (attr,-1) in self.__sorts__: self.__sorts__.remove((attr,-1))
        elif (attr, 1) in self.__sorts__: self.__sorts__.remove((attr,1))
        if direction==self.FORWARD:
            #self.__sorts__ = [(attr,1)] + self.__sorts__
            self.__sorts__.append((attr,1))
        elif direction==self.REVERSE:
            #self.__sorts__ = [(attr,-1)] + self.__sorts__
            self.__sorts__.append((attr,-1))
        self.emit('view-sort',self.__sorts__)

    #def _do_sort_ (self):
    #    if self.__all_sorts__:
    #        self.do_change_view(self.view.sortrev([getattr(self.view,a) for a in self.__all_sorts__],
    #                                              [getattr(self.view,a) for a in self.__reverse_sorts__])
    #                            )
    #    else:
    #        self.do_change_view(self.unsorted_view)

    def do_change_view (self, vw, length=None):
        self.parent_list = self.view = vw
        self.__length__ = None
        self.update_tree()
        self.emit('view-changed')

    def change_view (self, vw, length=None):
        self.do_change_view(vw,length=length)
        # Don't change the page anymore... it screws up a lot of
        # things... if we want to change the page during a search for
        # "usability", then we should do this from higher up so we can
        # have more fine-grained control of when it happens. 
        # if self.page != 0:
        #     self.page = 0
        #     self.emit('page-changed')

if __name__ == '__main__':
    pts=PageableTreeStore([str,str],parent_args=[[str(n),str(30-n)] for n in range(30)])
    #for n in range(30): pts.append(None,[str(n),str(n)])
    cssu = ColumnSortSetterUpper(pts)
    tv=gtk.TreeView()
    renderer = gtk.CellRendererText()
    tvc=gtk.TreeViewColumn('first',renderer,text=0)
    cssu.set_sort_column_id(tvc,0)
    tv.append_column(tvc)
    tvc2=gtk.TreeViewColumn('first',renderer,text=1)
    cssu.set_sort_column_id(tvc2,1)    
    tv.append_column(tvc2)
    tv.set_model(pts)
    sw = gtk.ScrolledWindow()
    sw.add(tv)
    vb = gtk.VBox()
    w = gtk.Window()
    w.add(vb)
    vb.add(sw)

    # add buttons
    b=gtk.Button('next page')
    def nxt ():
        #tv.set_model(None)
        pts.next_page()
        #tv.set_model(pts)
    def prv ():
        pts.prev_page()
    b.connect('clicked',lambda *args: nxt())
    vb.pack_start(b,False)
    pb = gtk.Button('prev')
    pb.connect('clicked',lambda *args: prv())
    vb.pack_start(pb,False)

    
    w.show_all()
    w.connect('delete-event',lambda *args: gtk.main_quit())
    gtk.main()
    
