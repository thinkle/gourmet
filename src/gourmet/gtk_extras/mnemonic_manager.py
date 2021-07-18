from gi.repository import Gdk, Gtk


def collect_descendants (parent, descendants=None):
    """Return all descendants of parent widget.

    Crawls tree recursively.
    """
    if not descendants: descendants = []
    if hasattr(parent,'get_children'):
        for c in parent.get_children():
            if c not in descendants: descendants.append(c)
            collect_descendants(c,descendants)
    if hasattr(parent,'get_submenu'):
        #print 'Getting submenu!'
        if parent.get_submenu():
            descendants.append(parent.get_submenu())
            collect_descendants(parent.get_submenu(),descendants)
    return descendants

class MnemonicManager:

    """This is a class to help prevent collisions of mnemonics. This
    works in an automated way, so that we don't have to rely on
    translators knowing which strings show up on the same page
    together in order to prevent collisions of mnemonics.

    This class can collect all mnemonics from a Gtk.Builder file or by
    working down from a toplevel widget.

    mm = MnemonicManager()

    mm.add_toplevel_widget(widget)
    OR
    mm.add_builder(Gtk.Builder instance)

    mm.fix_conflicts_peacefully()

    The fix_conflicts_peacefully algorithm will get rid of all the
    conflicts it can eliminate.  The algorithm knows that submenus are
    special animals and will set up a separate sub-instance of
    MnemonicManager to deal with each submenu within the menu system.

    mm.sacred_cows is a list of items that should never be changed.
    """

    sacred_cows = ['okay','cancel','close','file','edit']

    def __init__ (self):
        self.mnemonics = {}
        self.sub_managers = {}
        self.notebook_managers = {}
        self.untouchable_accels = []
        self.untouchable_widgs = []

    def get_submanager (self, w):
        p = w.get_parent()
        while p:
            if p in self.sub_managers:
                return self.sub_managers[p]
            p = p.get_parent()
        return self

    def add_toplevel_widget (self, w):
        widgets = collect_descendants(w)
        self.add_ui(widgets)

    def add_builder (self, ui=None, ui_file=None):
        """Add all mnemonic widgets in Gtk.Builder object.

        We can be passed a Gtk.Builder (.ui) file or a Gtk.Builder object.
        Realistically, though, you'll want to pass the object and keep
        a reference around to use. The file option's really just for
        testing :)
        """
        if not ui:
            ui = Gtk.Builder()
            ui.add_from_file(ui_file)
        widgets=ui.get_objects() # get all widgets
        # Check if there are more than one window, in which case we
        # each window gets its own sub_handler
        windows = [w for w in widgets if isinstance(w,Gtk.Window)]
        if len(windows)>0:
            for w in windows:
                self.sub_managers[w]=MnemonicManager()
                self.sub_managers[w].add_toplevel_widget(w)
            return
        else:
            self.add_ui(widgets)

    def add_ui (self, widgets):
        added = []
        # handle menu items
        menus = [x for x in widgets if isinstance(x,Gtk.Menu)]
        for menu in menus:
            #print 'Create submenu for ',menu
            self.sub_managers[menu] = MnemonicManager()
        menu_items = [x for x in widgets if isinstance(x,Gtk.MenuItem)]
        for mi in menu_items:
            #print 'Looking at menu item',mi,mi.get_children()
            widgets.remove(mi)
            children =  mi.get_children()
            if children and isinstance(children[0],Gtk.Label):
                lab = children[0]
            else:
                #print 'Ignoring menu',mi,mi.get_children()
                continue
            added.append(lab)
            if self.get_submanager(mi) == self:
                self.add_widget_mnemonic(lab,untouchable=True)
            else:
                self.get_submanager(mi).add_widget_mnemonic(lab)
        # handle other mnemonic labels we have
        has_keyval = [x for x in widgets if (hasattr(x,'get_mnemonic_keyval')
                                       and
                                       Gdk.keyval_name(x.get_mnemonic_keyval())!='VoidSymbol')]
        more_mnemonics = []
        for w in widgets:
            mm = w.list_mnemonic_labels()
            more_mnemonics.extend(mm)
            if isinstance(w,Gtk.TreeView):
                self.add_treeview(w)
        for l in more_mnemonics:
            if l not in has_keyval and l not in added: has_keyval.append(l)
        for w in has_keyval:
            # Are we in a notebook?
            nb = None
            # help(w)
            p = w.get_parent()
            added_to_sub = False
            while p:
                if isinstance(p.get_parent(),Gtk.Notebook):
                    break
                elif p.get_parent() in self.sub_managers:
                    self.sub_managers[p.get_parent()].add_widget_mnemonic(w)
                    added_to_sub = True
                    break
                else:
                    p=p.get_parent()
            if added_to_sub: continue
            if p and isinstance(p.get_parent(),Gtk.Notebook):
                nb = p.get_parent()
                page = nb.page_num(p)
                if nb not in self.notebook_managers:
                    self.notebook_managers[nb]={}
                if page not in self.notebook_managers[nb]:
                    self.notebook_managers[nb][page]=MnemonicManager()
                self.notebook_managers[nb][page].add_widget_mnemonic(w)
            else:
                if isinstance(w.get_parent(),Gtk.Notebook):
                    # make notebook tab labels (should be our only
                    # direct descendant labels) untouchable.
                    self.add_widget_mnemonic(w,untouchable=True,fix_untouchables=True)
                else:
                    self.add_widget_mnemonic(w)
        more_mnemonics = []

    def add_treeview (self, tv):
        #print 'Mnemonic manager add TV'
        for c in tv.get_columns():
            t = c.get_title()
            #print 'Column:',t
            if t.find('_')>-1:
                widg = Gtk.Label(label=t)
                widg.set_use_underline(True)
                c.set_widget(widg)
                widg.show()
                self.add_widget_mnemonic(widg)

    def add_widget_mnemonic (self, w, untouchable=False, fix_untouchables=False):
        k = Gdk.keyval_name(w.get_mnemonic_keyval())
        if w.get_text().lower().replace('_','') in self.sacred_cows:
            untouchable = True; fix_untouchables=False
        if untouchable:
            if k in self.untouchable_accels and fix_untouchables:
                # we have a conflict among untouchables to fix...
                alts = self.find_alternatives(w)
                if alts:
                    k = alts[0]
                    self.change_mnemonic(w,k)
            #print 'Add untouchable key:',k,w
            self.untouchable_accels.append(k)
            self.untouchable_widgs.append(w)
        if k not in self.mnemonics: self.mnemonics[k]=[]
        if not w in self.mnemonics[k]:
            self.mnemonics[k].append(w)

    def generate_new_mnemonic (self, text):
        for c in text:
            if c.lower() not in self.mnemonics:
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
            alts = [l for l in alts if l not in self.untouchable_accels]
        return alts

    def find_peaceful_alternatives (self, w):
        return [l for l in self.find_alternatives(w) if l not in self.mnemonics]

    def fix_conflicts_peacefully (self, do_submenus=True):
        """Remove all conflicts from mnemonics.

        Don't touch anything in self.sacred_cows.  if do_submenus is
        True, we will recursively resolve mnemonic conflicts within
        any sub-menus as well.
        """
        to_reconcile = []
        changed = []
        #print 'MNEMONICS: ',
        #for k,v in self.mnemonics.items():
        #    print k,[w.get_text() for w in v],
        #print
        for k,v in list(self.mnemonics.items()):
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
                        #print 'Generated alternatives for ',w,w.get_text(),':',alts
                        can_move.append((w,alts))
                if len(can_move)==len(v):
                    # If everything is movable, then we keep our first
                    # AccelLabel guy as it was and move the rest.
                    from functools import cmp_to_key
                    can_move.sort(key=cmp_to_key(self.sort_movables))
                    can_move=can_move[1:]
                # We extend our guys to move with to_move
                for w,alts in can_move:
                    #print 'Changing mnemonic',w,w.get_text(),alts[0]
                    self.change_mnemonic(w,alts[0])
                    changed.append(w)
        if changed:
            #print '>>>Recursing...'
            self.fix_conflicts_peacefully()
            #print '<<<Done recursing'
        if do_submenus:
            for mm in list(self.sub_managers.values()):
                #print '>>>>>Submenus...'
                mm.fix_conflicts_peacefully()
                #print '<<<<<Done with submenus'
        # for each of our notebooks
        for nb in list(self.notebook_managers.values()):
            # for each of our pages
            for pagemanager in list(nb.values()):
                self.merge_notebook(pagemanager)
                pagemanager.fix_conflicts_peacefully()

    def merge_notebook (self, notebook_manager):
        """Add our own items to a notebook page manager as untouchables.

        In other words, the notebook's manager will know to avoid
        other widgets in the containing context, but won't touch us.
        """
        for ww in list(self.mnemonics.values()):
            for w in ww:
                notebook_manager.add_widget_mnemonic(w,untouchable=True)

    def sort_movables (self, moveable1, moveable2):
        widg,alts = moveable1
        widg2,alts2 = moveable2
        al1 = isinstance(widg,Gtk.AccelLabel)
        al2 = isinstance(widg2,Gtk.AccelLabel)
        if al1 and not al2: return 1
        elif al2 and not al1: return -1
        else: return 0

    def get_all_possibilities (self):
        pass

    def change_mnemonic (self, widget, new_mnemonic):
        txt=widget.get_text()
        old = Gdk.keyval_name(widget.get_mnemonic_keyval())
        if old in self.mnemonics and widget in self.mnemonics[old]:
            self.mnemonics[old].remove(widget)
        if new_mnemonic not in self.mnemonics:
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
    from pkgutil import get_data
    mm=MnemonicManager()
    ui = Gtk.Builder()
    ui.add_from_string(get_data('gourmet', 'ui/app.ui').decode())
    mm.add_builder(ui)
    #tree = ui.get_widget('recTree')
    #rend = Gtk.CellRendererText()
    #cols = ['Cuisine','Rating','Preparation Time','Cooking Time','Title','Servings']
    #for i,l in enumerate(cols):
    #    col =  Gtk.TreeViewColumn('_'+l,text=i)
    #    tree.append_column(col)
    #mod = Gtk.ListStore(*[str]*(i+1))
    #for n in range(10): mod.append(cols)
    #tree.set_model(mod)
    #mm.add_treeview(tree)
    mm.fix_conflicts_peacefully()
    def show ():
        ui.get_widget('app').show()
        ui.get_widget('app').connect('delete-event',Gtk.main_quit)
        Gtk.main()
    show()
