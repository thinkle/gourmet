import gtk.glade, gtk

class MnemonicManager:

    sacred_cows = ['okay','cancel','close']

    def __init__ (self):
        self.mnemonics = {}
        self.sub_managers = {}
        self.notebook_managers = {}
        self.untouchable_accels = []
        self.untouchable_widgs = []

    def get_submanager (self, w):
        p = w.parent
        while p:
            if self.sub_managers.has_key(p):
                return self.sub_managers[p]
            p = p.parent
        return self

    def add_glade (self, glade=None, glade_file=None):
        """Add all mnemonic widgets in glade object.

        We can be passed a gladefile or a glade object.
        Realistically, though, you'll want to pass the object and keep
        a reference around to use. The file option's really just for
        testing :)
        """
        added = []
        if not glade:
            glade=gtk.glade.XML(glade_file)
        widgets=glade.get_widget_prefix('') # get all widgets
        # Check if there are more than one window, in which case we
        # each window gets its own sub_handler
        windows = filter(lambda w: isinstance(w,gtk.Window),widgets)
        if len(windows)>0:
            for w in windows:
                self.sub_managers[w]=MnemonicManager()
        # handle menu items
        menu_items = filter(lambda x: isinstance(x,gtk.MenuItem),widgets)
        for mi in menu_items:
            widgets.remove(mi)
            children =  mi.get_children()
            if children and isinstance(children[0],gtk.Label):
                lab = children[0]
            else:
                continue
            if isinstance(mi.parent,gtk.MenuBar):
                added.append(lab)
                self.get_submanager(mi.parent).add_widget_mnemonic(lab,untouchable=True)
            # otherwise, we create a sub-instance of ourselves to
            # handle submenus, etc.
            else:
                if not self.sub_managers.has_key(mi.parent):
                    self.sub_managers[mi.parent]=MnemonicManager()
                added.append(lab)
                self.sub_managers[mi.parent].add_widget_mnemonic(lab)
        # handle other mnemonic labels we have
        has_keyval = filter(lambda x: (hasattr(x,'get_mnemonic_keyval')
                                       and
                                       gtk.gdk.keyval_name(x.get_mnemonic_keyval())!='VoidSymbol'),
                            widgets)
        more_mnemonics = []
        for w in widgets:
            mm = w.list_mnemonic_labels()
            more_mnemonics.extend(mm)
        for l in more_mnemonics:
            if l not in has_keyval and l not in added: has_keyval.append(l)
        for w in has_keyval:
            # Are we in a notebook?
            nb = None
            p = w.parent
            added_to_sub = False
            while p:
                if isinstance(p.parent,gtk.Notebook):
                    break
                elif self.sub_managers.has_key(p.parent):
                    self.sub_managers[p.parent].add_widget_mnemonic(w)
                    added_to_sub = True
                    break
                else:
                    p=p.parent
            if added_to_sub: continue
            if p and isinstance(p.parent,gtk.Notebook):
                nb = p.parent
                page = nb.page_num(p)
                if not self.notebook_managers.has_key(nb):
                    self.notebook_managers[nb]={}
                if not self.notebook_managers[nb].has_key(page):
                    self.notebook_managers[nb][page]=MnemonicManager()
                self.notebook_managers[nb][page].add_widget_mnemonic(w)
            else:
                if isinstance(w.parent,gtk.Notebook):
                    # make notebook tab labels (should be our only
                    # direct descendant labels) untouchable.
                    self.add_widget_mnemonic(w,untouchable=True,fix_untouchables=True)
                else:
                    self.add_widget_mnemonic(w)
        more_mnemonics = []

    def add_treeview (self, tv):
        for c in tv.get_columns():
            t = c.get_title()
            if t.find('_')>-1:
                widg = gtk.Label(t)
                widg.set_use_underline(True)
                c.set_widget(widg)
                widg.show()
                self.add_widget_mnemonic(widg)

    def add_widget_mnemonic (self, w, untouchable=False, fix_untouchables=False): 
        k = gtk.gdk.keyval_name(w.get_mnemonic_keyval())
        if w.get_text().lower().replace('_','') in self.sacred_cows:
            untouchable = True; fix_untouchables=False
        if untouchable:
            if k in self.untouchable_accels and fix_untouchables:
                # we have a conflict among untouchables to fix...
                alts = self.find_alternatives(w)
                if alts:
                    k = alts[0]
                    self.change_mnemonic(w,k)
            self.untouchable_accels.append(k)
            self.untouchable_widgs.append(w)
        if self.mnemonics.has_key(k):
            if not w in self.mnemonics[k]:
                self.mnemonics[k].append(w)
        else:
            self.mnemonics[k]=[w]

    def generate_new_mnemonic (self, text):
        for c in text:
            if not self.mnemonics.has_key(c.lower()):
                self.mnemonics[c.lower()]=[text]
                n = text.find(c)
                return text[0:n]+'_'+text[n:]
        # default to first character if there's no conflict-free
        # mnemonic available
        self.mnemonics[text[0].lower()].append(text)
        return '_'+text

    def find_alternatives (self, w, filter_untouchables = True):
        text = w.get_text()
        if not text: return []
        cur_ind = text.find('_')+1
        alts = [text[cur_ind].lower()]
        # Now we go through and find first letters of words...
        if cur_ind == 1: ind=2
        else: ind = 0
        ind = text.find(' ',ind)
        last_letter_that_could_be_word_start = len(text)-2
        while -1 < ind <= last_letter_that_could_be_word_start:
            alt = text[ind+1].lower()
            if alt not in alts: alts.append(alt)
            ind = text.find(' ',ind+1)
        for l in list(text):
            if l.lower() not in alts:
                if l in list(' (),_[]:;,.!{}/=+'): continue
                else: alts.append(l.lower())
        if filter_untouchables:
            alts = filter(lambda l: l not in self.untouchable_accels, alts)
        return alts

    def find_peaceful_alternatives (self, w):
        return filter(lambda l: not self.mnemonics.has_key(l),self.find_alternatives(w))
    
    def fix_conflicts_peacefully (self, do_submenus=True):
        to_reconcile = []
        changed = []
        for k,v in self.mnemonics.items():
            if len(v)>1:
                can_move = []
                for w in v:
                    if w in self.untouchable_widgs:
                        continue
                    if k in self.untouchable_accels:
                        alts = self.find_alternatives(w)
                    else:
                        alts = self.find_peaceful_alternatives(w)
                    if alts:
                        can_move.append((w,alts))
                if len(can_move)==len(v):
                    # If everything is movable, then we keep our first
                    # AccelLabel guy as it was and move the rest.
                    can_move.sort(self.sort_movables)
                    can_move=can_move[1:]
                # We extend our guys to move with to_move
                for w,alts in can_move:
                    self.change_mnemonic(w,alts[0])
                    changed.append(w)
        if changed:
            self.fix_conflicts_peacefully()
        if do_submenus:
            for mm in self.sub_managers.values():
                mm.fix_conflicts_peacefully()
        # for each of our notebooks
        for nb in self.notebook_managers.values():
            # for each of our pages
            for pagemanager in nb.values():
                self.merge_notebook(pagemanager).fix_conflicts_peacefully()

    def merge_notebook (self, mm):
        """Add our own items to a notebook page manager as untouchables.

        In other words, the notebook's manager will know to avoid
        other widgets in the containing context, but won't touch us.
        """
        new_mm = mm
        for ww in self.mnemonics.values():
            for w in ww:
                new_mm.add_widget_mnemonic(w,untouchable=True)
        for ww in mm.mnemonics.values():
            for w in ww:
                new_mm.add_widget_mnemonic(w)
        return new_mm

    def sort_movables (self, moveable1, moveable2):
        widg,alts = moveable1
        widg2,alts2 = moveable2
        al1 = isinstance(widg,gtk.AccelLabel)
        al2 = isinstance(widg2,gtk.AccelLabel)
        if al1 and not al2: return 1
        elif al2 and not al1: return -1
        else: return 0

    def get_all_possibilities (self):
        pass

    def change_mnemonic (self, widget, new_mnemonic):
        txt=widget.get_text()
        old = gtk.gdk.keyval_name(widget.get_mnemonic_keyval())
        if self.mnemonics.has_key(old) and widget in self.mnemonics[old]:
            self.mnemonics[old].remove(widget)
        if not self.mnemonics.has_key(new_mnemonic):
            self.mnemonics[new_mnemonic]=[]
        self.mnemonics[new_mnemonic].append(widget)
        start = 0
        index = 0
        found = txt.lower().find(new_mnemonic,start)
        while found != -1:
            index = found
            if index==0 or txt[index-1]==' ':
                break
            found = txt.lower().find(new_mnemonic,index+1)
        widget.set_text_with_mnemonic(txt[0:index] + '_' + txt[index:])
        
        
if __name__ == '__main__':
    mm=MnemonicManager()
    import gtk.glade, gtk
    g = gtk.glade.XML('/usr/share/gourmet/app.glade')
    mm.add_glade(g)
    #tree = g.get_widget('recTree')
    #rend = gtk.CellRendererText()
    #cols = ['Cuisine','Rating','Preparation Time','Cooking Time','Title','Servings']
    #for i,l in enumerate(cols):
    #    col =  gtk.TreeViewColumn('_'+l,text=i)
    #    tree.append_column(col)
    #mod = gtk.ListStore(*[str]*(i+1))
    #for n in range(10): mod.append(cols)
    #tree.set_model(mod)
    #mm.add_treeview(tree)
    mm.fix_conflicts_peacefully()
    def show ():
        g.get_widget('app').show()
        gtk.main()
    
