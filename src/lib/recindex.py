#!/usr/bin/env python
import gtk.glade, gtk, time, re, gtk.gdk, gobject, pango
from gtk_extras import WidgetSaver, ratingWidget
from ImageExtras import get_pixbuf_from_jpg
from gtk_extras import dialog_extras as de
from gtk_extras import treeview_extras as te
from gtk_extras import cb_extras as cb
import convert, Undo
from gglobals import *
from gdebug import debug
from gtk_extras import mnemonic_manager
from gtk_extras import pageable_store
from gettext import gettext as _
from gettext import ngettext

class RecIndex:
    """We handle the 'index view' of recipes, which puts
    a recipe model into a tree and allows it to be searched
    and sorted. We're a separate class from the main recipe
    program so that we can be created again (e.g. in the recSelector
    dialog called from a recipe card."""

    default_searches = [{'column':'deleted','operator':'=','search':False}]
    
    def __init__ (self, glade, rd, rg, editable=False):
        #self.visible = 1 # can equal 1 or 2
        self.editable=editable
        self.selected = True        
        self.rtcols=rg.rtcols
        self.rtcolsdic=rg.rtcolsdic
        self.rtwidgdic=rg.rtwidgdic
        self.prefs=rg.prefs
        self.glade = glade
        self.rd = rd
        self.rg = rg
        self.searchByDic = {
            unicode(_('anywhere')):'anywhere',
            unicode(_('title')):'title',
            unicode(_('ingredient')):'ingredient',
            unicode(_('instructions')):'instructions',
            unicode(_('notes')):'modifications',
            unicode(_('category')):'category',
            unicode(_('cuisine')):'cuisine',
            #_('rating'):'rating',
            unicode(_('source')):'source',
            }
        self.searchByList = [_('anywhere'),
                             _('title'),
                             _('ingredient'),
                             _('category'),
                             _('cuisine'),
                             #_('rating'),
                             _('source'),
                             _('instructions'),
                             _('notes'),
                             ]
        # ACK, this breaks internationalization!
        #self.SEARCH_KEY_DICT = {
        #    "t":_("title"),
        #    "i":_("ingredient"),
        #    "c":_("category"),
        #    "u":_("cuisine"),
        #    's':_("source"),
        #    }        
        self.setup_search_actions()
        self.setup_widgets()

    def setup_widgets (self):
        self.srchentry=self.glade.get_widget('rlistSearchbox')
	self.limitButton = self.glade.get_widget('rlAddButton')
        # Don't # allow for special keybindings
        #self.srchentry.connect('key_press_event',self.srchentry_keypressCB)        
        self.SEARCH_MENU_KEY = "b"
        self.srchLimitBar = self.glade.get_widget('srchLimitBar')
        assert(self.srchLimitBar)
        self.srchLimitBar.hide()
        self.srchLimitLabel=self.glade.get_widget('srchLimitLabel')
        self.srchLimitClearButton = self.glade.get_widget('srchLimitClear')
        self.srchLimitText=self.srchLimitLabel.get_text()
        self.srchLimitDefaultText=self.srchLimitText
        self.searchButton = self.glade.get_widget('searchButton')
        self.rSearchByMenu = self.glade.get_widget('rlistSearchByMenu')
        cb.set_model_from_list(self.rSearchByMenu, self.searchByList, expand=False)
        cb.setup_typeahead(self.rSearchByMenu)
        self.rSearchByMenu.set_active(0)
        self.rSearchByMenu.connect('changed',self.search_as_you_type)
        self.sautTog = self.glade.get_widget('searchAsYouTypeToggle')
        self.search_actions.get_action('toggleSearchAsYouType').connect_proxy(self.sautTog)
        self.regexpTog = self.glade.get_widget('regexpTog')
        self.searchOptionsBox = self.glade.get_widget('searchOptionsBox')
        self.search_actions.get_action('toggleShowSearchOptions').connect_proxy(
            self.glade.get_widget('searchOptionsToggle')
            )
        self.search_actions.get_action('toggleRegexp').connect_proxy(self.regexpTog)
        self.rectree = self.glade.get_widget('recTree')
        self.rectree.connect('start-interactive-search',lambda *args: self.srchentry.grab_focus())
        self.prev_button = self.glade.get_widget('prevButton')
        self.next_button = self.glade.get_widget('nextButton')
        self.first_button = self.glade.get_widget('firstButton')
        self.last_button = self.glade.get_widget('lastButton')        
        self.showing_label = self.glade.get_widget('showingLabel')
        self.stat = self.glade.get_widget('statusbar')
        self.contid = self.stat.get_context_id('main')
        self.setup_search_views()
        self.setup_rectree()
        self.prev_button.connect('clicked',lambda *args: self.rmodel.prev_page())
        self.next_button.connect('clicked',lambda *args: self.rmodel.next_page())
        self.first_button.connect('clicked',lambda *args: self.rmodel.goto_first_page())
        self.last_button.connect('clicked',lambda *args: self.rmodel.goto_last_page())
        self.glade.signal_autoconnect({
            'rlistSearch': self.search_as_you_type,
            'ingredientSearch' : lambda *args: self.set_search_by('ingredient'),
            'titleSearch' : lambda *args: self.set_search_by('title'),
            'ratingSearch' : lambda *args: self.set_search_by('rating'),
            'categorySearch' : lambda *args: self.set_search_by('category'),
            'cuisineSearch' : lambda *args: self.set_search_by('cuisine'),
            'search' : self.search,
            'searchBoxActivatedCB':self.search_entry_activate_cb,
            'rlistReset' : self.reset_search,
            'rlistLimit' : self.limit_search,
            'search_as_you_type_toggle' : self.toggleTypeSearchCB,})
        self.toggleTypeSearchCB(self.sautTog)
        # this has to come after the type toggle is connected!
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.sautTog,
            self.prefs.get('sautTog',
                           {'active':self.sautTog.get_active()}),
            ['toggled']))
        self.rg.conf.append(WidgetSaver.WidgetSaver(
            self.regexpTog,
            self.prefs.get('regexpTog',
                           {'active':self.regexpTog.get_active()}),
            ['toggled']))        
        # and we update our count with each deletion.
        self.rd.delete_hooks.append(self.set_reccount)
        # setup a history
        self.uim=self.glade.get_widget('undo_menu_item')
        self.rim=self.glade.get_widget('redo_menu_item')
        self.raim=self.glade.get_widget('reapply_menu_item')
        self.history = Undo.UndoHistoryList(self.uim,self.rim,self.raim)
        # Fix up our mnemonics with some heavenly magic
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.sacred_cows.append("search for") # Don't touch _Search for
        self.mm.add_glade(self.glade)
        self.mm.add_treeview(self.rectree)
        self.mm.fix_conflicts_peacefully()

    def setup_search_actions (self):
        self.search_actions = gtk.ActionGroup('SearchActions')
        self.search_actions.add_toggle_actions([
            ('toggleRegexp',None,_('Use regular expressions in search'),
             None,_('Use regular expressions (an advanced search language) in text search'),
             self.toggleRegexpCB,False),
            ('toggleSearchAsYouType',None,_('Search as you type'),None,
             _('Search as you type (turn off if search is too slow).'),
             self.toggleTypeSearchCB, True
             ),
            ('toggleShowSearchOptions',
             None,
             _('Show Search _Options'),
             None,
             _('Show advanced searching options'),
             self.toggleShowSearchOptions),
            ])

    def setup_search_views (self):
        """Setup our views of the database."""
        self.last_search = {}
        #self.rvw = self.rd.fetch_all(self.rd.recipe_table,deleted=False)
        self.searches = self.default_searches[0:]
        self.sort_by = []
        self.rvw = self.rd.search_recipes(self.searches,sort_by=self.sort_by)

    def make_rec_visible (self, *args):
        """Make sure recipe REC shows up in our index."""
        #if not self.rg.wait_to_filter:
        #self.setup_search_views()
        self.redo_search()
        #debug('make_rec_visible',0)
        #self.visible.append(rec.id)
        #if not self.rg.wait_to_filter:
        #    self.rmodel_filter.refilter()

    def search_entry_activate_cb (self, *args):
        if self.rmodel._get_length_()==1:
            self.rec_tree_select_rec()
        else:
            if not self.search_as_you_type:
                self.search()
                gobject.idle_add(lambda *args: self.limit_search())
            else:
                self.limit_search()
    
    def rmodel_page_changed_cb (self, rmodel):
        if rmodel.page==0:
            self.prev_button.set_sensitive(False)
            self.first_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)
            self.first_button.set_sensitive(True)
        if rmodel.get_last_page()==rmodel.page:
            self.next_button.set_sensitive(False)
            self.last_button.set_sensitive(False)
        else:
            self.next_button.set_sensitive(True)
            self.last_button.set_sensitive(True)
        self.set_reccount()

    def rmodel_sort_cb (self, rmodel, sorts):
        self.sort_by = sorts
        self.last_search = {}
        self.search()
        #self.do_search(None,None)

    def create_rmodel (self, vw):
        self.rmodel = RecipeModel(vw,self.rd,per_page=self.prefs.get('recipes_per_page',12))
        #self.set_reccount() # This will be called by the rmodel_page_changed_cb
    
    def setup_rectree (self):
        """Create our recipe treemodel."""
        self.create_rmodel(self.rvw)
        self.rmodel.connect('page-changed',self.rmodel_page_changed_cb)
        self.rmodel.connect('view-changed',self.rmodel_page_changed_cb)
        self.rmodel.connect('view-sort',self.rmodel_sort_cb)
        # and call our handler once to update our prev/next buttons + label
        self.rmodel_page_changed_cb(self.rmodel)
        # and hook up our model
        self.rectree.set_model(self.rmodel)
        self.rectree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.selection_changed()
        self.setup_reccolumns()
        # this has to come after columns are added or else adding columns resets out column order!
        self.rectree_conf=te.TreeViewConf(self.rectree,
                                          hidden=self.prefs.get('rectree_hidden_columns',DEFAULT_HIDDEN_COLUMNS),
                                          order=self.prefs.get('rectree_column_order',{}))
        self.rectree_conf.apply_column_order()
        self.rectree_conf.apply_visibility()
        self.rectree.connect("row-activated",self.rec_tree_select_rec)#self.rec_tree_select_rec)
        self.rectree.get_selection().connect("changed",self.selection_changedCB)
        self.rectree.set_property('rules-hint',True) # stripes!
        self.rectree.expand_all()
        self.rectree.show()

    def set_reccount (self, *args):
        """Display the count of currently visible recipes."""
        debug("set_reccount (self, *args):",5)
        self.count = self.rmodel._get_length_()
        bottom,top,total = self.rmodel.showing()
        if top >= total and bottom==1:
            lab = ngettext('%s recipe','%s recipes',top)%top
            for b in self.first_button,self.prev_button,self.next_button,self.last_button:
                b.hide()
        else:
            for b in self.first_button,self.prev_button,self.next_button,self.last_button:
                b.show()
            # Do not translate bottom, top and total -- I use these fancy formatting
            # strings in case your language needs the order changed!
            lab = _('Showing recipes %(bottom)s to %(top)s of %(total)s'%locals())
        self.showing_label.set_markup('<i>' + lab + '</i>')
        if self.count == 1:
            sel = self.rectree.get_selection()
            if sel: sel.select_path((0,))

    def setup_reccolumns (self):
        """Setup the columns of our recipe index TreeView"""
        renderer = gtk.CellRendererPixbuf()
        cssu=pageable_store.ColumnSortSetterUpper(self.rmodel)
        col = gtk.TreeViewColumn("",renderer,pixbuf=1)
        col.set_min_width(-1)
        self.rectree.append_column(col)
        n = 2
        crc = True
        if not hasattr(gtk,'CellRendererCombo'):
            print 'CellRendererCombo not yet supported'
            print 'Update pygtk/gtk for lovely comboboxes'
            print 'in your treemodels!'
            print '(but don\'t worry, Gourmet will still work'
            print 'fine with what you have)'
        _title_to_num_ = {}
        for c in self.rtcols:
            if c=='rating':
                # special case -- for ratings we set up our lovely
                # star widget
                twsm = ratingWidget.TreeWithStarMaker(
                    self.rectree,
                    self.rg.star_generator,
                    data_col=n,
                    col_title='_%s'%self.rtcolsdic[c],
                    handlers=[self.star_change_cb],
                    properties={'reorderable':True,
                                'resizable':True},
                    )
                cssu.set_sort_column_id(twsm.col,twsm.data_col)
                n += 1
                twsm.col.set_min_width(110)
                continue
            # And we also special case our time column
            elif c in ['preptime','cooktime']:
                _title_to_num_[self.rtcolsdic[c]]=n
                renderer=gtk.CellRendererText()
                renderer.set_property('editable',True)
                renderer.connect('edited',self.rtree_time_edited_cb,n,c)
                def get_colnum (tc):
                    try:
                        t = tc.get_title()
                        if t:
                            return _title_to_num_[t.replace('_','')]
                        else:
                            print 'wtf, no title for ',tc
                            return -1
                    except:
                        print 'problem with ',tc
                        raise
                    
                ncols = self.rectree.insert_column_with_data_func(
                    -1,
                    '_%s'%self.rtcolsdic[c],
                    renderer,
                    lambda tc,cell,mod,titr: \
                    cell.set_property(
                    'text',
                    convert.seconds_to_timestring(mod.get_value(
                    titr,
                    get_colnum(tc),
                    #_title_to_num_[tc.get_title().replace('_','')],
                    ))
                    )
                    )
                col=self.rectree.get_column(ncols-1)
                cssu.set_sort_column_id(col,n)
                col.set_property('reorderable',True)
                col.set_property('resizable',True)
                n+=1
                continue
            elif self.editable and CRC_AVAILABLE and self.rtwidgdic[c]=='Combo':
                renderer = gtk.CellRendererCombo()
                model = gtk.ListStore(str)
                if c=='category':
                    map(lambda i: model.append([i]),self.rg.rd.get_unique_values(c,self.rg.rd.categories_table)
                        )
                else:
                    map(lambda i: model.append([i]),self.rg.rd.get_unique_values(c))
                renderer.set_property('model',model)
                renderer.set_property('text-column',0)
            else:
                renderer = gtk.CellRendererText()
                if c=='link':
                    renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
                else:
                    # If we have gtk > 2.8, set up text-wrapping
                    try:
                        renderer.get_property('wrap-width')
                    except TypeError:
                        pass
                    else:
                        renderer.set_property('wrap-mode',pango.WRAP_WORD)
                        if c == 'title': renderer.set_property('wrap-width',200)
                        else: renderer.set_property('wrap-width',150)
            renderer.set_property('editable',self.editable)
            renderer.connect('edited',self.rtree_edited_cb,n, c)
            titl = self.rtcolsdic[c]
            col = gtk.TreeViewColumn('_%s'%titl,renderer, text=n)
            # Ensure that the columns aren't really narrow on initialising.
            #if c=='title':            # Adjust these two to be even bigger
            #    col.set_min_width(200)
            #else:
            #    col.set_min_width(60)
            if c=='title':
                col.set_property('expand',True)
            col.set_reorderable(True)
            col.set_resizable(True)
            col.set_clickable(True)
            #col.connect('clicked', self.column_sort)
            self.rectree.append_column(col)
            cssu.set_sort_column_id(col,n)
            debug("Column %s is %s->%s"%(n,c,self.rtcolsdic[c]),5)
            n += 1

    def toggleTypeSearchCB (self, widget):
        """Toggle search-as-you-type option."""
        if widget.get_active():
            self.search_as_you_type=True
            self.searchButton.hide()
        else:
            self.search_as_you_type=False
            self.searchButton.show()

    def toggleRegexpCB (self, widget):
        """Toggle search-with-regexp option."""
        #if widget.get_active():
        #    self.message('Advanced searching (regular expressions) turned on')
        #else:
        #    self.message('Advanced searching off')
        pass

    def toggleShowSearchOptions (self, widget):
        if widget.get_active():
            self.searchOptionsBox.show()
        else:
            self.searchOptionsBox.hide()

    def regexpp (self):
        """Return True if we're using regexps"""
        if self.regexpTog.get_active():
            return True
        else:
            return False

    def search_as_you_type (self, *args):
        """If we're searching-as-we-type, search."""
        if self.search_as_you_type:
            self.search()

    def set_search_by (self, str):
        """Manually set the search by label to str"""
        debug('set_search_by',1)
        #self.rSearchByMenu.get_children()[0].set_text(str)
        cb.cb_set_active_text(self.rSearchByMenu, str)
        self.search()

    def redo_search (self, *args):
        self.last_search = {}
        self.search()
    
    def search (self, *args):
        debug("search (self, *args):",5)
        txt = self.srchentry.get_text()
        searchBy = cb.cb_get_active_text(self.rSearchByMenu)
        searchBy = self.searchByDic[unicode(searchBy)]
	if txt and self.limitButton: self.limitButton.set_sensitive(True)
        elif self.limitButton: self.limitButton.set_sensitive(False)
        if self.make_search_dic(txt,searchBy) == self.last_search:
            debug("Same search!",1)
            return
        if self.srchentry.window: self.srchentry.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        debug('Doing new search for %s, last search was %s'%(self.make_search_dic(txt,searchBy),self.last_search),1)
        gobject.idle_add(lambda *args: self.do_search(txt, searchBy))

    def make_search_dic (self, txt, searchBy):
        srch = {'column':searchBy}
        if self.regexpp():
            srch['operator'] = 'REGEXP'
            srch['search'] = txt.replace(' %s '%_('or'), # or operator for searches
                                         '|')
        else:
            srch['operator']='LIKE'
            srch['search'] = txt.replace('%','%%')+'%'
        return srch

    def do_search (self, txt, searchBy):
        if txt and searchBy:
            srch = self.make_search_dic(txt,searchBy)
            self.last_search = srch.copy()
            self.update_rmodel(self.rd.search_recipes(
                self.searches + [srch],
                sort_by=self.sort_by)
                               )
        elif self.searches:
            self.update_rmodel(self.rd.search_recipes(
                self.searches,
                sort_by=self.sort_by)
                               )
        else:
            self.update_rmodel(self.rd.fetch_all(self.recipe_table,deleted=False,sort_by=self.sort_by))
    
    def limit_search (self, *args):
        debug("limit_search (self, *args):",5)
        self.search() # make sure we've done the search...
        self.searches.append(self.last_search)
        last_col = self.last_search['column']
        self.srchLimitBar.show()
        if last_col != _('anywhere'):
            newtext = ' ' + _('%s in %s')%(self.srchentry.get_text(),last_col)
        else:
            newtext = ' ' + self.srchentry.get_text()
        if self.srchLimitDefaultText!=self.srchLimitLabel.get_text():
            newtext = ',' + newtext
        self.srchLimitText="%s%s"%(self.srchLimitLabel.get_text(),newtext)
        self.srchLimitLabel.set_markup("<i>%s</i>"%self.srchLimitText)
        self.srchentry.set_text("")

    def reset_search (self, *args):
        debug("reset_search (self, *args):",5)
        self.srchLimitLabel.set_text(self.srchLimitDefaultText)
        self.srchLimitText=self.srchLimitDefaultText
        self.srchLimitBar.hide()
        self.searches = self.default_searches[0:]
        self.last_search={} # reset search so we redo it
        self.search()

    def get_rec_from_iter (self, iter):
        debug("get_rec_from_iter (self, iter): %s"%iter,5)
        obj=self.rectree.get_model().get_value(iter,0)
        retval=self.rd.get_rec(obj.id)
        return retval

    def rtree_time_edited_cb (self, renderer, path_string, text, colnum, attribute):
        if not text: secs = 0
        else:
            secs = self.rg.conv.timestring_to_seconds(text)
            if not secs:
                #self.message(_("Unable to recognize %s as a time."%text))
                return
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.rectree.get_model()
        iter = store.get_iter(path)
        #self.rmodel.set_value(iter,colnum,secs)
        rec = self.get_rec_from_iter(iter)
        if convert.seconds_to_timestring(getattr(rec,attribute))!=text:
            self.rd.undoable_modify_rec(rec,
                                        {attribute:secs},
                                        self.history,
                                        get_current_rec_method=lambda *args: self.get_selected_recs_from_rec_tree()[0],
                                        )
            self.update_modified_recipe(rec,attribute,secs)
        # Is this really stupid? I don't know, but I did it before so
        # perhaps I had a reason.
        #self.rmodel.row_changed(path,iter)
        self.rmodel.update_iter(iter)
        self.rd.save()

    def rtree_edited_cb (self, renderer, path_string, text, colnum, attribute):
        debug("rtree_edited_cb (self, renderer, path_string, text, colnum, attribute):",5)
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.rectree.get_model()
        iter = store.get_iter(path)
        if not iter: return
        #self.rmodel.set_value(iter, colnum, text)
        rec=self.get_rec_from_iter(iter)
        if attribute=='category':
            val = ", ".join(self.rd.get_cats(rec))
        else:
            val = "%s"%getattr(rec,attribute)
        if val!=text:
            # only bother with this if the value has actually changed!
            self.rd.undoable_modify_rec(rec,
                                        {attribute:text},
                                        self.history,
                                        get_current_rec_method=lambda *args: self.get_selected_recs_from_rec_tree()[0],
                                        )
            self.update_modified_recipe(rec,attribute,text)
        # for metakit, which isn't autocomitting very nicely...        
        #self.rmodel.row_changed(path,iter)
        self.rmodel.update_iter(iter)
        self.rd.save()

    def star_change_cb (self, value, model, treeiter, column_number):
        #itr = model.convert_iter_to_child_iter(None,treeiter)
        #self.rmodel.set_value(treeiter,column_number,value)
        rec = self.get_rec_from_iter(treeiter)
        if getattr(rec,'rating')!=value:
            self.rd.undoable_modify_rec(
                rec,
                {'rating':value},
                self.history,
                get_current_rec_method = lambda *args: self.get_selected_recs_from_rec_tree()[0],
                )
            #self.rmodel.row_changed(self.rmodel.get_path(treeiter),treeiter)
            self.rmodel.update_iter(treeiter)

    def update_modified_recipe(self,rec,attribute,text):
        """Update a modified recipe.

        Subclasses can use this to update other widgets duplicating
        the information in the index view."""
        pass

    def rec_tree_select_rec (self, *args):
        raise NotImplementedError

    def get_selected_recs_from_rec_tree (self):
        debug("get_selected_recs_from_rec_tree (self):",5)
        def foreach(model,path,iter,recs):
            debug("foreach(model,path,iter,recs):",5)
            try:
                recs.append(model[path][0])
                #recs.append(self.get_rec_from_iter(iter))
            except:
                debug("DEBUG: There was a problem with iter: %s path: %s"%(iter,path),1)
        recs=[]
        sel = self.rectree.get_selection()
        if sel:
            sel.selected_foreach(foreach,recs)
            return recs
        else:
            return []

    def selection_changedCB (self, *args):
        """We pass along true or false to selection_changed
        to say whether there is a selection or not."""
        debug("selection_changed (self, *args):",5)
        v=self.rectree.get_selection().get_selected_rows()[1]
        if v: selected=True
        else: selected=False
        self.selection_changed(v)

    def selection_changed (self, selected=False):
        """This is a way to act whenever the selection changes."""
        pass

    def visibility_fun (self, model, iter):
        try:
            if (model.get_value(iter,0) and
                not model.get_value(iter,0).deleted and
                model.get_value(iter, 0).id in self.visible):
                return True
            else: return False
        except:
            debug('something bizaare just happened in visibility_fun',1)
            return False

    def update_rmodel (self, recipe_table):
        self.rmodel.change_view(recipe_table)
        self.set_reccount()

class RecipeModel (pageable_store.PageableViewStore):
    """A ListStore to hold our recipes in 'pages' so we don't load our
    whole database at a time.
    """
    per_page = 12
    page = 0

    columns_and_types = [('rec',gobject.TYPE_PYOBJECT,),
                         ('thumb',gtk.gdk.Pixbuf),
                         ]
    for n in [r[0] for r in REC_ATTRS]:
        if n in INT_REC_ATTRS: columns_and_types.append((n,int))
        else: columns_and_types.append((n,str))
    
    columns = [c[0] for c in columns_and_types]
    column_types = [c[1] for c in columns_and_types]

    def __init__ (self, vw, rd, per_page=None):
        self.rd = rd
        pageable_store.PageableViewStore.__init__(self,
                                                  vw,
                                                  columns=self.columns,
                                                  column_types=self.column_types,
                                                  per_page=per_page)
        self.made_categories = False

    def _get_slice_ (self,bottom,top):
        try:
            return [[self._get_value_(r,col) for col in self.columns] for r in self.view[bottom:top]]
        except:
            print '_get_slice_ failed with',bottom,top
            raise

    def _get_value_ (self, row, attr):
        if attr=='category':
            cats = self.rd.get_cats(row)
            if cats: return ", ".join(cats)
            else: return ""
        elif attr=='rec':
            return row
        elif attr=='thumb':
            if row.thumb: return get_pixbuf_from_jpg(row.thumb)
            else: return None        
        elif attr in INT_REC_ATTRS:
            return getattr(row,attr) or 0
        else:
            val = getattr(row,attr)
            if val: return str(val)
            else: return None
        #else:
        #    
        #    return str(getattr(row,attr))

    def update_recipe (self, recipe):
        """Handed a recipe (or a recipe ID), we update its display if visible."""
        debug('Updating recipe %s'%recipe.title,3)
        if type(recipe)!=int: recipe=recipe.id # make recipe == id
        for n,row in enumerate(self):
            debug('Looking at row',3)
            if row[0].id==recipe:
                indx = int(n + (self.page * self.per_page))
                # update parent
                self.parent_list[indx] = self.rd.fetch_one(self.rd.recipe_table,
                                                           id=recipe)
                # update self
                self.update_iter(row.iter)
                debug('updated row -- breaking',3)
                break

    #def make_categories (self):
    #    # This is ugly, terrible, no good code. Among other things,
    #    # this is rather specifically metakit hackery which will have
    #    # to be reworked should another backend ever be implemented.
    #    #sorted_categories_table = self.rd.categories_table.sort('category')
    #    #if self.rd.__class__.__module__.find('rmetakit')>=0:
    #    #    for r in sorted_categories_table:
    #    #        if r and r.category:
    #    #            self.rd.modify_rec(r,
    #    #                               {'categoryname':r.category})
    #    #self.made_categories=True
