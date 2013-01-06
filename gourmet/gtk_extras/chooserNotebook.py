import gtk

class ChooserNotebook:

    def __init__ (self, treeview, notebook):
        self.treeview = treeview
        self.notebook = notebook
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.connect('switch-page',self.page_changed_cb)
        self.setup_tree()
        self.page_changed_cb(self.notebook,None,self.notebook.get_current_page())
        
    def get_tab_labels (self):
        return [self.notebook.get_tab_label(c).get_text() for c in self.notebook.get_children()]

    def make_model (self):
        ls = gtk.ListStore(int,str)
        for n,l in enumerate(self.get_tab_labels()):
            ls.append((n,l))
        return ls

    def setup_tree (self):
        self.treeview.set_model(self.make_model())
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn('',rend,text=1)
        col.set_resizable(False)
        self.treeview.append_column(col)
        self.treeview.get_selection().set_mode(gtk.SELECTION_BROWSE)
        self.treeview.get_selection().connect('changed',
                                              self.selection_changed_cb
                                              )
        self.treeview.set_headers_visible(False)
        self.treeview.set_search_column(1)

    # Callbacks
    def selection_changed_cb (self, ts):
        mod,itr = ts.get_selected()
        if itr:
            n = mod.get_value(itr,0)
            self.notebook.set_current_page(n)

    def page_changed_cb (self, notebook, page, page_num):
        self.treeview.get_selection().select_path((page_num,))
    
def chooserify_notebook (nb):
    """Make a notebook into a cool chooser-style notebook.

    We can take a notebook in glade and change it -- we put the
    notebook into an HBox with a treeview as necessary, reparenting
    etc. This makes it convenient to use the ChooserNotebook from a
    glade file without having to use a custom widget.
    """
    parent = nb.parent
    packing = parent.query_child_packing(nb)
    # Set position to position of our child...
    for position,c in enumerate(parent.get_children()):
        if c==nb: break
    parent.remove(nb)
    hb = gtk.HBox()
    parent.add(hb)
    parent.set_child_packing(hb,*packing)
    parent.reorder_child(hb,position)
    tv = gtk.TreeView()
    hb.pack_start(tv,expand=False,fill=False)
    hb.pack_start(nb,expand=True,fill=True)
    tv.show()
    cn = ChooserNotebook(tv,nb)
    hb.show()
    return hb,cn
        
if __name__ == '__main__':
    from gourmet import gglobals

    import os.path

    def make_sample_notebook ():
        nb = gtk.Notebook()
        for txt in ['Foo','Bar','Baz']:
            l = gtk.Label((txt+' ')*10)
            l.set_selectable(True)
            nb.append_page(l,gtk.Label(txt))
        tv = gtk.TreeView()
        hb = gtk.HBox()
        hb.add(tv)
        hb.add(nb)
        tv.show(); nb.show_all()
        cn = ChooserNotebook(tv,nb)
        w = gtk.Window()
        w.add(hb)
        hb.show()
        w.show()
        w.connect('delete-event',lambda *args: gtk.main_quit())
        gtk.main()

    def do_glade_funkiness (gladefile=os.path.join(gglobals.uibase,'recCardDisplay.ui'),
                            nb_widget='notebook1'):
        gf = gtk.Builder()
        gf.add_from_file(gladefile)
        nb = gf.get_object(nb_widget)
        chooserify_notebook(nb)
        window = nb.parent
        while not isinstance(window,gtk.Window):
            window = window.parent
        window.show()
        window.connect('delete-event',lambda *args: gtk.main_quit())
        gtk.main()
    
    #make_sample_notebook()
    do_glade_funkiness()

    
