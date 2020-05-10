from gi.repository import Gtk
from gi.repository import GObject
from gourmet.gdebug import debug

class FocusFixer:
    key = None
    def __init__ (self,cbe):
        children = cbe.get_children()
        self.e = children[0] if children else cbe
        self.e.connect('key-press-event',self.keypress_event_cb)
        self.e.connect('focus-out-event',self.focus_out_cb)
        self.e.connect('focus-in-event',self.focus_in_cb)
        cbe.connect('focus-in-event',self.focus_in_cb)

    def focus_in_cb (self, widget, event):
        self.e.grab_focus()

    def focus_out_cb (self, widget, event):
        if not event.in_ and self.key in ['Tab']:
            parent = widget.get_parent()
            while parent and not isinstance(parent,Gtk.Window) :
                parent = parent.get_parent()
            for n in range(2): parent.emit('move-focus',Gtk.DIRECTION_LEFT)
            #parent.emit('move-focus',Gtk.DIRECTION_LEFT)

    def keypress_event_cb (self, w, event):
        self.key = Gdk.keyval_name(event.keyval)

def cb_get_active_text (combobox):
    """Get the selected/active text of combobox"""
    model = combobox.get_model()
    active = combobox.get_active()
    if active < 0:
        return None
    return model[active][0]

def cb_set_active_text (combobox, text, col=0):
    """Set the active text of combobox to text. We fail
    if the text is not already in the model. Column is the column
    of the model from which text is drawn."""
    model = combobox.get_model()
    n = 0
    for rw in model:
        if rw[col]==text:
            combobox.set_active(n)
            return n
        n += 1
    return None

class setup_typeahead:
    """We setup selection of ComboBox items when the ComboBox
    is selected."""
    def __init__ (self, cb, col=0):
        self.cb = cb
        # we try to connect to our children renderers...
        if self.cb.get_children():
            for c in cb.get_children():
                #c.set_direction(Gtk.DIR_UP)
                try:
                    c.connect('key_press_event',self.key_press_cb)
                except:
                    debug("couldn't connect key_press_event for %s"%c,1)
        self.col = col
        self.str = ""
        self.cb.connect('key_press_event',self.key_press_cb)
        self.typeahead_timeout = 1500
        self.last_timeout=None

    def key_press_cb (self, widget, event):
        newstr = event.string
        if not newstr: return
        self.str += newstr
        match=self.match_string_in_combo(self.str)
        if type(match) == type(0):
            self.cb.set_active(match)
        ## otherwise, perhaps they didn't mean to combine strings
        else:
            self.str = ""
            match=self.match_string_in_combo(newstr)
            if type(match) == type(0):
                self.cb.set_active(match)
                self.string = newstr
        if type(match)==type(0):
            if self.last_timeout: GObject.source_remove(self.last_timeout)
            self.last_timeout=GObject.timeout_add(self.typeahead_timeout, self.reset_str)

    def reset_str (self, *args):
        self.string = ""

    def match_string_in_combo (self, str):
        mod = self.cb.get_model()
        n = 0
        for r in mod:
            modstr = r[self.col]
            if modstr.lower().find(str.lower()) == 0:
                return n
            n += 1


def setup_completion (cbe, col=0):
    """Setup an EntryCompletion on a ComboBoxEntry based on the
    items in the ComboBox's model"""
    model = cbe.get_model()
    children = cbe.get_children()
    if children:
        entry = children[0]
        cbe.entry = entry  # for convenience/backward compatibility with Gtk.Combo
        make_completion(entry, model, col)

def make_completion (entry, model, col=0):
    """Setup completion for an entry based on model."""
    if not isinstance(entry,Gtk.Entry):
        import traceback
        if isinstance(entry.get_child(),Gtk.Entry):
            print('WARNING: make_completion() called with ',entry,'and model',model)
            entry = entry.get_child()
            traceback.print_stack(limit=3)
            print('Using its child, ',entry,'instead.')
        else:
            print('WARNING: ',entry,'is not a GTK Entry')
            traceback.print_stack(limit=3)
            return
    completion = Gtk.EntryCompletion()
    completion.set_model(model)
    completion.set_text_column(col)
    entry.set_completion(completion)

    def on_activate (*args):
        txt = entry.get_text().lower()
        completion = False
        for r in model:
            if r[0].lower().startswith(txt):
                if completion:
                    # if there are more than one
                    # possible completion, we do nothing
                    return True
                completion = r[0]
        if completion != txt:
            if completion: entry.set_text(completion)
            return True
    entry.connect('activate',on_activate)

def set_model_from_list (cb, list, expand=True):
    """Setup a ComboBox based on a list of strings."""
    model = Gtk.ListStore(str)
    for l in list:
        model.append([l])
    cb.set_model(model)
    if type(cb) == (Gtk.ComboBox,):
        cb.set_text_column(0)
        setup_completion(cb)
    elif type(cb) == Gtk.ComboBox:
        cb.clear()
        cell = Gtk.CellRendererText()
        # help(cb)
        #  |      pack_start(self, cell:Gtk.CellRenderer, expand:bool)
        cb.pack_start(cell, expand)
        cb.add_attribute(cell, 'text',0)
        setup_typeahead(cb, 0)

if __name__ == '__main__':
    w = Gtk.Window()
    vb = Gtk.VBox()
    #vb.add(Gtk.Button('Blank button'))
    #for n in range(10): vb.add(Gtk.Button('Other blank'))
    hbox = Gtk.HBox()
    label = Gtk.Label()
    label.set_text_with_mnemonic('Enter a _fruit: ')
    cbe = Gtk.ComboBoxEntry()
    FocusFixer(cbe)
    label.set_mnemonic_widget(cbe)
    set_model_from_list(cbe, ['Apples','Oranges','Grapes','Mango',
                              'Papaya','Plantain','Kiwi','Cherry',
                              'Bananas'])
    hbox.add(label)
    hbox.add(cbe)
    vb.add(Gtk.Label(label="""Here's an EntryCompletion widget automatically
    in sync with the ComboBoxEntry widget. Hitting return will select
    the first item in the EntryCompletion popup window."""))
    vb.add(hbox)
    def make_combo (expand=True):
        label2 = Gtk.Label()
        label2.set_text_with_mnemonic('Mode of _Transportation')
        cb = Gtk.ComboBox()
        label2.set_mnemonic_widget(cb)
        set_model_from_list(cb, ['Planes','Trains','Automobiles','Spacecraft','Bicycles'],
                            expand=expand)
        setup_typeahead(cb)
        hb2 = Gtk.HBox()
        hb2.add(label2)
        hb2.add(cb)
        hb2.show_all()
        return hb2
    vb.add(Gtk.Label("""Here's a ComboBox widget. With the widget selected,
    you can type e.g. "a" to select "airplane." Once the cb-popup window
    is up, however, typing doesn't do anything (doh!)"""))
    vb.add(make_combo())
    vb.add(Gtk.Label("""ComboBox, expand=False"""))
    vb.add(make_combo(expand=False))
    vb.show_all()
    w.add(vb)
    w.show_all()
    w.connect('destroy',lambda *args: Gtk.main_quit())
    Gtk.main()
