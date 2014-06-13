from gourmet.ImageExtras import get_pixbuf_from_jpg
from gourmet.gdebug import debug
from gourmet.gglobals import REC_ATTRS, INT_REC_ATTRS, DEFAULT_HIDDEN_COLUMNS
from gourmet.gtk_extras import WidgetSaver, ratingWidget, cb_extras as cb, \
    mnemonic_manager, pageable_store, treeview_extras as te
from gourmet.models import Recipe, Category
from gourmet.models.meta import Session
from gourmet import convert
from gourmet import Undo

from gettext import gettext as _, ngettext
import gobject
import gtk
import gtk.gdk
import pango

def paginate(model, it, interval):
    lower, upper = interval
    return lower <= model.get_path(it)[0] < upper

def page(n, per_page):
    return n * per_page, (n+1) * per_page

class RecIndex:
    """We handle the 'index view' of recipes, which puts
    a recipe model into a tree and allows it to be searched
    and sorted. We're a separate class from the main recipe
    program so that we can be created again (e.g. in the recSelector
    dialog called from a recipe card."""

    default_searches = [{'column':'deleted','operator':'=','search':False}]
    
    def __init__ (self, ui, rd, rg, editable=False, session=Session()):
        #self.visible = 1 # can equal 1 or 2
        self.editable=editable
        self.selected = True        
        self.rtcols=rg.rtcols
        self.rtcolsdic=rg.rtcolsdic
        self.rtwidgdic=rg.rtwidgdic
        self.prefs=rg.prefs
        self.ui = ui
        self.rd = rd
        self.rg = rg
        self.session = session
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
        self.per_page = self.prefs.get('recipes_per_page',12)
        self.page = 0
        self.srchentry=self.ui.get_object('rlistSearchbox')
        self.limitButton = self.ui.get_object('rlAddButton')
        # Don't # allow for special keybindings
        #self.srchentry.connect('key_press_event',self.srchentry_keypressCB)        
        self.SEARCH_MENU_KEY = "b"
        self.srchLimitBar = self.ui.get_object('srchLimitBar')
        assert(self.srchLimitBar)
        self.srchLimitBar.hide()
        self.srchLimitLabel=self.ui.get_object('srchLimitLabel')
        self.srchLimitClearButton = self.ui.get_object('srchLimitClear')
        self.srchLimitText=self.srchLimitLabel.get_text()
        self.srchLimitDefaultText=self.srchLimitText
        self.searchButton = self.ui.get_object('searchButton')
        self.rSearchByMenu = self.ui.get_object('rlistSearchByMenu')
        cb.set_model_from_list(self.rSearchByMenu, self.searchByList, expand=False)
        cb.setup_typeahead(self.rSearchByMenu)
        self.rSearchByMenu.set_active(0)
        self.rSearchByMenu.connect('changed',self.search_as_you_type)
        self.sautTog = self.ui.get_object('searchAsYouTypeToggle')
        self.search_actions.get_action('toggleSearchAsYouType').connect_proxy(self.sautTog)
        self.regexpTog = self.ui.get_object('regexpTog')
        self.searchOptionsBox = self.ui.get_object('searchOptionsBox')
        self.search_actions.get_action('toggleShowSearchOptions').connect_proxy(
            self.ui.get_object('searchOptionsToggle')
            )
        self.search_actions.get_action('toggleRegexp').connect_proxy(self.regexpTog)
        self.rectree = self.ui.get_object('recTree')
        self.sw = self.ui.get_object('scrolledwindow')
        self.rectree.connect('start-interactive-search',lambda *args: self.srchentry.grab_focus())
        self.prev_button = self.ui.get_object('prevButton')
        self.next_button = self.ui.get_object('nextButton')
        self.first_button = self.ui.get_object('firstButton')
        self.last_button = self.ui.get_object('lastButton')        
        self.showing_label = self.ui.get_object('showingLabel')
        self.stat = self.ui.get_object('statusbar')
        self.contid = self.stat.get_context_id('main')
        self.setup_search_views()
        self.setup_rectree()
        self.prev_button.connect('clicked',lambda *args: self.update_page(self.page - 1))
        self.next_button.connect('clicked',lambda *args: self.update_page(self.page + 1))
        self.first_button.connect('clicked',lambda *args: self.update_page(0))
        self.last_button.connect('clicked',lambda *args: self.update_page(self.get_last_page()))
        self.ui.connect_signals({
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
        self.uim=self.ui.get_object('undo_menu_item')
        self.rim=self.ui.get_object('redo_menu_item')
        self.raim=self.ui.get_object('reapply_menu_item')
        self.history = Undo.UndoHistoryList(self.uim,self.rim,self.raim)
        # Fix up our mnemonics with some heavenly magic
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.sacred_cows.append("search for") # Don't touch _Search for:
        self.mm.add_builder(self.ui)
        self.mm.add_treeview(self.rectree)
        self.mm.fix_conflicts_peacefully()
        self.page_changed_cb()

    def update_page(self, n=0):
        self.page = n
        self.bottom, self.top = page(self.page, self.per_page)
        self.recipes_on_page = self.all_recipes.filter_new()
        self.recipes_on_page.set_visible_func(paginate, (self.bottom, self.top))
        self.rectree.set_model(self.recipes_on_page)
        self.page_changed_cb()

    def get_last_page (self):
        """Return the number of our last page."""
        pages = (self.count / self.per_page) - 1
        if self.count % self.per_page: pages+=1
        return pages

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
        self.search_ng = self.session.query(Recipe).filter_by(deleted=False)
        self.sort_by = []
        self.rvw = self.session.query(Recipe).filter_by(deleted=False).all() #self.rd.search_recipes(self.searches,sort_by=self.sort_by)

    def make_rec_visible (self, *args):
        """Make sure recipe REC shows up in our index."""
        #if not self.rg.wait_to_filter:
        #self.setup_search_views()
        self.redo_search()
        #debug('make_rec_visible',0)
        #self.visible.append(rec.id)
        #if not self.rg.wait_to_filter:
        #    self.recipes_on_page_filter.refilter()

    def search_entry_activate_cb (self, *args):
        if self.recipes_on_page._get_length_()==1:
            self.rec_tree_select_rec()
        elif self.srchentry.get_text():
            if not self.search_as_you_type:
                self.search()
                gobject.idle_add(lambda *args: self.limit_search())
            else:
                self.limit_search()
    
    def page_changed_cb (self):
        if self.page==0:
            self.prev_button.set_sensitive(False)
            self.first_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)
            self.first_button.set_sensitive(True)
        if self.page==self.get_last_page():
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
        self.all_recipes = pageable_store.SqlaModel(Recipe, vw)
        self.count = self.all_recipes.iter_n_children(None)
        self.update_page()
    
    def setup_rectree (self):
        """Create our recipe treemodel."""
        self.create_rmodel(self.rvw)
#        self.recipes_on_page.connect('page-changed',self.recipes_on_page_page_changed_cb)
#        self.recipes_on_page.connect('view-changed',self.recipes_on_page_page_changed_cb)
#        self.recipes_on_page.connect('view-sort',self.recipes_on_page_sort_cb)
        # and call our handler once to update our prev/next buttons + label
        #self.recipes_on_page_page_changed_cb(self.recipes_on_page)
        self.rectree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.selection_changed()
        self.setup_reccolumns()
        # this has to come after columns are added or else adding columns resets out column order!
        self.rectree_conf=te.TreeViewConf(self.rectree,
                                          hidden=self.prefs.get('rectree_hidden_columns',DEFAULT_HIDDEN_COLUMNS),
                                          order=self.prefs.get('rectree_column_order',{}))
        self.rectree_conf.apply_column_order()
        self.rectree_conf.apply_visibility()
        self.rectree.connect("row-activated",self.rec_tree_select_rec)
        self.rectree.connect('key-press-event',self.tree_keypress_cb)        
        self.rectree.get_selection().connect("changed",self.selection_changedCB)
        self.rectree.set_property('rules-hint',True) # stripes!
        self.rectree.expand_all()
        self.rectree.show()

    def set_reccount (self, *args):
        """Display the count of currently visible recipes."""
        debug("set_reccount (self, *args):",5)
        if self.top >= self.count and self.bottom==1:
            lab = ngettext('%s recipe','%s recipes',self.top)%self.top
            for b in self.first_button,self.prev_button,self.next_button,self.last_button:
                b.hide()
        else:
            for b in self.first_button,self.prev_button,self.next_button,self.last_button:
                b.show()
            bottom = self.bottom+1
            top = min(self.top, self.count)
            total = self.count
            # Do not translate bottom, top and total -- I use these fancy formatting
            # strings in case your language needs the order changed!
            lab = _('Showing recipes %(bottom)s to %(top)s of %(total)s')%locals()
        self.showing_label.set_markup('<i>' + lab + '</i>')
        if self.count == 1:
            sel = self.rectree.get_selection()
            if sel: sel.select_path((0,))

    def setup_reccolumns (self):
        """Setup the columns of our recipe index TreeView"""
        renderer = gtk.CellRendererPixbuf()
        cssu=pageable_store.ColumnSortSetterUpper(self.recipes_on_page)
        col = gtk.TreeViewColumn("", renderer)

        def data_fun (col,renderer,mod,itr):
            thumb = mod.get_value(itr, self.all_recipes.get_column_index('thumb'))
            if thumb:
                renderer.set_property('pixbuf', get_pixbuf_from_jpg(thumb))
            else:
                renderer.set_property('pixbuf', None)

        col.set_cell_data_func(renderer, data_fun)
        col.set_min_width(-1)
        self.rectree.append_column(col)
        _title_to_num_ = {}
        for c in self.rtcols:
            if c == 'category':
                n = self.all_recipes.get_column_index('categories_string')
            else:
                n = self.all_recipes.get_column_index(c)

            if c=='rating':
                # special case -- for ratings we set up our lovely
                # star widget
                twsm = ratingWidget.TreeWithStarMaker(
                    self.rectree,
                    self.rg.star_generator,
                    data_col=n,
                    col_title='_%s'%self.rtcolsdic[c],
                    handlers=[],
                    properties={'reorderable':True,
                                'resizable':True},
                    )
                cssu.set_sort_column_id(twsm.col,twsm.data_col)
                twsm.col.set_min_width(110)
                continue
            # And we also special case our time column
            elif c in ['preptime','cooktime']:
                _title_to_num_[self.rtcolsdic[c]]=n
                renderer=gtk.CellRendererText()
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
                continue
            else:
                renderer = gtk.CellRendererText()
                if c=='link':
                    renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
                else:
                    renderer.get_property('wrap-width')
                    renderer.set_property('wrap-mode',pango.WRAP_WORD)
                    if c == 'title': renderer.set_property('wrap-width',200)
                    else: renderer.set_property('wrap-width',150)
            if c in self.rtcolsdic:
                titl = self.rtcolsdic[c]
            else:
                titl = "N/A"
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
            #debug("Column %s is %s->%s"%(n,c,self.rtcolsdic[c]),5)

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
        if self.limitButton: self.limitButton.set_sensitive(txt!='')
        if self.make_search_dic(txt,searchBy) == self.last_search:
            debug("Same search!",1)
            return
        # Get window
        if self.srchentry:
            parent = self.srchentry.parent
            while parent and not (isinstance(parent,gtk.Window)):
                parent = parent.parent
            parent.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
            debug('Doing new search for %s, last search was %s'%(self.make_search_dic(txt,searchBy),self.last_search),1)
            gobject.idle_add(lambda *args: (self.do_search(txt, searchBy) or parent.window.set_cursor(None)))
        else:
            gobject.idle_add(lambda *args: self.do_search(txt, searchBy))

    def make_search_dic (self, txt, searchBy):
        srch = {'column':searchBy}
        if self.regexpp():
            srch['operator'] = 'REGEXP'
            srch['search'] = txt.replace(' %s '%_('or'), # or operator for searches
                                         '|')
        else:
            srch['operator']='LIKE'
            srch['search'] = '%' + txt.replace('%','%%')+'%'
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

    def tree_keypress_cb (self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname in ['Page_Up','Page_Down']:
            sb = self.sw.get_vscrollbar()
            adj =  self.sw.get_vscrollbar().get_adjustment() 
            val = adj.get_value(); upper = adj.get_upper()
            if keyname == 'Page_Up':
                if val > 0:
                    return None
                if self.page > 0:
                    self.update_page(self.page-1)
                sb.set_value(upper)
                return True
            if keyname == 'Page_Down':
                if val < (upper - adj.page_size):
                    return None
                if self.page < self.get_last_page():
                    self.update_page(self.page+1)
                sb.set_value(0)
                return True
        if keyname == 'Home':
            self.update_page(0)
            self.sw.get_vscrollbar().set_value(0)
            return True            
        if keyname == 'End':
            self.update_page(self.get_last_page())
            sb = self.sw.get_vscrollbar()
            sb.set_value(sb.get_adjustment().get_upper())
            return True

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
            recs.append(model.get_value(iter, 0))

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
        self.recipes_on_page.change_view(recipe_table)
        self.set_reccount()


class ListWrapper(gobject.GObject):
    def __init__(self, mylist):
        self.mylist = mylist

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

    #columns_and_types.append(('ingredients',ListWrapper))
    #columns_and_types.append(('categories',ListWrapper))
    #columns_and_types.append(('categories_string',str))
    
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
