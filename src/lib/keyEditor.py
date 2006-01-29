import gtk, gtk.glade, gobject, re, os, os.path
import gglobals, convert
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
        self.glade = gtk.glade.XML(os.path.join(gglobals.gladebase,'keyeditor.glade'))        
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
        self.FIELD_COL = 1
        self.VALUE_COL = 2
        self.COUNT_COL = 3
        self.REC_COL = 4
        cssu = pageable_store.ColumnSortSetterUpper(self.treeModel)
        sortable = [self.VALUE_COL,self.COUNT_COL]
        for n,head in [[self.FIELD_COL,_('Field')],
                       [self.VALUE_COL,_('Value')],
                       [self.COUNT_COL,_('Count')],
                       [self.REC_COL, _('Recipes')]]:
            renderer = gtk.CellRendererText()
            if n==self.VALUE_COL:
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
        field = self.treeModel.get_value(iter, self.FIELD_COL)
        value = self.treeModel.get_value(iter, self.VALUE_COL)
        if value == text: return
        print 'CHANGE!'
        print 'change: "%s"'%field
        if field==self.treeModel.KEY:
            print '>KEY:',
            key = value
            print 'key "%s"'%key
            if de.getBoolean(label=_('Change all keys "%s" to "%s"?')%(key,text),
                             sublabel=_("You won't be able to undo this action. If there are already ingredients with the key \"%s\", you won't be able to distinguish between those items and the items you are changing now."%text)
                             ):
                self.rd.update(
                    self.rd.iview,
                    {'ingkey':key},
                    {'ingkey':text}
                    )
                self.rd.delete_by_criteria(
                    self.rd.ikview,
                    {'ingkey':key}
                    )
        elif field==self.treeModel.ITEM:
            print '>ITEM:'
            key = self.treeModel.get_value(
                self.treeModel.iter_parent(iter),
                self.VALUE_COL
                )
            item = value
            print 'key "%s"'%key,'item "%s"'%item
            if de.getBoolean(label=_('Change all items "%s" to "%s"?')%(item,text),
                             sublabel=_("You won't be able to undo this action. If there are already ingredients with the item \"%s\", you won't be able to distinguish between those items and the items you are changing now.")%text
                             ):
                self.rd.update(
                    self.rd.iview,
                    {'item':item},
                    {'item':text}
                    )                
        elif field==self.treeModel.UNIT:
            print '>UNIT:'
            item_itr = self.treeModel.iter_parent(iter)
            key_itr = self.treeModel.iter_parent(item_itr)
            item = self.treeModel.get_value(item_itr,self.VALUE_COL)
            key = self.treeModel.get_value(key_itr,self.VALUE_COL)
            unit = value
            print 'key "%s"'%key,'item "%s"'%item,'unit "%s"'%unit
            val = de.getRadio(label='Change unit',
                                options=[
                [_('Change _all instances of "%(unit)s" to "%(text)s"')%locals(),1],
                [_('Change "%(unit)s" to "%(text)s" only for _ingredients "%(key)s"')%locals(),2],
                ],
                              default = 2,
                              )
            if val==1:
                self.rd.update(
                    self.rd.iview,
                    {'unit':unit},
                    {'unit':text},
                    )
            elif val==2:
                self.rd.update(
                    self.rd.iview,
                    {'unit':unit,'ingkey':key},
                    {'unit':text}
                    )
        elif field==self.treeModel.AMOUNT:
            print '>AMOUNT:'
            unit_itr = self.treeModel.iter_parent(iter)
            item_itr = self.treeModel.iter_parent(unit_itr)
            key_itr = self.treeModel.iter_parent(item_itr)
            unit = self.treeModel.get_value(unit_itr,self.VALUE_COL)
            item = self.treeModel.get_value(item_itr,self.VALUE_COL)
            key = self.treeModel.get_value(key_itr,self.VALUE_COL)
            amount = value
            print 'AMOUNT:','key "%s"'%key,'item "%s"'%item,'unit "%s"'%unit,'amount "%s"'%amount
            val = de.getRadio(label='Change amount',
                        options=[
                [_('Change _all instances of "%(amount)s" %(unit)s to %(text)s %(unit)s')%locals(),1],
                [_('Change "%(amount)s" %(unit)s to "%(text)s" %(unit)s only _where the ingredient key is %(key)s')%locals(),2],
                [_('Change "%(amount)s" %(unit)s to "%(text)s" %(unit)s only where the ingredient key is %(key)s _and where the item is %(item)s')%locals(),3],
                ],
                default=3,
                              )
            if val == 1:
                cond = {'unit':unit,'amount':amount}
            elif val == 2:
                cond = {'unit':unit,'amount':amount,'ingkey':key}
            elif val == 3:
                cond = {'unit':unit,'amount':amount,'ingkey':key,'item':item}
            self.rd.update(
                self.rd.iview,
                {'unit':unit,'amount':amount},
                {'unit':unit,'amount':convert.frac_to_float(amount)}
                )
        else:
            print 'NO FIELD MATCH'
            return
        print 'new val:',text
        self.treeModel.set_value(iter, n, text)
        return
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
            #rows = normtable.select(ingkey=new_key)
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
        print 'change ->',new_key,rows
        if not new_key:
            de.show_message(_("You haven't entered a key!"))
            return
        if not de.getBoolean(label=_("Are you sure you want the keys\n for all %s selections set to\n \"%s\"")%(len(rows),new_key)):
            return
        for path in rows:
            iter=self.treeModel.get_iter(path)
            field = self.treeModel.get_value(iter, self.FIELD_COL)
            if field!=self.treeModel.KEY:
                continue
            curkey = self.treeModel.get_value(iter,self.VALUE_COL)
            print 'update',curkey,'->',new_key
            self.rd.update(
                self.rd.iview,
                {'ingkey':curkey},
                {'ingkey':new_key}
                )
            self.rd.delete_by_criteria(
                self.rd.ikview,
                {'ingkey':curkey}
                )
            self.treeModel.set_value(iter, self.VALUE_COL, new_key)        
            
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

    KEY = _('Key')+':'
    ITEM = _('Item')+':'
    UNIT = _('Unit')+':'
    AMOUNT = _('Amount')+':'    
    
    columns = ['obj','ingkey','item','count','recipe']
    def __init__ (self, rd, per_page=15):
        self.rd = rd
        pageable_store.PageableTreeStore.__init__(self,
                                                  [gobject.TYPE_PYOBJECT, # row ref
                                                   str, # column
                                                   str, # value
                                                   int, # count
                                                   str, # recipe
                                                   ],
                                                  per_page=per_page)

    def reset_views (self):
        self.view = self.rd.get_ingkeys_with_count()
        #self.ikview = self.rd.filter(self.rd.ikview,lambda row: row.item)
        # Limit iview to ingkeys only, then select the unique values of that, then
        # filter ourselves to values that have keys
        #self.view = self.rd.filter(self.rd.iview.project(self.rd.iview.ingkey).unique(),
        #                           lambda foo: foo.ingkey)

    def _setup_parent_ (self, *args, **kwargs):
        self.reset_views()

    def limit_on_ingkey (self, txt, search_options={}):
        self.limit(txt,'ingkey',search_options)

    def limit_on_item (self, txt, search_options={}):
        self.limit(txt,'item',search_options)

    def limit (self, txt, column='ingkey', search_options={}):
        if not txt: self.reset_views()
        if search_options['use_regexp']:
            s = {'search':txt,'operator':'REGEXP'}
        else:
            s = {'search':'%'+txt.replace('%','%%')+'%','operator':'LIKE'}
        s['column']=column
        self.change_view(self.rd.get_ingkeys_with_count(s))
      
    def _get_length_ (self):
        return len(self.view)

    get_last_page = pageable_store.PageableViewStore.get_last_page

    def _get_slice_ (self, bottom, top):
        return [self.get_row(i) for i in self.view[bottom:top]]

    def _get_item_ (self, path):
        return self.get_row(self.view[indx])
        
    def get_row (self, row):
        return [row,
                self.KEY,
                row.ingkey,
                # avoidable slowdown (look here if code seems sluggish)
                row.count,
                None,
                ]

    def _get_children_ (self,itr):
        ret = []
        field = self.get_value(itr,1)
        value = self.get_value(itr,2)
        if field==self.KEY:
            ingkey = value
            for item in self.rd.get_unique_values('item',self.rd.iview,ingkey=ingkey):
                ret.append([None,
                            self.ITEM,
                            item,
                            self.rd.fetch_len(self.rd.iview,ingkey=ingkey,item=item),
                            self.get_recs(ingkey,item)])
        elif field==self.ITEM:
            ingkey = self.get_value(self.iter_parent(itr),2)
            item = value
            for unit in self.rd.get_unique_values('unit',self.rd.iview,ingkey=ingkey,item=item):
                ret.append([None,
                            self.UNIT,
                            unit,
                            self.rd.fetch_len(self.rd.iview,ingkey=ingkey,item=item,unit=unit),
                            None])
            if not ret:
                ret.append([None,
                            self.UNIT,
                            '',
                            self.get_value(self.iter_parent(itr),3),
                            None])                
        elif field==self.UNIT:
            item = self.get_value(self.iter_parent(itr),2)
            ingkey = self.get_value(self.iter_parent(
                self.iter_parent(itr)),2)
            unit = self.get_value(itr,2)
            amounts = []
            for i in self.rd.fetch_all(self.rd.iview,ingkey=ingkey,item=item,unit=unit):
                astring = self.rd.get_amount_as_string(i)
                if astring in amounts: continue
                ret.append([None,
                            self.AMOUNT,
                            astring,
                            (i.rangeamount
                             and self.rd.fetch_len(self.rd.iview,
                                                   ingkey=ingkey,item=item,
                                                   unit=unit,
                                                   amount=i.amount,rangeamount=i.rangeamount)
                             or  self.rd.fetch_len(self.rd.iview,
                                                   ingkey=ingkey,item=item,
                                                   unit=unit,
                                                   amount=i.amount)),
                            None])
                amounts.append(astring)
            if not ret:
                ret.append([None,
                            self.AMOUNT,
                            '',
                            self.get_value(self.iter_parent(itr),3),
                            None])
            
        return ret
        #row = row[0]
        #return [[subrow,
        #         row.ingkey,
        #         subrow.item,
        #         subrow.count,
        #         self.get_recs(row.ingkey,subrow.item)] for subrow in row.grouped]


    def get_recs (self, key, item):
        """Return a string with a list of recipes containing an ingredient with key and item"""
        recs = [i.id for i in self.rd.fetch_all(self.rd.iview,ingkey=key,item=item)]
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
    import recipeManager
    rm = recipeManager.default_rec_manager()
    import testExtras
    rg = testExtras.FakeRecGui(rm)
    ke=KeyEditor(rm,rg)
    gtk.main()
