#!/usr/bin/env python
import gtk, os.path, optionTable, thumbnail, cb_extras, fnmatch
import gglobals
from gettext import gettext as _
from gdebug import debug
H_PADDING=12
Y_PADDING=12

class mDialog (gtk.Dialog):
    def __init__ (self, default=None, title="", okay=True, label=False, sublabel=False, parent=None, cancel=True, modal=True, expander=None):
        """Our basic class. We allow for a label. Possibly an expander
        with extra information, and a simple Okay button.  The
        expander is are only fancy option. It should be a list ['Name
        of expander', CONTENTS]. CONTENTS can be a string (to be put
        in a label), a widget (to be packed in the expander), or a
        list of strings and widgets to be packed in order."""
        self.setup_dialog(title=title, parent=parent)
        self.connect('destroy',self.cancelcb)
        self.set_border_width(15)
        self.default = default
        self.ret = default
        if modal: self.set_modal(gtk.TRUE)
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
        if cancel or okay:
            self.setup_buttons(cancel, okay)
        self.vbox.show_all()

    def setup_dialog (self, *args, **kwargs):
        gtk.Dialog.__init__(self, *args, **kwargs)

    def setup_label (self, label):
        # we're going to add pango markup to our
        # label to make it bigger as per GNOME HIG
        label = '<span weight="bold" size="larger">%s</span>'%label
        self.label = gtk.Label(label)
        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.vbox.pack_start(self.label,expand=False)
        self.label.set_padding(H_PADDING,Y_PADDING)
        self.label.set_use_markup(True)
        self.label.show()
        
    def setup_sublabel (self,sublabel):
        self.sublabel = gtk.Label(sublabel)
        self.sublabel.set_selectable(True)
        self.vbox.pack_start(self.sublabel, expand=False)
        self.sublabel.set_padding(H_PADDING,Y_PADDING)
        self.sublabel.set_use_markup(True)
        self.sublabel.set_line_wrap(True)
        self.sublabel.show()

    def setup_buttons (self, cancel, okay):
        if okay:
            self.ok = gtk.Button(stock=gtk.STOCK_OK)
            self.action_area.pack_end(self.ok)        
            self.ok.show()
            self.ok.connect('clicked',self.okcb)
            self.ok.grab_focus()
        if cancel:
            self.cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
            self.action_area.pack_end(self.cancel)
            self.cancel.show()
            self.cancel.connect('clicked',self.cancelcb)            
            
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
            l.set_line_wrap(True)
            self.expander_vbox.pack_start(l,
                                          expand=False,
                                          fill=False)
        elif type(item)==[] or type(item)==():
            map(self._add_expander_item,item)
        else:
            self.expander_vbox.pack_start(item)
            
    def run (self):
        self.show()
        if self.modal: gtk.mainloop()
        return self.ret

    def okcb (self, *args):
        self.hide()
        if self.modal: gtk.mainquit()

    def cancelcb (self, *args):
        self.hide()
        self.ret=None
        if self.modal: gtk.mainquit()

class messageDialog (gtk.MessageDialog, mDialog):
    def __init__ (self, title="", default=None, okay=True, cancel=True, label=False, sublabel=False,
                  expander=None, message_type=gtk.MESSAGE_INFO, parent=None):
        self.message_type=message_type
        mDialog.__init__(self, title=title, default=default, okay=okay, cancel=cancel, label=label, sublabel=sublabel, parent=parent, expander=expander)

    def setup_dialog (self, *args, **kwargs):
        kwargs['type']=self.message_type
        if kwargs.has_key('title'):
            del kwargs['title']
        gtk.MessageDialog.__init__(self, *args, **kwargs)

    def setup_label (self, label):
        label = '<span weight="bold" size="larger">%s</span>'%label
        self.label.set_text(label)
        self.label.set_use_markup(True)

    def setup_sublabl (self, sublabel):
        curtext = self.label.get_text()
        curtext += "\n%s"%sublabel
        self.label.set_text(curtext)
                  
class numberDialog (mDialog):
    def __init__(self,default=None,label=False,sublabel=False,step_incr=1,page_incr=10,digits=0,
                 min=0,max=10000, parent=None):
        mDialog.__init__(self,default=default, parent=parent)
        self.hbox=gtk.HBox()
        self.vbox.add(self.hbox)
        #self.spinButton=gtk.SpinButton(climb_rate=climb_rate,digits=digits)
        if not default:
            val = 0
        else:
            val = float(default)
        self.adjustment=gtk.Adjustment(val,
                                       lower=min,
                                       upper=max,
                                       step_incr=step_incr,
                                       page_incr=page_incr)
        self.spinButton=gtk.SpinButton(self.adjustment)
        if default:
            self.spinButton.set_value(default)
        if label:
            self.label=gtk.Label(label)
            self.label.set_selectable(True)
            self.label.set_line_wrap(True)
            self.label.set_padding(H_PADDING, Y_PADDING)
            self.hbox.add(self.label)
            self.label.show()
        self.hbox.add(self.spinButton)
        self.spinButton.get_adjustment().connect("value_changed",self.update_value)
        self.spinButton.show()
        self.hbox.show()                
        
    def update_value (self, *args):
        self.ret=self.spinButton.get_value()

class entryDialog (mDialog):
    def __init__ (self, default=None, label=None, sublabel=None, entryLabel=False, parent=None, visibility=True):
        mDialog.__init__(self,default=default,parent=parent, label=label, sublabel=sublabel)
        self.hbox=gtk.HBox()
        self.vbox.add(self.hbox)        
        if entryLabel:
            self.label=gtk.Label(entryLabel)
            self.label.set_line_wrap(True)
            self.label.set_selectable(True)
            self.hbox.add(self.label)
            self.label.show()
            self.label.set_padding(H_PADDING,Y_PADDING)
        self.entry = gtk.Entry()
        self.entry.set_visibility(visibility)
        self.hbox.add(self.entry)
        self.hbox.show()
        if default:
            self.entry.set_text(default)
        self.entry.connect("changed",self.update_value)
        self.entry.show()

    def update_value (self, *args):
        self.ret = self.entry.get_text()

class optionDialog (mDialog):
    def __init__ (self, default=None, label="Select Option", sublabel=None, options=[], parent=None, expander=None, cancel=True):
        """Options can be a simple option or can be a tuple or a list
        where the first item is the label and the second the value"""
        mDialog.__init__(self, okay=True, label=label, sublabel=sublabel, parent=parent, expander=expander, cancel=cancel)
        self.menucb = self.get_option        
        self.optdic={}
        self.menu = gtk.Menu()
        # set the default value to the first item
        first = options[0]
        if type(first)==type(""): self.ret=first
        else: self.ret=first[1]
        for o in options:
            if type(o)==type(""):
                l=o
                v=o
            else:
                l=o[0]
                v=o[1]
            i = gtk.MenuItem(l)
            i.connect('activate',self.menucb)
            i.show()
            self.optdic[i]=v
            self.menu.append(i)
        self.optionMenu=gtk.OptionMenu()
        self.vbox.add(self.optionMenu)
        self.optionMenu.set_menu(self.menu)
        self.optionMenu.show()
        self.menu.show()


    def get_option (self, widget):
        self.ret=self.optdic[widget]
        #return self.ret

    def set_value (self, value):
        self.ret=value

class progressDialog (mDialog):
    def __init__ (self, title="", okay=True, label=False, sublabel=False, parent=None,
                  cancel=False, stop=True, pause=True,modal=False):
        """stop,cancel,and pause will be given as callbacks to their prospective buttons."""
        self.custom_pausecb=pause
        self.custom_cancelcb=cancel
        self.custom_stopcb=stop
        mDialog.__init__(self, title, okay=okay, label=label, sublabel=sublabel, parent=parent,
                         cancel=cancel,modal=modal)
        self.set_title(label)
        self.progress_bar = gtk.ProgressBar()
        self.vbox.add(self.progress_bar)
        self.detail_label = gtk.Label()
        self.vbox.add(self.detail_label)
        self.detail_label.set_use_markup(True)
        self.detail_label.set_padding(H_PADDING,Y_PADDING)
        self.detail_label.set_line_wrap(True)
        self.vbox.show_all()
        if okay: self.ok.set_sensitive(False) # we're false by default!
        
    def setup_buttons (self, cancel, okay):                
        if self.custom_pausecb:
            self.pause = gtk.ToggleButton(_('_Pause'),True)
            self.pause.connect('toggled',self.custom_pausecb)
            self.action_area.pack_end(self.pause)
        if self.custom_stopcb:
            self.stop = gtk.ToggleButton(_('_Stop'),True)
            self.stop.connect('clicked',self.custom_stopcb)
            self.stop.connect('clicked',self.cancelcb)
            self.action_area.pack_end(self.stop)
        mDialog.setup_buttons(self,cancel,okay)
        if self.custom_cancelcb:
            self.cancel.connect('clicked',self.custom_cancelcb)            
    
        
class preferences_dialog (mDialog):
    def __init__ (self, options=([None,None]), option_label="Option",
                  value_label="Value", default=True, label=None,
                  apply_func=None, parent=None, dont_ask_cb=None,
                  dont_ask_custom_text=None):
        """Options is a tuple of lists where each list is ['option', VALUE], handed to OptionTable
        
        VALUE can be any of the following:
        a string (will be editable)
        a number (will be editable and returned as a number)
        true or false (will be a checkbox)

        If apply_func is True, we will have an apply button, which
        will hand the option tuple as its argument. Otherwise, okay will simply
        return the list on okay."""
        if apply_func: modal=False
        else: modal=True
        self.apply_func = apply_func
        self.options = options        
        mDialog.__init__(self, okay=True, label=label, parent=parent, modal=modal)
        self.table = optionTable.OptionTable(options=self.options,
                                             option_label=option_label,
                                             value_label=value_label,
                                             changedcb=self.changedcb)        
        self.vbox.add(self.table)
        if dont_ask_cb:
            if not dont_ask_custom_text:
                dont_ask_custom_text=_("Don't ask me this again.")
            self.dont_ask = gtk.CheckButton(dont_ask_custom_text)
            self.dont_ask.connect('toggled',dont_ask_cb)
            self.vbox.add(self.dont_ask)
        self.vbox.show_all()

    def setup_buttons (self, cancel, okay):
        if self.apply_func:
            self.revert = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
            self.revert.connect('clicked',self.revertcb)
            self.action_area.add(self.revert)
            self.apply = gtk.Button(stock=gtk.STOCK_APPLY)
            self.apply.set_sensitive(gtk.FALSE)
            self.apply.connect('clicked',self.applycb)
            self.action_area.add(self.apply)
            self.apply.show()
            self.changedcb = lambda *args: self.apply.set_sensitive(gtk.TRUE)
        else:
            self.changedcb=None
            self.set_modal(gtk.FALSE)
        mDialog.setup_buttons(self, cancel, okay)

    def revertcb (self, *args):
        self.table.revert()
        
    def applycb (self, *args):
        self.table.apply()
        self.apply_func(self.table.options)
        self.apply.set_sensitive(gtk.FALSE)

    def run (self):
        self.show()
        if self.apply_func:
            return
        else:
            gtk.mainloop()
            return self.ret
        
    def okcb (self, *args):
        if self.apply_func:
            if self.apply.get_property('sensitive'):
                # if there are unsaved changes...
                if getBoolean(label="Would you like to apply the changes you've made?"):
                    self.applycb()
            self.hide()
        else:
            self.table.apply()
            self.ret = self.table.options
            self.hide()
            gtk.main_quit()
                   
    def cancelcb (self, value):
        self.hide()
        self.ret=None
        
        
class booleanDialog (messageDialog):
    def __init__ (self, title="", default=True, label=_("Do you really want to do this"),
                  sublabel=False, cancel=True,
                  parent=None, custom_yes=None, custom_no=None, expander=None,
                  dont_ask_cb=None, dont_ask_custom_text=None,
                  cancel_returns=None, message_type=gtk.MESSAGE_QUESTION
                  ):
        """Setup a booleanDialog which returns True or False.
        parent is our parent window.
        custom_yes is custom text for the button that returns true or a dictionary
                   to be handed to gtk.Button as keyword args.
        custom_no is custom text for the button that returns False or a dictionary
                   to be handed to gtk.Button as keyword args
        expander is a list whose first item is a label and second is a widget to be packed
        into an expander widget with more information.
        if dont_ask_variable is set, a Don't ask me again check
        button will be displayed which the user can check to avoid this kind
        of question again. (NOTE: if dont_ask_variable==None, this won't work!)
        dont_ask_custom_text is custom don't ask text."""
        self.cancel_returns = cancel_returns
        messageDialog.__init__(self,title=title,okay=False,label=label, cancel=cancel, sublabel=sublabel,parent=parent, expander=expander, message_type=message_type)
        if custom_no:
            if type(custom_no)==type("") or type(custom_no)==type(unicode):
                self.no = gtk.Button(custom_no)
            else:
                self.no = gtk.Button(**custom_no)
        else: self.no = gtk.Button(stock=gtk.STOCK_NO)
        if custom_yes:
            if type(custom_yes)==type("") or type(custom_yes)==type(unicode):
                self.yes = gtk.Button(custom_yes)
            else:
                self.yes = gtk.Button(**custom_yes)                
        else: self.yes = gtk.Button(stock=gtk.STOCK_YES)
        if dont_ask_cb:
            if not dont_ask_custom_text:
                dont_ask_custom_text=_("Don't ask me this again.")
            self.dont_ask = gtk.CheckButton(dont_ask_custom_text)            
            self.dont_ask.connect('toggled',dont_ask_cb)
            self.vbox.add(self.dont_ask)
            self.dont_ask.show()
        self.action_area.add(self.no)
        self.action_area.add(self.yes)
        self.yes.connect('clicked',self.yescb)
        self.no.connect('clicked',self.nocb)
        self.action_area.show_all()

    def yescb (self, *args):
        self.ret=True
        self.okcb()

    def cancelcb (self, *args):
        if self.cancel_returns != None:
            self.ret = self.cancel_returns
            self.okcb()

    def nocb (self, *args):
        self.ret=False
        self.okcb()


def show_message (*args, **kwargs):
    #if not kwargs.has_key(message_type):
    #    message_type=gtk.MESSAGE_INFO
    if not kwargs.has_key('cancel'):
        kwargs['cancel']=False
    d=messageDialog(*args,**kwargs)
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
    sfd=select_file_dialog(title,filename=filename,filters=filters,select_multiple=select_multiple,
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
    sfd=select_file_dialog(title,filename=filename,filters=filters,
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
    sfd=select_image_dialog(title,filename=filename,action=action,buttons=buttons)
    return sfd.run()

class select_file_dialog:
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
        self.fsd = gtk.FileChooserDialog(self.title,action=self.action,parent=self.parent,buttons=self.buttons)
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
        self.timeout = gtk.timeout_add(100, self.update_filetype_widget)
        
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
                    custom_no={'stock':gtk.STOCK_CANCEL},
                    ):
                    return self.run()
            self.quit()
            return fn
        else:
            self.quit()
            return None

    def quit (self, *args):
        if hasattr(self,'timeout'):
            gtk.timeout_remove(self.timeout)
        self.fsd.destroy()
        
    
class select_image_dialog (select_file_dialog):
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
        select_file_dialog.__init__(self, title, filename, filters, action, set_filter, buttons)

    def post_dialog (self):
        self.preview = gtk.Image()
        self.fsd.set_preview_widget(self.preview)
        self.fsd.connect('selection-changed',self.update_preview)
        self.preview.show()

    def update_preview (self, *args):
        uri = self.fsd.get_uri()
        # first, let's look for a large thumbnail
        thumbpath = thumbnail.check_for_thumbnail(uri)
        # next we try for a normal sized thumbnail
        if thumbpath:
            self.preview.set_from_file(thumbpath)
            self.preview.show()
        else:
            self.preview.hide()

def getNumber (*args, **kwargs):
    """Run numberDialog, passing along all args, waiting on input and passing along
    the results."""
    d = numberDialog(*args, **kwargs)
    return d.run()
                     
def getEntry (*args, **kwargs):
    """Run entryDialog, passing along all args, waiting on input and passing along
    the results."""    
    d = entryDialog(*args, **kwargs)
    return d.run()

def getBoolean (*args,**kwargs):
    """Run booleanDialog, passing along all args, waiting on input and
    passing along the results."""
    d = booleanDialog(*args,**kwargs)
    retval = d.run()
    if retval==None:
        raise "getBoolean dialog cancelled!"
    else:
        return retval

def getOption (*args,**kwargs):
    d=optionDialog(*args,**kwargs)
    return d.run()

if __name__ == '__main__':
    w=gtk.Window()
    w.connect('delete_event',gtk.main_quit)
    b=gtk.Button("show dialog (modal)")
    opts=(["Toggle Option",True],
          ["String Option","Hello"],
          ["Integer Option",1],
          ["Float Option",float(3)])
    pd=preferences_dialog(options=opts)
    def run_prefs (*args):
        print pd.run()
    b.connect('clicked',run_prefs)
    def show_options (options):
        print options
    b2=gtk.Button("show dialog (not modal)")
    vb=gtk.VBox()
    def msg(*args):
        for a in args:
            print a
    for s,f in [
        ['show dialog (modal)',run_prefs],
        ['show dialog (not modal)',lambda *args: preferences_dialog(options=opts,apply_func=show_options).show()],
        ['show message',lambda *args: show_message('howdy',label='Hello there. This is a very long label for the top of a dialog.', sublabel='And this is a sub message.',message_type=gtk.MESSAGE_WARNING)],
        ['show boolean', lambda *args: getBoolean()],
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
        b = gtk.Button(s)
        b.connect('clicked',f)
        vb.add(b)
    w.add(vb)
    vb.show_all()
    w.show_all()
    gtk.main()
    

