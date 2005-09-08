import gtk, gtk.glade, gobject, re
from gglobals import *
import WidgetSaver
import cb_extras as cb
import dialog_extras as de
from gettext import gettext as _
from gettext import ngettext
import mnemonic_manager
import pageable_store

class KeyEditor:

    """KeyEditor sets up a GUI to allow editing which keys correspond to which items throughout
    the recipe database. It is useful for corrections or changes to keys en masse.
    """
    
    def __init__ (self, rd=None, rg=None):
        self.glade = gtk.glade.XML(os.path.join(gladebase,'keyeditor.glade'))        
        self.rd = rd
        self.rg = rg
        self.widget_names = ['treeview', 'searchByBox', 'searchEntry', 'searchButton', 'window',
                             'searchAsYouTypeToggle', 'regexpTog', 'changeKeyEntry', 'changeKeyButton' ]
        for w in self.widget_names:
            setattr(self,w,self.glade.get_widget(w))
        # setup entry callback to sensitize/desensitize apply
        self.changeKeyButton.set_sensitive(False)
        self.changeKeyEntry.connect('changed',self.changeKeyEntryChangedCB)
        # Make our lovely model
        self.makeTreeModel()
        # setup completion in entry
        cb.make_completion(self.changeKeyEntry,self.rg.inginfo.key_model)
        # Setup next/prev/first/last buttons for view
        self.prev_button = self.glade.get_widget('prevButton')
        self.next_button = self.glade.get_widget('nextButton')
        self.first_button = self.glade.get_widget('firstButton')
        self.last_button = self.glade.get_widget('lastButton')
        self.showing_label = self.glade.get_widget('showingLabel')
        self.prev_button.connect('clicked',lambda *args: self.treeModel.prev_page())
        self.next_button.connect('clicked',lambda *args: self.treeModel.next_page())
        self.first_button.connect('clicked',lambda *args: self.treeModel.goto_first_page())
        self.last_button.connect('clicked',lambda *args: self.treeModel.goto_last_page())
        # Setup search stuff
        self.search_string=""
        self.search_by = _('Key')
        self.use_regexp=True
        self.setupTreeView()
        self.treeview.set_model(self.treeModel)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        #self.treeview.set_model(self.treeModel)
        self.glade.signal_autoconnect({
            'iSearch':self.isearchCB,
            'search':self.searchCB,
            'search_as_you_type_toggle':self.search_as_you_typeCB,
            'changeKey':self.change_keyCB,
            'close_window': lambda *args: self.window.hide() and self.window.destroy()
            })
        # setup mnemonic manager
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.sacred_cows.append('search for')
        self.mm.add_glade(self.glade)
        self.mm.add_treeview(self.treeview)
        self.mm.fix_conflicts_peacefully()
        # to set our regexp_toggled variable
        self.searchByBox.set_active(0)
        self.dont_ask = self.rg.prefs.get('dontAskDeleteKey',False)
        # setup WidgetSavers
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.searchAsYouTypeToggle,
            self.rg.prefs.get('sautTog',
                           {'active':self.searchAsYouTypeToggle.get_active()}),
            ['toggled']))
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.regexpTog,
            self.rg.prefs.get('regexpTog',
                           {'active':self.regexpTog.get_active()}),
            ['toggled']))
                
    def dont_ask_cb (self, widget, *args):
        self.dont_ask=widget.get_active()
        self.rg.prefs['dontAskDeleteKey']=self.dont_ask
    
    def setupTreeView (self):
        self.KEY_COL = 1
        self.ITEM_COL = 2
        self.COUNT_COL = 3
        self.REC_COL = 4
        cssu = pageable_store.ColumnSortSetterUpper(self.treeModel)
        sortable = [self.KEY_COL]
        for n,head in [[self.KEY_COL,_('_Key')],
                       [self.ITEM_COL,_('Item')],
                       [self.COUNT_COL,_('Count')],
                       [self.REC_COL, _('Recipes')]]:
            renderer = gtk.CellRendererText()
            if n==self.KEY_COL or n==self.ITEM_COL:
                renderer.set_property('editable',True)
                renderer.connect('edited',self.tree_edited,n,head)
            col = gtk.TreeViewColumn(head, renderer, text=n)
            col.set_resizable(True)
            self.treeview.append_column(col)
            if n in sortable: cssu.set_sort_column_id(col,n)

    def tree_edited (self, renderer, path_string, text, n, head):
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        iter = self.treeModel.get_iter(path)
        key = self.treeModel.get_value(iter, self.KEY_COL)
        item = self.treeModel.get_value(iter, self.ITEM_COL)
        children = self.treeModel.iter_children(iter)
        if n==self.KEY_COL and key==text: return
        if n==self.ITEM_COL and item==text: return
        ## make sure they want to make this change
        if not self.dont_ask:
            msg = _("Are you sure you want to change the ")
            if n==self.KEY_COL: msg += _('key')
            if n==self.ITEM_COL: msg += _('item')
            if item:
                msg += _("for \"%s from \"%s\"")%(item,key)
            else:
                msg += _(" from \"%s\" ")%key
            msg += _(" to \"%s\"")%text
            if not de.getBoolean(label=msg,
                                 dont_ask_cb=self.dont_ask_cb,
                                 dont_ask_custom_text=_("Don't ask me before changing keys and items.")
                                 ):
                return
        if children and n==self.KEY_COL:
            self.change_children(key, text, iter)
        else:
            if n==self.KEY_COL:
                self.changeItem(key, item, new_key=text)
            elif n==self.ITEM_COL:
                self.changeItem(key, item, new_item=text)
        #self.treeModel.set_value(iter, n, text)
        self.treeModel.update_tree()

    def change_children (self, key, new_key, iter):
        # if it's children, it means we're changing a key for
        # all cases... and then we just have to change the model
        # so our user knows it worked
        normtable = self.rd.normalizations['ingkey']
        new_keys = normtable.select(ingkey=new_key)
        if new_keys:
            # then we just have to change all occurrences in ingview...
            self.changeItem(key,new_key=new_key)
            #self.rd.delete_by_criteria(normtable,{'ingkey':key}) # nuke the old key
        # If the new key doesn't exist yet, we just change the key reference in the
        # normalization table (i.e. key ID 462 now points to "sugar")
        else:
            row = normtable.select(ingkey=key)[0]
            row.ingkey = new_key
            rows = normtable.select(ingkey=new_key)
        self.reset_tree()
        
    def changeItem (self, key, item=None, new_key=None, new_item=None):
        if item:
            vw=self.rd.iview.select(ingkey=key,item=item)
        else:
            vw=self.rd.iview.select(ingkey=key)
        for i in vw:
            if new_key:
                self.rd.modify_ing(i,{'ingkey':new_key})
                #i.ingkey=new_key
                self.rd.changed=True
            if new_item:
                self.rd.modify_ing(i,{'item':new_item})
                #i.item=new_item
                self.rd.changed=True
        self.reset_tree()
        
    def makeTreeModel (self):
        self.treeModel = KeyStore(self.rd,per_page=self.rg.prefs.get('recipes_per_page',12))
        #self.orig_view = self.treeModel.view
        self.treeModel.connect('page-changed',self.model_changed_cb)
        self.treeModel.connect('view-changed',self.model_changed_cb)
        
    def doSearch (self):
        """Do the actual searching."""
        last_search = self.search_string
        self.search_string = self.searchEntry.get_text()
        last_by = self.search_by
        self.search_by = cb.cb_get_active_text(self.searchByBox)
        last_regexp = self.use_regexp
        self.use_regexp = self.regexpTog.get_active()
        if (self.search_by==last_by and
            self.search_string==last_search and
            self.use_regexp==last_regexp):
            # Don't do anything...
            return
        # RESET THE VIEW IF NEED BE
        if (self.search_string.find(last_search)!=0 or
            self.search_by != last_by or
            self.use_regexp != last_regexp):
            self.treeModel.reset_views()
        if self.search_by == _('Key'):
            self.treeModel.limit_on_ingkey(self.search_string,
                                           search_options={'use_regexp':self.use_regexp,}
                                           )
        else:
            self.treeModel.limit_on_item(self.search_string,
                                         search_options={'use_regexp':self.use_regexp})

    def isearchCB (self, *args):
        if self.searchAsYouTypeToggle.get_active():
            self.doSearch()

    def searchCB (self, *args):
        self.doSearch()

    def search_as_you_typeCB (self, *args):
        if self.searchAsYouTypeToggle.get_active():
            self.searchButton.hide()
        else: self.searchButton.show()

    def change_keyCB (self, *args):
        new_key = self.changeKeyEntry.get_text()
        mod,rows = self.treeview.get_selection().get_selected_rows()
        if not new_key:
            de.show_message(_("You haven't entered a key!"))
            return
        if not de.getBoolean(label=_("Are you sure you want the keys\n for all %s selections set to\n \"%s\"")%(len(rows),new_key)):
            return
        for path in rows:
            iter=self.treeModel.get_iter(path)
            key = self.treeModel.get_value(iter, self.KEY_COL)
            item = self.treeModel.get_value(iter, self.ITEM_COL)
            self.changeItem(key,item,new_key=new_key)
            self.change_children(key, new_key, iter)
            self.treeModel.set_value(iter, self.KEY_COL, new_key)        
            
    def changeKeyEntryChangedCB (self, *args):
        if self.changeKeyEntry.get_text():
            self.changeKeyButton.set_sensitive(True)
        else: self.changeKeyButton.set_sensitive(False)

    def reset_tree (self):
        self.treeModel.reset_views()
        self.search_by = None
        self.search_string = ''
        self.doSearch()

    # Paging handlers
    def model_changed_cb (self, model):
        if model.page==0:
            self.prev_button.set_sensitive(False)
            self.first_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)
            self.first_button.set_sensitive(True)
        if model.get_last_page()==model.page:
            self.next_button.set_sensitive(False)
            self.last_button.set_sensitive(False)
        else:
            self.next_button.set_sensitive(True)
            self.last_button.set_sensitive(True)
        self.update_showing_label()
        
    def update_showing_label (self):
        bottom,top,total = self.treeModel.showing()
        if top >= total and bottom==1:
            lab = ngettext('%s ingredient','%s ingredients',top)%top
        else:
            # Do not translate bottom, top and total -- I use these fancy formatting
            # strings in case your language needs the order changed!
            lab = _('Showing ingredients %(bottom)s to %(top)s of %(total)s'%locals())
        self.showing_label.set_markup('<i>' + lab + '</i>')


class KeyStore (pageable_store.PageableTreeStore,pageable_store.PageableViewStore):
    """A ListStore to show our beautiful keys.
    """
    __gsignals__ = {
        'view-changed':(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
        }
    columns = ['obj','ingkey','item','count','recipe']
    def __init__ (self, rd, per_page=15):
        self.rd = rd
        pageable_store.PageableTreeStore.__init__(self,
                                                  [gobject.TYPE_PYOBJECT, # row ref
                                                   str, # key
                                                   str, # item
                                                   int, # count
                                                   str, # recipe
                                                   ],
                                                  per_page=per_page)

    def reset_views (self):
        self.ikview = self.rd.filter(self.rd.ikview,lambda row: row.item)
        # Limit iview to ingkeys only, then select the unique values of that, then
        # filter ourselves to values that have keys
        self.view = self.rd.filter(self.rd.iview.project(self.rd.iview.ingkey).unique(),
                                   lambda foo: foo.ingkey)
        

    def _setup_parent_ (self, *args, **kwargs):
        self.reset_views()

    def limit_on_ingkey (self, txt, search_options={}):
        if not txt: self.reset_views()
        self.change_view(self.rd.search(self.view,'ingkey',txt,**search_options))

    def limit_on_item (self, txt, search_options={}):
        if not txt: self.reset_views()
        results = self.rd.search(self.rd.ikview,'item',txt,**search_options)
        self.change_view(
            # this should probably be done with some kind of funky join...
            self.rd.filter(self.view,
                           lambda foo: results.select(ingkey=foo.ingkey) and True or False)
            )

    def _get_length_ (self):
        return len(self.view)

    get_last_page = pageable_store.PageableViewStore.get_last_page

    def _get_slice_ (self, bottom, top):
        return [self.get_row(i) for i in self.view[bottom:top]]

    def _get_item_ (self, path):
        return self.get_row(self.view[indx])
        
    def get_row (self, row):
        return [row,
                row.ingkey,
                None,
                # avoidable slowdown (look here if code seems sluggish)
                len(self.rd.iview.select(ingkey=row.ingkey)),
                None,
                ]

    def _get_children_ (self, row):
        ingkey =row[1]
        ret = []
        for child in self.ikview.select(ingkey=ingkey):
            item = child.item
            ret.append([child,
                        ingkey,
                        item,
                        # avoidable slowdown (look here if code seems sluggish)                        
                        len(self.rd.iview.select(ingkey=ingkey,item=item)),
                        self.get_recs(ingkey,item)])
        return ret
        #row = row[0]
        #return [[subrow,
        #         row.ingkey,
        #         subrow.item,
        #         subrow.count,
        #         self.get_recs(row.ingkey,subrow.item)] for subrow in row.grouped]

    def get_recs (self, key, item):
        """Return a string with a list of recipes containing an ingredient with key and item"""
        recs = [i.id for i in self.rd.iview.select(ingkey=key,item=item)]
        titles = []
        looked_at = []
        for r_id in recs:
            if r_id in looked_at: continue
            rec = self.rd.get_rec(r_id)
            if rec:
                titles.append(rec.title)
        return ", ".join(titles)

if gtk.pygtk_version[1]<8:
    gobject.type_register(KeyStore)    

if __name__ == '__main__':
    ke=KeyEditor()
    gtk.main()
