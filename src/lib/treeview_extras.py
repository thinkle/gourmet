#!/usr/bin/python2.3
from gdebug import *
import gtk

def path_next (path, inc=1):
    """Return the path NEXT rows after PATH. Next can be negative, in
    which case we get previous paths."""
    next=list(path[0:-1])
    last=path[-1]
    last += inc
    if last < 0:
        last=0
    next.append(last)
    next=tuple(next)
    return next

def get_unique_iter_from_value (mod, col, val):
    for r in mod:
        if r[col]==val: return r.iter
        for rc in r.iterchildren():
            if rc[col]==val: return rc.iter

def move_iter (mod, iter, sibling=None, parent=None, direction="before"):
    """move_iter will move iter relative to sibling or
    parent. Direction (before or after) tells us whether to
    insert_before or insert_after (with a sib) or to prepend or append
    (with a parent)."""
    if direction != "after":
        direction = "before"
    path = mod.get_path(iter)
    if sibling:
        dpath = mod.get_path(sibling)
    elif parent:
        dpath = mod.get_path(parent)
    else:
        dpath = ()
    rowdata = get_row(mod, iter)
    children=harvest_children(mod, iter)
    def insert_new (parent):
        """A little subroutine to insert our row. We'll call this at the appropriate
        time depending on the order of source and destination iters"""
        if not parent:
            parent=None
            if len(dpath) > 1:
                parent=mod.get_iter(dpath[0:-1])
        if parent==sibling or not sibling:
            """If our parent is our destination iter or if we have
            only a parent specified, we're moving inside, not before"""
            if direction=="before":
                return mod.append(parent, rowdata)
            else:
                return mod.prepend(parent, rowdata)
        elif direction=="before":
                return mod.insert_before(parent,sibling,rowdata)
        else:
            return mod.insert_after(parent,sibling,rowdata)
    # if the source is before the destination, we add then remove. otherwise, we remove then add.
    path_last = path_compare(path,dpath)
    if path_last:
        remove_children(mod, iter)
        mod.remove(iter)
        new=insert_new(parent)
        insert_children(mod, new, children)
    elif path_last==0: debug("Moving into my self is nonsensical!",1)
    else:
        new=insert_new(parent)
        insert_children(mod, new, children)
        mod.remove(iter)
        remove_children(mod, iter)

def insert_children (mod, iter, children):
    for row in children:
        mod.append(iter, row)

def remove_children (mod, iter):
    # in spite of its name, children gets the first child
    child = mod.iter_children(iter)
    while child:
        mod.remove(child)
        child = mod.iter_children(iter)        

def harvest_children (mod, iter):
    ret = []
    n = 0
    child = mod.iter_nth_child(iter, n)
    while child:
        ret.append(get_row(mod, child))
        n += 1
        child = mod.iter_nth_child(iter, n)
    return ret
            
def path_compare (p1, p2):
    """Return 1 if p1 > p2, 0 if p1 = p2 and -1 if p1 < p2
    Greater than means comes after."""
    flag = True
    retval = None
    n = 0
    while flag:
        if len(p1)>n and len(p2)>n:
            if p1[n] > p2[n]:
                retval=1
                flag=False
            elif p1[n] < p2[n]:
                retval=-1
                flag=False
            else: flag=True
        elif len(p1)<=n and len(p2)<=n:
            ## if we're both too short, we're done comparing and we're equal
            retval=0
            flag=False
        else:
            ## otherwise one of these is greater (the longer path comes after/is greater than the shorter)
            if len(p1) > len(p2):
                retval=1
                flag=False
            else:
                retval=-1
                flag=False
        n += 1
    return retval
        
def get_row (mod, iter):
        """Grab all values in iter and return as a list suitable for
        feeding to 'row' argument of append/prepend/insert"""
        n = 0
        flag = True
        row = []
        while flag:
            try:
                row.append(mod.get_value(iter,n))
            except:
                flag=False
            n += 1
        return row

class selectionSaver:
    """A class to save selections in a treeStore. This is implemented because it is too damned
    hard to follow iters when potentially moving around multiple items. It will only work if
    one column of data in the treeIter is a unique identifier. This happens to be true of all
    of my treeViews. To use this class, initilialize it before moving things around. Then call
    'restore_selections' to fix up your selections."""

    def __init__ (self, treeview, unique_column=0):
        """unique_column is the column with unique data (used to identify selections). treeview
        is the treeview in question"""
        self.tv = treeview
        self.uc = unique_column
        self.model=self.tv.get_model()
        self.selection=self.tv.get_selection()
        self.save_selections()
        
    def save_selections (self):
        self.selected = []
        self.expanded = {}
        self.selection.selected_foreach(self._add_to_selected)

    def _add_to_selected (self, model, path, iter):
        self.add_selection(iter)
        
    def add_selection (self, iter):
        """Add iter to list of selected items"""
        v = self.model.get_value(iter,self.uc)
        self.selected.append(v)
        self.expanded[v] = self.tv.row_expanded(self.model.get_path(iter))

    def rem_selection (self, iter):
        """Remove iter from list of selected items. Silently do nothing if
        handed an iter that wasn't selected in the first place."""
        try:
            selected.remove(self.model.get_value(iter,self.uc))
        except ValueError:
            pass

    def restore_selections (self, tv=None):
        """Restore selections. We can optionally do the unlikely task of
        restoring selections to a new treeView. This might come in handy
        w/ dragndrop within an application between treeViews. Otherwise,
        we remember and use the treeView we were initially handed."""
        if tv:
            self.tv=tv
            self.model=self.tv.get_model()
            self.selection=self.tv.get_selection()
        else:
            self.model = self.tv.get_model()
            self.selection = self.tv.get_selection()
        self.selection.unselect_all()
        iter = self.model.get_iter_first()
        new_paths=[]
        while iter:
            v = self.model.get_value(iter,self.uc)
            if self.selected.__contains__(v):
                self.selection.select_iter(iter)
                if self.expanded.get(v,None):
                    self.tv.expand_row(self.model.get_path(iter),True)
                new_paths.append(self.model.get_path(iter))
            child = self.model.iter_children(iter)            
            if child:
                iter = child
            else:
                next = self.model.iter_next(iter)
                if next:
                    iter = next
                else:
                    parent = self.model.iter_parent(iter)
                    if parent:
                        iter = self.model.iter_next(parent)
                    else:
                        iter = None
        #    #if iter: print 'walking...',self.model.get_path(iter)
        #    
        #if new_paths:
        #    self.tv.scroll_to_cell(new_paths[0])
        #if len(new_paths) > 1:
        #    # we try to get all cells visible if possible... if not,
        #    # we leave the last cell in view
        #    self.tv.scroll_to_cell(new_paths[-1])
            
class TreeViewConf:
    """Handed a treeView and two configuration items, this class allows
    us to save user changes made to a treeView. Whoever calls us is responsible
    for saving our self.hidden and self.order at the appropriate times and handing
    them back to us when needed. Note: this will break if column titles aren't unique."""
    def __init__ (self, tv, hidden=[], order={}):
        self.tv=tv
        self.order=order
        self.hidden=hidden
        self.tv.connect("columns-changed",self.save_column_change_cb)
        
    def apply_visibility (self):
        for c in self.tv.get_columns():
            t=c.get_title()
            if t in self.hidden: c.set_visible(False)
            else:
                # and try with "_" removed
                l=list(t)
                if '_' in l: l.remove('_')
                t="".join(l)
                if t in self.hidden: c.set_visible(False)
                else: c.set_visible(True)

    def apply_column_order (self):
        coldic = {}
        for c in self.tv.get_columns():
            try:
                coldic[self.order[c.get_title()]]=c
            except:
                debug("I don't know about column titled %s"%c.get_title(),3)
        prevcol=None
        for n in range(len(self.tv.get_columns())):
            if coldic.has_key(n):
                c=coldic[n]
                self.tv.move_column_after(c,prevcol)
                prevcol=c
            else:
                debug("There is no column in position %s"%n,4)

    def save_column_change_cb (self,tv):
        self.order = {}
        n=0
        for c in tv.get_columns():
            titl=c.get_title()
            self.order[titl]=n
            n += 1

class QuickTree (gtk.ScrolledWindow):
    def __init__ (self, rows, titles=None):
        
        """Handed a list of data, we create a simple treeview.  The
        rules are simple. Each row can be a LIST in which case it is
        taken to be a list of columns (and each LIST is assumed to be
        the same length). Alternatively, each row can be an item, in
        which case there is only one column. All items must produce a
        string with str(item)."""
        debug('QuickTree got rows: %s'%rows,0)
        gtk.ScrolledWindow.__init__(self)
        self.tv=gtk.TreeView()
        self.rows = rows
        self.titles=titles
        if self.rows:
            first = self.rows[0]
            if type(first) != type(()) and type(first) != type([]):
                debug('Mappifying!',0)
                self.rows=map(lambda x: [x],self.rows)
            self.setup_columns()
            self.setup_model()
        self.add(self.tv)
        self.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.show_all()


    def setup_columns (self):
        self.cols=len(self.rows[0])
        if not self.titles:
            self.titles = [None] * self.cols
        rend=gtk.CellRendererText()
        for n in range(self.cols):
            debug('Adding column: %s'%self.titles[n],0)
            col = gtk.TreeViewColumn(self.titles[n],rend,text=n)
            col.set_resizable(True)
            col.set_reorderable(n)
            col.set_sort_column_id(n)
            self.tv.append_column(col)

    def setup_model (self):
        self.model = apply(gtk.ListStore,[str]*self.cols)
        for row in self.rows:
            iter = self.model.append()
            while len(row) > self.cols:
                row.pop()
            while len(row) < self.cols:
                row.append("")
            self.model[iter]=map(lambda i: str(i),row)
        self.tv.set_model(self.model)
            
            
if __name__ == '__main__':
    vb = gtk.VBox()
    sw = QuickTree(
        ['Foo','Bar'],
        ['Bar','Foo']
        )
    sw.tv.set_reorderable(True)
    sw.tv.ss = selectionSaver(sw.tv,0)
    def ss_save (*args):
        sw.tv.ss.save_selections()
    def ss_get (*args):
        sw.tv.ss.restore_selections()
    sw.tv.connect('drag-begin',ss_save)
    sw.tv.connect('drag-end',ss_get)
    w = gtk.Window()
    w.add(sw)
    w.show_all()
    gtk.main()
