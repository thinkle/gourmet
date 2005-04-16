import gtk, gobject
from gdebug import debug

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
                c.set_direction(gtk.DIR_UP)
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
            if self.last_timeout: gobject.source_remove(self.last_timeout)
            self.last_timeout=gobject.timeout_add(self.typeahead_timeout, self.reset_str)

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
    entry = cbe.get_children()[0]
    cbe.entry = entry  # for convenience/backward compatability with gtk.Combo
    make_completion(entry, model, col)

def make_completion (entry, model, col=0):
    """Setup completion for an entry based on model."""
    completion = gtk.EntryCompletion()
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
    model = gtk.ListStore(str)
    for l in list:
        model.append([l])
    cb.set_model(model)
    if type(cb) == gtk.ComboBoxEntry:
        cb.set_text_column(0)        
        setup_completion(cb)
    elif type(cb) == gtk.ComboBox:
        cb.clear()
        cell = gtk.CellRendererText()
        cb.pack_start(cell, expand=expand)
        cb.add_attribute(cell, 'text',0)
        setup_typeahead(cb, 0)

if __name__ == '__main__':
    w = gtk.Window()
    vb = gtk.VBox()    
    hbox = gtk.HBox()
    label = gtk.Label()
    label.set_text_with_mnemonic('Enter a _fruit: ')
    cbe = gtk.ComboBoxEntry()
    label.set_mnemonic_widget(cbe)
    set_model_from_list(cbe, ['Apples','Oranges','Grapes','Mango',
                              'Papaya','Plantain','Kiwi','Cherry',
                              'Bananas'])
    hbox.add(label)
    hbox.add(cbe)    
    label2 = gtk.Label()
    label2.set_text_with_mnemonic('Mode of _Transportation')
    cb = gtk.ComboBox()
    
    label2.set_mnemonic_widget(cb)
    set_model_from_list(cb, ['Planes','Trains','Automobiles','Spacecraft','Bicycles'])
    setup_typeahead(cb)
    hb2 = gtk.HBox()
    hb2.add(label2)
    hb2.add(cb)
    hb2.show_all()
    vb.add(gtk.Label("""Here's an EntryCompletion widget automatically
    in sync with the ComboBoxEntry widget. Hitting return will select
    the first item in the EntryCompletion popup window."""))
    vb.add(hbox)
    vb.add(gtk.Label("""Here's a ComboBox widget. With the widget selected,
    you can type e.g. "a" to select "airplane." Once the cb-popup window
    is up, however, typing doesn't do anything (doh!)"""))
    vb.add(hb2)
    vb.show_all()
    w.add(vb)
    w.show_all()
    w.connect('destroy',lambda *args: gtk.main_quit())
    gtk.main()
    
    
