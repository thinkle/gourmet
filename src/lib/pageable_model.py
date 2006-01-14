import gtk, gobject
from gettext import gettext as _

class RowRef:
    def __init__ (self, view, path):
        self.view = view
        if type(path)!=int:
            self.indx = path[0]
            self.path = path
        else:
            self.path = path
            self.indx = path
        self.get_view_row()

    def get_view_row (self): return self.view[self.indx]

class ViewTreeModel (gtk.GenericTreeModel):

    columns = 'foo','bar'
    column_types = int,str

    def __init__ (self, view):
        #print "__init__ (self, view):",self, view
        self.view = view
        gtk.GenericTreeModel.__init__(self)

    def get_row_ref (self, path):
        return RowRef(self.view,path)
    
    def on_get_flags(self):
        #print "on_get_flags(self):",self
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        #print "on_get_n_columns(self):",self
        return len(self.column_types)
    
    def on_get_column_type(self, index):
        #print "on_get_column_type(self, index):",self, index
        return self.column_types[index]
    
    def on_get_iter(self, path):
        #print "on_get_iter(self, path):",self, path
        try: return self.get_row_ref(path)
        except: return None
    
    def on_get_path(self, rowref):
        #print "on_get_path(self, rowref):",self, rowref
        return rowref.path
    
    def on_get_value(self, rowref, column):
        #print "on_get_value(self, rowref, column):",self, rowref, column
        #print 'getting value'
        try:
            return getattr(rowref.get_view_row(),self.columns[column])
        except:
            return None
    
    def on_iter_next(self, rowref):
        #print "on_iter_next(self, rowref):",self, rowref
        try:
            path = rowref.path
            try:
                path = (path[0]+1,)
            except:
                path += 1
            return self.get_row_ref(path)
        except:
            return None

    def on_iter_children(self, parent):
        #print "on_iter_children(self, parent):",self, parent
        if not parent and self.view: return self.get_row_ref(0)
        else: return None
    
    def on_iter_has_child(self, rowref):
        #print "on_iter_has_child(self, rowref):",self, rowref
        return False
    
    def on_iter_n_children(self, rowref):
        #print "on_iter_n_children(self, rowref):",self,rowref
        if rowref: return 0
        else: return len(self.view)
    
    def on_iter_nth_child(self, rowref, n):
        #print "on_iter_nth_child(self, rowref, n):",self,rowref,n
        if rowref: return None
        try:
            #print 'making row out of ',n
            return self.get_row_ref(n)
        except:
            #print 'failed!'
            return None
    
    def on_iter_parent(self, child):
        #print "on_iter_parent(self, child):",self,child
        return None

class PagedRowRef (RowRef):
    def __init__ (self, view, path, pvm):
        self.pvm = pvm
        RowRef.__init__(self,view,path)

    def get_view_row (self):
        converted_indx = self.indx + (self.pvm.per_page*self.pvm.page)
        return self.view[converted_indx]
    

class PageableViewTreeModel (ViewTreeModel, gobject.GObject):

    OFF = None
    FORWARD = gtk.SORT_ASCENDING
    REVERSE = gtk.SORT_DESCENDING
    
    page = 0    

    __gsignals__ = {
        'page-changed':(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE, #RETURN
                        () # PARAMS
                        ),
        'view-changed':(gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         ()
                         ),
        #'sort-changed':(gobject.SIGNAL_RUN_LAST,
        #                gobject.TYPE_PYOBJECT, # return a list
        #                [gobject.TYPE_PYOBJECT]),
        }
    
    def __init__ (self, view, per_page=15):
        self.per_page=int(per_page)
        ViewTreeModel.__init__(self,view)
        gobject.GObject.__init__(self)
        self.cur_length = len(self)
        self.unsorted_view = self.view
        self.__all_sorts__ = []
        self.__reverse_sorts__ = []
    
    def update_all (self):
        totn = len(self.view)
        start_at = self.page*self.per_page
        to_delete = [(n,) for n in range(self.cur_length)]
        # Delete backwards to keep paths straight
        to_delete.reverse()
        for pth in to_delete:
            #print 'deleting ',pth
            self.row_deleted(pth)
        self.cur_length = len(self)
        #print 'update_all - ',self.cur_length
        for pth in [(n,) for n in range(self.cur_length)]:
            try:
                itr = self.get_iter(pth)
            except ValueError:
                #print 'breaking!'
                break
            else:
                #print 'inserting',pth,itr
                self.row_inserted(pth,itr)
        return

    def get_row_ref (self, path):
        try:
            return PagedRowRef(self.view,path,self)
        except:
            return None

    def set_page (self, n):
        self.page = n
        self.update_all()
        self.emit('page-changed')
        
    def goto_first_page (self):
        if self.page!=0: self.set_page(0)

    def goto_last_page (self):
        last_page = self.last_page()
        if self.page != last_page:
            self.set_page(last_page)
    
    def next_page (self): 
        if (self.page+1)*self.per_page < len(self.view):
            self.set_page(self.page + 1)
            
    def prev_page (self):
        if self.page > 0: self.set_page(self.page - 1)

    def change_items_per_page (self, n):
        n = int(n)
        curpage = self.page
        currec = self.page * self.per_page
        self.per_page = n
        new_page = currec / self.per_page
        if new_page != curpage:
            self.set_page(new_page)
        else:
            self.update_all()
        

    def change_view (self, vw):
        self.unsorted_view = vw
        if self.__reverse_sorts__ or self.__all_sorts__ and vw:
            vw = vw.sortrev(
                [getattr(self.view,a) for a in self.__all_sorts__],
                [getattr(self.view,a) for a in self.__reverse_sorts__]
                )
        self.do_change_view(vw)
        pch = False
        if self.page != 0:
            self.page = 0
            pch=True
            self.emit('page-changed')        

    def do_change_view (self, vw):
        self.view = vw
        self.update_all()
        self.emit('view-changed')

    def add_search_term (self, term, direction):
        """Add search term.

        Counterintuitively, you can remove the term with direction=OFF
        """
        # First remove any previous search in either direction (if
        # it's the same direction, we'll be reprioritizing the search
        # to first)
        if term in self.__all_sorts__: self.__all_sorts__.remove(term)
        if direction == self.FORWARD or direction==self.REVERSE:
            self.__all_sorts__ = [term]+self.__all_sorts__
        if direction!=self.REVERSE and term in self.__reverse_sorts__:
            self.__reverse_sorts__.remove(term)
        elif direction==self.REVERSE and term not in self.__reverse_sorts__:
            self.__reverse_sorts__.append(term)

    def do_sort (self):
        #print 'sorting by ',self.__all_sorts__,self.__reverse_sorts__
        if not self.__all_sorts__:
            self.do_change_view(self.unsorted_view)
        self.do_change_view(self.view.sortrev([getattr(self.view,a) for a in self.__all_sorts__],
                          [getattr(self.view,a) for a in self.__reverse_sorts__])
                         )
        #self.emit('sort-changed',(self.__all_sorts__,self.__reverse_sorts__))

    def sort (self, term, direction=FORWARD):
        self.add_search_term(term,direction)
        self.do_sort()
        
    def sort_multiple (self, terms):
        """Sort by multiple terms, where each term is a tuple with
        (term, DIRECTION) and DIRECTION is FORWARD or REVERSE

        This will smash any prior record of searching.
        """
        for t,d in terms: self.add_search_term(t,d)
        self.do_sort()

    def toggle_sort (self, term, toggle_to=None):
        """Toggle sorting by a term

        We cycle through three positions: forward, backward, None,
        which is what standard gtk.TreeSort does as well!

        Return the direction we've toggled to
        """
        if toggle_to==None:
            if term not in self.__all_sorts__:
                toggle_to=self.FORWARD
            elif term in self.__reverse_sorts__:
                toggle_to=self.OFF
            else:
                toggle_to=self.REVERSE
        self.sort(term,toggle_to)
        return toggle_to

    def last_page (self):
        nrecs = len(self.view)
        pages = nrecs / self.per_page - 1
        if nrecs % self.per_page: pages+=1
        return pages

    def showing (self, short_format_string='%(top)s',
                 long_format_string='%(bottom)s to %(top)s of %(total)s'):
        bottom = self.page*self.per_page + 1
        top = self.page*self.per_page+len(self)
        total = len(self.view)
        return bottom,top,total,

    def on_get_iter (self, path):
        if path[0] > self.per_page:
            return None
        elif path[0] > len(self.view)+self.page*self.per_page:
            return None
        else: return self.get_row_ref(path)

    def on_iter_next (self, rowref):
        if rowref.indx >= self.per_page:
            return None
        else:
            try:
                path = rowref.path
                path = (path[0]+1,)
                return self.get_row_ref(path)
            except:
                return None

    def __len__ (self):
        return self.on_iter_n_children(None)

    def on_iter_n_children (self, rowref):
        totlen = len(self.view)
        if totlen < self.per_page:
            return totlen
        pages = totlen / self.per_page - 1
        last_page = totlen % self.per_page
        if last_page: pages += 1
        if self.page < pages:
            return self.per_page
        elif last_page:
            return last_page
        else: return self.per_page

    def iter_is_valid (self, itr):
        #print itr
        if itr.view==self.view: return True

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
        tree_column.set_clickable(True)
        tree_column.connect('clicked',self.sort_by_column_callback,model_column)
                                 
    def sort_by_column_callback (self,tree_column,model_column):
        attr = self.mod.columns[model_column]
        tog = self.mod.toggle_sort(attr)
        if tog==None:
            tree_column.set_sort_indicator(False)
        else:
            tree_column.set_sort_indicator(True)
            tree_column.set_sort_order(tog)

gobject.type_register(PageableViewTreeModel)

if __name__ == '__main__':
    import metakit
    # build and populate a database
    s=metakit.storage()
    vw = s.getas('duck[foo:i,bar:s]')
    vw2 = s.getas('goat[foo:i,bar:s]')
    words = """The quick red fox ran over the lazy brown dog who was taking oats away from some old horse catching another horse whan that aprille with the shorres soughte the drought of march had perced to the rote the tendre croppes and the yonge sonne hath in the ram his halve course he run""".split()
    import random
    for n in range(90):
        vw.append({'foo':n,'bar':'%s'%random.choice(words)})
        vw2.append({'foo':2**(n/20),'bar':'f'*n})
    #print 'view has ',len(vw)
    vwm=PageableViewTreeModel(vw)
    tv=gtk.TreeView()
    renderer = gtk.CellRendererText()
    cssu=ColumnSortSetterUpper(vwm)
    tvc=gtk.TreeViewColumn('first',renderer,text=0)
    cssu.set_sort_column_id(tvc,0)
    tv.append_column(tvc)
    tvc2=gtk.TreeViewColumn('first',renderer,text=1)
    cssu.set_sort_column_id(tvc2,1)
    tv.append_column(tvc2)
    tv.set_model(vwm)
    #print 'model has ',len(vwm)
    sw = gtk.ScrolledWindow()
    sw.add(tv)
    vb = gtk.VBox()
    w = gtk.Window()
    w.add(vb)
    vb.add(sw)
    b=gtk.Button('next page')
    def nxt ():
        #tv.set_model(None)
        vwm.next_page()
        #tv.set_model(vwm)
        #print "%s-%s of %s"%vwm.showing()
    def prv ():
        vwm.prev_page()
        #print "%s-%s of %s"%vwm.showing()
    b.connect('clicked',lambda *args: nxt())
    vb.pack_start(b,False)
    pb = gtk.Button('prev')
    pb.connect('clicked',lambda *args: prv())
    vb.pack_start(pb,False)
    cb = gtk.Button('change view')
    vb.pack_start(cb,False)
    n = 0
    def chg ():
        if n==0:
            vwm.change_view(vw2)
            n=1
        else:
            vwm.change_view(vw)
            n=0
    cb.connect('clicked', lambda *args: chg())
    w.show_all()
    w.connect('delete-event',lambda *args: gtk.mainquit())
    gtk.main()
