import gtk, gtk.glade

class FauxDruid (gtk.Dialog):
    """A GTK-only implentation of GNOME Druid.

    We rely on a glade file in which individual windows have been set
    up as individual pages of a glade file using numbers to enumerate
    pages.  We also need "forward", "back", and "apply" buttons in the
    glade file readymade.
    """

    def __init__ (self, *args, **kwargs):
        gtk.Dialog.__init__(self,*args,**kwargs)
        self.pages = []
        self.vbox.pack_start(gtk.Label('Druid'),expand=False,fill=False)
        self.setup_action_area()
        self.show_all()

    def setup_action_area (self):
        for b,stock in [('backward',gtk.STOCK_GO_BACK),
                  ('forward',gtk.STOCK_GO_FORWARD),
                  ('apply',gtk.STOCK_APPLY),]:
            setattr(self,b,gtk.Button(stock=stock)) #e.g. self.forward = gtk.Button(...), etc.
            self.action_area.add(getattr(self,b))
        self.forward.connect('clicked',self.go_forward)
        self.backward.connect('clicked',self.go_backward)
        self.apply.connect('clicked',self.do_apply)

    def do_apply (self, *args): pass

    def display (self,*args):
        self.show_all()
        self.present()
    
    def go_forward (self, *args):
        self.set_page(self.current_page+1)

    def go_backward (self, *args):
        self.set_page(self.current_page-1)

    def set_button_sensitivities (self):
        """Set sensitivity of forward/backward/apply appropriately"""
        if self.current_page == 0: self.backward.set_sensitive(False)
        else: self.backward.set_sensitive(True)
        if self.current_page >= len(self.pages)-1: self.forward.set_sensitive(False)
        else: self.forward.set_sensitive(True)
        if self.current_page == len(self.pages)-1: self.apply.set_sensitive(True)
        else: self.apply.set_sensitive(False)

    def append_page (self, page_widget):
        """Add a page to our page list."""
        if isinstance(page_widget,gtk.Window):
            page_widget=page_widget.get_child()
        self.pages.append(page_widget)
        if len(self.pages)==1:
            self.set_page(0)
        
    def prepend_page (self, page_widget, n=0):
        """Add a page to the front of our page list.
        If n != 0, then we add the page before N rather than to the beginning.

        In other words, if we have pages [0,1,2,3,4,5] and run
        prepend_page(page_widget,2)
        we will end up with pages [0,1,new_page,2,3,4,5]
        """
        if not n: self.pages = [page_widget] + self.pages
        else:
            self.pages = self.pages[0:n] + [page_widget] + self.pages[n:]

    def set_page (self,n):
        new_page = self.pages[n]
        if hasattr(self,'current_page_widget'):
            self.vbox.remove(self.current_page_widget)
        #new_page.unparent()
        new_page.reparent(self.vbox)
        self.vbox.add(new_page)
        new_page.show()
        self.vbox.show()
        self.current_page_widget = new_page
        self.current_page = n
        self.set_button_sensitivities()
        self.vbox.show_all()

class FauxGladeDruid (FauxDruid):
    """A GTK-only Druid that grabs pages from a GLADE file."""
    def __init__ (self,
                  glade_file,
                  page_widget_base_name="page",
                  dialog_kwargs={}):
        FauxDruid.__init__(self,**dialog_kwargs)
        self.glade = gtk.glade.XML(glade_file)
        n = 1
        widg = self.glade.get_widget('%s%s'%(page_widget_base_name,n))
        while widg:
            self.append_page(widg)
            print 'Appended page'
            n += 1
            widg = self.glade.get_widget('%s%s'%(page_widget_base_name,n))
    


if __name__ == '__main__':
    #fd=FauxDruid()
    #for l in range(10):
    #    vb_false = gtk.VBox()
    #    p = gtk.Label('Page %s. '%l * l)
    #    vb_false.add(p)
    #    fd.append_page(p)
    #fd.set_page(0)
    #fd.display()
    #gtk.main()
    glf = '/home/tom/Projects/grm-0.8/glade/htmlImporterDruid.glade'
    fd = FauxGladeDruid(glf)
    fd.set_page(0)
    fd.display()
    gtk.main()

