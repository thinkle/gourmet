#!/usr/bin/env python
import sys
import gtk, gtk.glade, gobject, pango
import re, os.path, fnmatch
import xml.sax.saxutils
from gettext import gettext as _
from gourmet import gglobals, gdebug
from gourmet import thumbnail



def get_custom_handler(unused_xml, proc, name, *unused_args):
    def takewhile(proc, l):
        ret = []
        while l and proc(l[0]):
            ret.append(l[0])
            l.remove(l[0])
        return ret

    def parse_proc(proc):
        parts = proc.split('.')
        assert len(parts) > 1
        modparts = takewhile(str.isalnum, parts)
        assert modparts and parts
        return '.'.join(modparts), '.'.join(parts)

    module, code = parse_proc(proc)
    try:
        __import__(module)
    except Exception, e:
        raise RuntimeError('Failed to load module %s: %s' % (module, e))

    try:
        w = eval(code, sys.modules[module].__dict__)
    except Exception, e:
        raise RuntimeError('Failed call %s in module %s: %s'
                           % (code, module, e))
    w.set_name(name)
    w.show()
    return w
    
gtk.glade.set_custom_handler(get_custom_handler)

###############################################################################
# SIMPLE GLADE DIALOG
###############################################################################
class GladeDialog(gobject.GObject):
    glade_file = None
    glade_typedict = None

    dialog = None

    def __init__(self, parent=None):
        gobject.GObject.__init__(self)
        try:
            assert self.glade_file
            filepath = os.path.join(gglobals.gladebase, self.glade_file)
            if self.glade_typedict:
                wtree = gtk.glade.XML(filepath, typedict=self.glade_typedict, domain='gourmet')
            else:
                wtree = gtk.glade.XML(filepath, domain='gourmet')
        except RuntimeError, e:
            raise RuntimeError('Failed to load file %s from directory %s: %s'
                               % (self.glade_file, self.glade_dir, e))

        self.widgets = {}
        for widget in wtree.get_widget_prefix(''):
            wname = widget.get_name()
            if isinstance(widget, gtk.Window):
                assert self.dialog == None
                self.dialog = widget
                continue

            if wname in self.widgets:
                raise AssertionError("Two objects with same name (%s): %r %r"
                                     % (wname, self.widgets[wname], widget))
            self.widgets[wname] = widget

        if parent:
            self.window.set_transient_for(parent)

        wtree.signal_autoconnect(self)

        self.show = self.dialog.show
        self.hide = self.dialog.hide
        self.present = self.dialog.present
        self.run = self.dialog.run

    def destroy(self):
        self.dialog.destroy()
        del self.dialog
        

H_PADDING=12
Y_PADDING=12

class UserCancelledError (Exception):
    pass

def is_markup (s):
    try:
        pango.parse_markup(s,u'0')
        return True
    except:
        return False

class ModalDialog (gtk.Dialog):
    def __init__ (self, default=None, title="", okay=True, label=False, sublabel=False, parent=None, cancel=True, modal=True, expander=None):
        """Our basic class. We allow for a label. Possibly an expander
        with extra information, and a simple Okay button.  The
        expander is only a fancy option. It should be a list ['Name
        of expander', CONTENTS]. CONTENTS can be a string (to be put
        in a label), a widget (to be packed in the expander), or a
        list of strings and widgets to be packed in order."""
        self.widget_that_grabs_focus = None
        self.setup_dialog(title=title, parent=parent)
        self.connect('destroy',self.cancelcb)
        self.set_border_width(15)
        self.default = default
        self.ret = default
        self.responses = {gtk.RESPONSE_OK:self.okcb,
                          gtk.RESPONSE_CANCEL:self.cancelcb,
                          gtk.RESPONSE_NONE:self.cancelcb,
                          gtk.RESPONSE_CLOSE:self.cancelcb,
                          gtk.RESPONSE_DELETE_EVENT:self.cancelcb}
        if modal: self.set_modal(True)
        else: self.set_modal(False)        
        if label:
            self.setup_label(label)
        if sublabel:
            self.setup_sublabel(sublabel)
        if expander:
            # if we have an expander, our window
            # should be resizable (just in case
            # the user wants to do more resizing)
            self.set_resizable(True)
            self.setup_expander(expander)
        self.setup_buttons(cancel, okay)
        self.vbox.show_all()

    def setup_dialog (self, *args, **kwargs):
        gtk.Dialog.__init__(self, *args, **kwargs)

    def setup_label (self, label):
        # we're going to add pango markup to our
        # label to make it bigger as per GNOME HIG
        self.set_title(label)
        label = '<span weight="bold" size="larger">%s</span>'%label
        self.label = gtk.Label(label)
        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.vbox.pack_start(self.label,expand=False)
        self.label.set_padding(H_PADDING,Y_PADDING)
        self.label.set_alignment(0,0)
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        self.label.set_use_markup(True)
        self.label.show()
        
    def setup_sublabel (self,sublabel):
        self.sublabel = gtk.Label(sublabel)
        self.sublabel.set_selectable(True)
        self.vbox.pack_start(self.sublabel, expand=False)
        self.sublabel.set_padding(H_PADDING,Y_PADDING)
        self.sublabel.set_alignment(0,0)
        self.sublabel.set_justify(gtk.JUSTIFY_LEFT)
        self.sublabel.set_use_markup(True)
        self.sublabel.set_line_wrap(gtk.WRAP_WORD)
        self.sublabel.show()

    def setup_buttons (self, cancel, okay):
        if cancel:
            self.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        if okay:
            self.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
        self.connect('response',self.response_cb)

    def response_cb (self, dialog, response, *params):
        #print 'response CB ',dialog,response,params
        if self.responses.has_key(response):
            #print 'we have a response!'
            self.responses[response]()
        else:
            print 'WARNING, no response for ',response
            
    def setup_expander (self, expander):
            label=expander[0]
            body = expander[1]
            self.expander = gtk.Expander(label)
            self.expander.set_use_underline(True)
            self.expander_vbox = gtk.VBox()
            self.expander.add(self.expander_vbox)
            self._add_expander_item(body)
            self.expander.show()
            self.expander_vbox.show_all()
            self.vbox.add(self.expander)
            
    def _add_expander_item (self, item):
        if type(item)==type(""):
            l=gtk.Label(item)
            l.set_selectable(True)
            l.set_line_wrap(gtk.WRAP_WORD)
            self.expander_vbox.pack_start(l,
                                          expand=False,
                                          fill=False)
        elif type(item)==[] or type(item)==():
            map(self._add_expander_item,item)
        else:
            self.expander_vbox.pack_start(item)
            
    def run (self):
        self.show()
        if self.widget_that_grabs_focus: self.widget_that_grabs_focus.grab_focus()
        if self.modal: gtk.main()
        return self.ret

    def okcb (self, *args):
        self.hide()
        if self.modal: gtk.main_quit()

    def cancelcb (self, *args):
        self.hide()
        self.ret=None
        if self.modal: gtk.main_quit()

class MessageDialog (gtk.MessageDialog, ModalDialog):

    """A simple class for displaying messages to our users."""
    
    def __init__ (self, title="", default=None, okay=True, cancel=True, label=False, sublabel=False,
                  expander=None, message_type=gtk.MESSAGE_INFO, parent=None):
        self.message_type=message_type
        ModalDialog.__init__(self, title=title, default=default, okay=okay, cancel=cancel, label=label, sublabel=sublabel, parent=parent, expander=expander)

    def setup_dialog (self, *args, **kwargs):
        kwargs['type']=self.message_type
        if kwargs.has_key('title'):
            del kwargs['title']
        gtk.MessageDialog.__init__(self, *args, **kwargs)

    def setup_label (self, label):
        if not is_markup(label):
            label = xml.sax.saxutils.escape(label)
        label = '<span weight="bold" size="larger">%s</span>'%label
        self.set_markup(label)

    def setup_sublabel (self, sublabel):
        #curtext = self.label.get_text()
        #curtext += "\n%s"%sublabel
        #self.label.set_text(xml.sax.saxutils.escape(curtext))
        self.format_secondary_markup(sublabel)
        
def show_traceback (label="Error", sublabel=None):
    """Show an error dialog with a traceback viewable."""
    from StringIO import StringIO
    import traceback
    f = StringIO()
    traceback.print_exc(file=f)
    error_mess = f.getvalue()
    show_message(label=label,
                 sublabel=sublabel,
                 expander=(_("_Details"),error_mess),
                 message_type=gtk.MESSAGE_ERROR
                 )

def show_message (*args, **kwargs):
    """Show a message dialog.
    Args and Kwargs are handed to MessageDialog
    We most likely want to hand it label= and sublabel=
    """
    #if not kwargs.has_key(message_type):
    #    message_type=gtk.MESSAGE_INFO
    if not kwargs.has_key('cancel'):
        kwargs['cancel']=False
    d=MessageDialog(*args,**kwargs)
    d.run()
    return d



def select_file (title,
                 filename=None,
                 filters=[],
                 # filters are lists of a name, a list of mime types and a list of
                 # patterns ['Plain Text', ['text/plain'], '*txt']
                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                 set_filter=True,
                 select_multiple=False,
                 buttons=None
                 ):
    sfd=FileSelectorDialog(title,filename=filename,filters=filters,select_multiple=select_multiple,
                           action=action,set_filter=set_filter,buttons=buttons)
    return sfd.run()

def saveas_file (title,
                 filename=None,
                 filters=[],
                 action=gtk.FILE_CHOOSER_ACTION_SAVE,
                 set_filter=True,
                 buttons=None,
                 parent=None,
                 show_filetype=True):
    """Almost identical to select_file, except that we return a tuple containing
    the filename and the export type (the string the user selected)"""
    sfd=FileSelectorDialog(title,filename=filename,filters=filters,
                           action=action,set_filter=set_filter,buttons=buttons,
                           show_filetype=show_filetype,parent=parent)
    retval = sfd.run()
    if not retval:
        return None,None    
    exp_type = None
    base,ext = os.path.splitext(retval)
    while filters and not exp_type:
        name,mime,rgxps = filters.pop()
        for r in rgxps:
            if os.path.splitext(r)[1] == ext:
                exp_type = name
    return retval,exp_type

def select_image (title,
                  filename=None,
                  action=gtk.FILE_CHOOSER_ACTION_OPEN,
                  buttons=None):    
    sfd=ImageSelectorDialog(title,filename=filename,action=action,buttons=buttons)
    return sfd.run()

class FileSelectorDialog:
    """A dialog to ask the user for a file. We provide a few custom additions to the
    standard file dialog, including a special choose-filetype menu and including dynamic update
    of the filetype based on user input of an extension"""
    def __init__ (self,
                  title,
                  filename=None,
                  filters=[],
                  # filters are lists of a name, a list of mime types and a list of
                  # patterns ['Plain Text', ['text/plain'], '*txt']
                  action=gtk.FILE_CHOOSER_ACTION_SAVE,
                  set_filter=True,
                  buttons=None,
                  show_filetype=True,
                  parent=None,
                  select_multiple=False
                  ):
        self.parent=parent
        self.buttons=buttons
        self.multiple=select_multiple
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
        self.fsd = gtk.FileChooserDialog(self.title,
                                         action=self.action,
                                         parent=self.parent,
                                         buttons=self.buttons)
        self.fsd.set_default_response(gtk.RESPONSE_OK)
        self.fsd.set_select_multiple(self.multiple)
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
        if not self.filters:
            self.do_saveas = False
            return
        self.do_saveas = True
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
            mimetypes = mimetypes[0:] # copy the list so we don't mutilate it
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
        crp.set_property('xalign',0)
        self.saveas.pack_start(crp, expand=False)
        self.saveas.add_attribute(crp, 'pixbuf', 1)
        self.saveas.connect('changed', self.change_file_extension)
        crt = gtk.CellRendererText()
        self.saveas.pack_start(crt, expand=True)
        self.saveas.add_attribute(crt, 'text', 0)
        self.hbox = gtk.HBox()
        l=gtk.Label()
        l.set_use_markup(True)
        l.set_selectable(True)
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
        self.timeout = gobject.timeout_add(100, self.update_filetype_widget)
        
    def update_filetype_widget (self, *args):
        fn=self.fsd.get_filename()
        if self.fn != fn:
            self.fn = fn
            if not fn:
                return True
            ext=os.path.splitext(fn)[1]
            if self.ext_to_n.has_key(ext):
                self.internal_extension_change=True
                self.saveas.set_active(self.ext_to_n[ext])
                self.internal_extension_change=False
        return True

    def change_file_extension (self, *args):
        if self.internal_extension_change: return
        fn = os.path.split(self.fsd.get_filename())[1]
        # strip off the old extension if it was one of our
        # filetypes and now we're changing
        if self.is_extension_legal(fn):
            base = os.path.splitext(fn)[0]
        else:
            base = fn
        ext = self.n_to_ext[self.saveas.get_active()]
        if self.show_filetype:
            debug('changing file extension to %s'%(base + ext),3)
            self.fsd.set_current_name(base + ext)
        else:
            debug('changing file extension for %s to %s'%(base, ext))
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
        if not fn: return
        for e in self.extensions:
            if not e: e=""
            if fnmatch.fnmatch(fn, e):
                return True

    def run (self):
        """Run our dialog and return the filename or None"""
        response = self.fsd.run()
        if response == gtk.RESPONSE_OK:
            if self.multiple:
                fn = self.fsd.get_filenames()
            else:
                fn = self.fsd.get_filename()
            if not fn:
                show_message(label=_('No file selected'),
                             sublabel=_('No file was selected, so the action has been cancelled')
                             )
                return None
            if self.action==gtk.FILE_CHOOSER_ACTION_SAVE:
                # add the extension if need be...
                if self.do_saveas and not self.is_extension_legal(fn):
                    if self.n_to_ext.has_key(self.saveas.get_active()):
                        add_ext = self.n_to_ext[self.saveas.get_active()]
                        if add_ext: fn += add_ext
                # if we're saving, we warn the user before letting them save over something.
                # Note: we don't have to worry about multiple filenames since we're looking at ACTION_SAVE
                if os.path.exists(fn) and not getBoolean(
                    default=False,
                    label=_("A file named %s already exists.")%os.path.split(fn)[1],
                    sublabel=_("Do you want to replace it with the one you are saving?"),
                    parent=self.fsd,
                    cancel=False, # cancel==No in this case
                    custom_yes='_Replace',
                    custom_no=gtk.STOCK_CANCEL,
                    ):
                    return self.run()
            self.quit()
            return fn
        else:
            self.quit()
            return None

    def quit (self, *args):
        if hasattr(self,'timeout'):
            gobject.source_remove(self.timeout)
        self.fsd.destroy()
        
    
class ImageSelectorDialog (FileSelectorDialog):
    IMAGE_FILTERS = [
        ['Image',
         ['image/jpeg','image/png','image/tiff',
          'image/bmp','image/cgf',],
         ['*.jpeg','*.jpg','gif','bmp','png',
          '*.JPEG','*.JPG','GIF','BMP','PNG']
         ],
        ['Jpeg Image',['image/jpeg'],['*.jpeg','*.jpg','*.JPG','*.JPEG']],
        ['PNG Image',['image/png'],['*.png','*.PNG']],
        ['Bmp Image',['image/bmp'],['*.bmp','*.BMP']],
        ['CGF Image',['image/cgf'],['*.cgf','*.CFG']],
        ['Tiff Image',['image/tiff'],['*.tiff','*.TIFF']]
        ]

    def __init__ (self,
                  title,
                  filename=None,
                  filters=IMAGE_FILTERS,
                  action=gtk.FILE_CHOOSER_ACTION_OPEN,
                  set_filter=True,
                  buttons=None
                  ):
        FileSelectorDialog.__init__(self, title, filename, filters, action, set_filter, buttons)

    def post_dialog (self):
        self.preview = gtk.Image()
        self.fsd.set_preview_widget(self.preview)
        self.fsd.connect('selection-changed',self.update_preview)
        self.preview.show()

    def update_preview (self, *args):
        uri = self.fsd.get_uri()
        # first, let's look for a large thumbnail
        thumbpath = thumbnail.check_for_thumbnail(uri) #default size is large
        if thumbpath:
            self.preview.set_from_file(thumbpath)
            self.preview.show()
        else:
            self.preview.hide()

def getNumber (*args, **kwargs):
    """Run NumberDialog, passing along all args, waiting on input and passing along
    the results."""
    d = NumberDialog(*args, **kwargs)
    return d.run()
                     
def getEntry (*args, **kwargs):
    """Run EntryDialog, passing along all args, waiting on input and passing along
    the results."""    
    d = EntryDialog(*args, **kwargs)
    return d.run()

def getBoolean (*args,**kwargs):
    """Run BooleanDialog, passing along all args, waiting on input and
    passing along the results."""
    d = BooleanDialog(*args,**kwargs)
    retval = d.run()
    if retval==None:
        raise UserCancelledError("getBoolean dialog cancelled!")
    else:
        return retval

def getOption (*args,**kwargs):
    d=OptionDialog(*args,**kwargs)
    return d.run()

def getRadio (*args,**kwargs):
    d=RadioDialog(*args,**kwargs)
    return d.run()

def get_ratings_conversion (*args,**kwargs):
    d=RatingsConversionDialog(*args,**kwargs)
    return d.run()

def show_amount_error (txt):
    """Show an error that explains how numeric amounts work."""
    de.show_message(label=_("""I'm sorry, I can't understand
the amount "%s".""")%txt,
                    sublabel=_("Amounts must be numbers (fractions or decimals), ranges of numbers, or blank."),
                    expander=[_("_Details"),
                              _("""
The "unit" must be in the "unit" field by itself.
For example, if you want to enter one and a half cups,
the amount field could contain "1.5" or "1 1/2". "cups"
should go in the separate "unit" field.

To enter a range of numbers, use a "-" to separate them.
For example, you could enter 2-4 or 1 1/2 - 3 1/2.
""")])


if __name__ == '__main__':
    w=gtk.Window()
    w.connect('delete_event',gtk.main_quit)
    b=gtk.Button("show dialog (modal)")
    opts=(["Toggle Option",True],
          ["String Option","Hello"],
          ["Integer Option",1],
          ["Float Option",float(3)],
          ["Option Option",("B",["A","B","C"])],
          )
    pd=PreferencesDialog(options=opts)
    def run_prefs (*args):
         pd.run()
    b.connect('clicked',run_prefs)
    def show_options (options):
        print options
    b2=gtk.Button("show dialog (not modal)")
    vb=gtk.VBox()
    def msg(*args):
        for a in args:
            print a
    char_measure = ""
    for n in range(10): char_measure="%s %s"%(char_measure,n)
    char_measure = char_measure * 50
    from ratingWidget import StarGenerator
    for s,f in [
        ['show dialog (modal)',run_prefs],
        ['show ratings dialog',lambda *args: get_ratings_conversion(['Good','Great','So so','Hot shit'],
                                                                    StarGenerator(),
                                                                    )],
        ['show dialog (not modal)',lambda *args: PreferencesDialog(options=opts,apply_func=show_options).show()],
        ['show FAQ',lambda *args: show_faq(jump_to='shopping')],
        ['show message',lambda *args: show_message('howdy',label='Hello there. This is a very long label for the top of a dialog.', sublabel='And this is a sub message.',message_type=gtk.MESSAGE_WARNING)],
        ['get entry', lambda *args: getEntry(label='Main label',sublabel='sublabel',entryLabel='Entry Label: ')],
        ['get number', lambda *args: getNumber(label='Main label',sublabel='sublabel')],        
        ['get long entry', lambda *args: getEntry(label='Main label', sublabel=char_measure, entryLabel='Entry Label: ',default_character_width=75,entryTip='Enter something long here.')],
        ['show boolean', lambda *args: getBoolean()],
        ['show custom boolean', lambda *args: getBoolean(custom_yes='_Replace',
                                                         custom_no=gtk.STOCK_CANCEL,
                                                         cancel=False
                                                         )],
        ['show radio dialog', lambda *args: getRadio(label='Main label',
                                                     sublabel='sublabel'*10,default=2,
                                                     options=[('First',1),
                                                              ('Second',2),
                                                              ('Third',3)]),],
        ['get image dialog',lambda *args: msg(select_image('Select Image'))],
        ['get file dialog',lambda *args: msg(select_file('Select File',
                                                     filters=[['Plain Text',['text/plain'],['*.txt','*.TXT']],
                                            ['PDF',['application/pdf'],['*.pdf','*.PDF']],
                                            ['Postscript',['application/postscript'],['*.ps','*.PS']],
                                            ['Web Page (HTML)',['text/html'],['*.htm','*.HTM','*.html','*.HTML']],
                                            ['Mealmaster File',['text/mmf'],['*.mmf','*.MMF']]],
                                                     select_multiple=True
                                                     )),
         ],
        ['save file with types',
         lambda *args: msg(saveas_file('export',filename='/tmp/test.mmf',
                                   filters=[['Plain Text',['text/plain'],['*.txt','*.TXT']],
                                            ['PDF',['application/pdf'],['*.pdf','*.PDF']],
                                            ['Postscript',['application/postscript'],['*.ps','*.PS']],
                                            ['Web Page (HTML)',['text/html'],['*.htm','*.HTM','*.html','*.HTML']],
                                            ['Mealmaster File',['text/mmf'],['*.mmf','*.MMF']]]))],
        ]:
        print b,f,s
        b = gtk.Button(s)
        def wrap (f):
            def _ (*args,**kwargs):
                print 'Doing ',f
                print 'f returns:',f()
                print 'Done'
            return _
        b.connect('clicked',wrap(f))
        vb.add(b)
    w.add(vb)
    vb.show_all()
    w.show_all()
    gtk.main()
    

