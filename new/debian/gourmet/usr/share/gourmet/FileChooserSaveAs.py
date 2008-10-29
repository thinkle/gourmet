import gtk, os.path, fnmatch

from gettext import gettext as _

class select_file_dialog:
    """We set up a file dialog.  If we are SAVEing and we have filters,
    we set up a nice ComboBox to let the user choose the filetype of the file,
    trying to immitate the functionality described here:
    http://www.gnome.org/~seth/designs/filechooser-spec/

    filename is an initial filename

    set_filter is whether to initially set the filter when opening a file

    buttons are a list of buttons and responses to add to the dialog. If these
    aren't provided, we'll provide sensible buttons depending on the action.

    filters are lists of a name for the filter that the user will see, a list of
    mime types the filter should include, and a list of patterns.  In the case of
    a save-as dialog, we will use the filters to set-up our choose-your-type dialog,
    giving the name as the string, choosing an icon based on the
    mime-type (if we can find one), and  using the first pattern to
    name our output file. NOTE: For this to work properly, the
    patterns must simply be *.extension (since we use the extension
    from the pattern directly).

    if show_filetype is True, we show the filename exactly as it is
    saved. If it is false, we hide the extension from the user.

    parent is the parent for our dialog.
    """
    def __init__ (self,
                  title,
                  filename=None,
                  filters=[],
                  # filters are lists of a name, a list of mime types and a list of
                  # patterns ['Plain Text', ['text/plain'], ['*.txt']
                  action=gtk.FILE_CHOOSER_ACTION_SAVE,
                  set_filter=True,
                  buttons=None,
                  show_filetype=True,
                  parent=None
                  ):
        self.parent=parent
        self.buttons=buttons
        self.set_filter=set_filter
        self.action=action
        self.filename=filename
        self.title=title
        self.filters=filters
        self.show_filetype=show_filetype
        self.setup_dialog()
        self.post_dialog()

    def post_dialog (self):
        """Run after the dialog is set up (to allow subclasses to do further setup)"""
        pass

    def setup_dialog (self):
        """Create our dialog"""
        self.setup_buttons()
        self.fsd = gtk.FileChooserDialog(self.title,action=self.action,parent=self.parent,buttons=self.buttons)
        self.fsd.set_default_response(gtk.RESPONSE_OK)
        if self.filename:
            path,name=os.path.split(os.path.expanduser(self.filename))
            if path: self.fsd.set_current_folder(path)
            if name: self.fsd.set_current_name(name)
        self.setup_filters()
        if self.action==gtk.FILE_CHOOSER_ACTION_SAVE:
            # a stupid hack until GNOME finally realizes the proper filechooser widget
            # described here: http://www.gnome.org/~seth/designs/filechooser-spec/
            self.setup_saveas_widget()

    def setup_buttons (self):
        """Set our self.buttons attribute"""
        if not self.buttons:
            if self.action==gtk.FILE_CHOOSER_ACTION_OPEN or self.action==gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER:
                self.buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
            else:
                self.buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK)
    
    def setup_filters (self):
        """Create and set filters for the dialog."""
        self.extensions = []
        for fil in self.filters:
            filter = gtk.FileFilter()
            filter_name, filter_mime_types, filter_patterns = fil
            filter.set_name(filter_name)
            if filter_mime_types:
                for f in filter_mime_types:
                    filter.add_mime_type(f)
            if filter_patterns:
                for f in filter_patterns:
                    filter.add_pattern(f)
                    self.extensions.append(f)
            self.fsd.add_filter(filter)
        if self.set_filter and self.filters:
            self.fsd.set_filter(self.fsd.list_filters()[0])

    def setup_saveas_widget (self):
        """We imitate the functionality we want GNOME to have not long
        from now and we provide a saveas widget."""
        self.saveas = gtk.ComboBox()
        # set up a ComboBox 
        self.it = gtk.icon_theme_get_default()
        ls=gtk.ListStore(str,gtk.gdk.Pixbuf)
        n = 0
        longest_word = 0
        self.ext_to_n = {}
        self.n_to_ext = {}
        for name,mimetypes,regexps in self.filters:
            if len(name) > longest_word:
                longest_word = len(name)
            image = None
            baseimage = None
            # we're going to turn this list around and pop off one
            # item at a time in order and see if we have a corresponding
            # icon.
            mimetypes = mimetypes[0:]
            mimetypes.reverse()
            while mimetypes and not image:
                mt = mimetypes.pop()
                if mt.find("/") > -1:
                    base,det=mt.split("/")
                else:
                    base = mt
                    det = ""
                image = self.find_mime_icon(base,det)
                if not image and not baseimage:
                    baseimage = self.find_mime_icon(base)
            # n_to_ext let's us grab the correct extension from our active iter
            self.n_to_ext[n]=os.path.splitext(regexps[0])[-1]
            for r in regexps:
                ext = os.path.splitext(r)[-1]
                # ext_to_n let's us select the correct iter from the extension typed in
                self.ext_to_n[ext]=n
            # for example, if there's no gnome-mime-text-plain, we'll settle for gnome-mime-text
            if not image: image=baseimage
            ls.append([name,image])
            n += 1
        self.saveas.set_model(ls)
        crp = gtk.CellRendererPixbuf()
        crp.set_property('xalign',0) #line up our pixbufs nicely
        self.saveas.pack_start(crp, expand=False)
        self.saveas.add_attribute(crp, 'pixbuf', 1)
        self.saveas.connect('changed', self.change_file_extension)
        crt = gtk.CellRendererText()
        self.saveas.pack_start(crt, expand=True)
        self.saveas.add_attribute(crt, 'text', 0)        
        self.hbox = gtk.HBox()
        l=gtk.Label()
        l.set_use_markup(True)
        l.set_text_with_mnemonic(_('Select File_type'))
        l.set_mnemonic_widget(self.saveas)
        self.hbox.add(l)
        self.hbox.add(self.saveas)
        self.hbox.show_all()
        self.fsd.set_extra_widget(self.hbox)
        self.fn = None
        self.fsd.connect('selection-changed',self.update_filetype_widget)
        self.internal_extension_change=False
        self.update_filetype_widget()
        # and now for a hack -- since we can't connect to the Entry widget,
        # we're going to simply check to see if the filename has changed with
        # an idle call.
        self.timeout = gtk.timeout_add(100, self.update_filetype_widget)
        
    def update_filetype_widget (self, *args):
        """Update the filetype widget based on the contents
        of the entry widget."""
        fn=self.fsd.get_filename()
        if self.fn != fn:
            self.fn = fn
            if not fn:
                return True
            ext=os.path.splitext(fn)[1]
            if self.ext_to_n.has_key(ext):
                self.saveas.set_active(self.ext_to_n[ext])
        return True

    def change_file_extension (self, *args):
        print 'changing extension'
        #if self.internal_extension_change: return
        fn = os.path.split(self.fsd.get_filename())[1]
        # strip off the old extension if it was one of our
        # filetypes and now we're changing
        if self.is_extension_legal(fn):
            base = os.path.splitext(fn)[0]
        else:
            base = fn
        ext = self.n_to_ext[self.saveas.get_active()]
        if self.show_filetype:
            self.fsd.set_current_name(base + ext)
        else:
            self.fsd.set_current_name(base)
            
    def find_mime_icon (self, base, ext=None, size=48):
        prefixes = ['gnome','gnome-mime']
        while prefixes:
            prefix = prefixes.pop()
            name = prefix + "-" + base
            if ext:
                name = name + "-" + ext
            if self.it.has_icon(name):
                return self.it.load_icon(name, size, gtk.ICON_LOOKUP_USE_BUILTIN)

    def is_extension_legal (self, fn):
        for e in self.extensions:
            if fnmatch.fnmatch(fn, e):
                return True

    def run (self):
        """Run our dialog and return the filename or None"""
        response = self.fsd.run()
        if response == gtk.RESPONSE_OK:
            fn = self.fsd.get_filename()            
            if self.action==gtk.FILE_CHOOSER_ACTION_SAVE:
                # add the extension if need be...
                if not self.is_extension_legal(fn):
                    fn += self.n_to_ext[self.saveas.get_active()]
                # if we're saving, we warn the user before letting them save over something.
                if os.path.exists(fn) and not getBoolean(
                    default=False,
                    label=_("A file named %s already exists.")%os.path.split(fn)[1],
                    sublabel=_("Do you want to replace it with the one you are saving?"),
                    parent=self.fsd,
                    cancel=False, # cancel==No in this case
                    custom_yes='_Replace',
                    custom_no={'stock':gtk.STOCK_CANCEL},
                    ):
                    return self.run()
            self.quit()
            return fn
        else:
            self.quit()
            return None

    def quit (self, *args):
        print 'removing timeout'
        if hasattr(self,'timeout'):
            gtk.timeout_remove(self.timeout)
        self.fsd.destroy()

def saveas_file (title,
                 filename=None,
                 filters=[],
                 action=gtk.FILE_CHOOSER_ACTION_SAVE,
                 set_filter=True,
                 buttons=None,
                 parent=None,
                 show_filetype=True):

    """Select a file and return a tuple containing
    the filename and the export type (the string the user selected)"""

    sfd=select_file_dialog(title,filename=filename,filters=filters,
                           action=action,set_filter=set_filter,buttons=buttons,
                           show_filetype=show_filetype,parent=parent)
    retval = sfd.run()
    if not retval:
        return None,None    
    exp_type = None
    base,ext = os.path.splitext(retval)
    filters = filters[0:] #we're about to destroy this list!
    while filters and not exp_type:
        name,mime,rgxps = filters.pop()
        for r in rgxps:
            if os.path.splitext(r)[1] == ext:
                exp_type = name
    return retval,exp_type

if __name__ == '__main__':
    w=gtk.Window()
    w.connect('delete_event',gtk.main_quit)
    vb = gtk.VBox()
    w.add(vb)
    def msg (args):
        for a in args: print a
    filters=[['Plain Text',['text/plain'],['*.txt']],
             ['PDF',['application/pdf'],['*.pdf']],
             ['Postscript',['application/postscript'],['*.ps']],
             ['Web Page (HTML)',['text/html'],['*.htm','*.html']],
             ['Jpeg Image',['image/jpeg'],['*.jpg','*.jpeg']],
             ]
    for s,f in [
        ['Save as (show extensions)', 
         lambda *args: msg(saveas_file('Save As...',filename='~/duck.pdf',
                                       filters=filters))
         ],
        ['Save as (hide extensions)',
         lambda *args: msg(saveas_file('Save As...',filename='~/duck.pdf',
                                       filters=filters, show_filetype=False))
         ]
        ]:
        b = gtk.Button(s)
        b.connect('clicked',f)
        vb.add(b)
    vb.show_all()
    w.show_all()
    gtk.main()
