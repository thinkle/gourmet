#!/usr/bin/env python
import gtk.glade, gtk, time, re, gtk.gdk, gobject
import WidgetSaver, Undo, ratingWidget
from ImageExtras import get_pixbuf_from_jpg
import dialog_extras as de
import treeview_extras as te
import cb_extras as cb
import convert
from gglobals import *
from gdebug import debug
import mnemonic_manager
#import pageable_model
import pageable_store
from gettext import gettext as _
from gettext import ngettext

class RecIndex:
    """We handle the 'index view' of recipes, which puts
    a recipe model into a tree and allows it to be searched
    and sorted. We're a separate class from the main recipe
    program so that we can be created again (e.g. in the recSelector
    dialog called from a recipe card."""
    #def __init__ (self, model, glade, rd, rg, editable=False):
    def __init__ (self, glade, rd, rg, editable=False):
        #self.visible = 1 # can equal 1 or 2
        self.editable=editable
        self.rtcols=rg.rtcols
        self.rtcolsdic=rg.rtcolsdic
        self.rtwidgdic=rg.rtwidgdic
        self.prefs=rg.prefs
        self.glade = glade
        self.rd = rd
        self.rg = rg
        self.srchentry=self.glade.get_widget('rlistSearchbox')
	self.limitButton = self.glade.get_widget('rlAddButton')
        # Don't # allow for special keybindings
        #self.srchentry.connect('key_press_event',self.srchentry_keypressCB)
        self.searchByDic = {
            _('title'):'title',
            _('ingredient'):'ingredient',
            _('instructions'):'instructions',
            _('notes'):'modifications',
            _('category'):'category',
            _('cuisine'):'cuisine',
            #_('rating'):'rating',
            _('source'):'source',
            }
        self.searchByList = [_('title'),
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
        self.SEARCH_MENU_KEY = "b"
        self.srchLimitBar=self.glade.get_widget('srchLimitBar')
        self.srchLimitBar.hide()
        self.srchLimitLabel=self.glade.get_widget('srchLimitLabel')
        self.srchLimitClearButton = self.glade.get_widget('srchLimitClear')
        self.srchLimitText=self.srchLimitLabel.get_text()
        self.srchLimitDefaultText=self.srchLimitText
        self.searchButton = self.glade.get_widget('searchButton')
        self.rSearchByMenu = self.glade.get_widget('rlistSearchByMenu')
        cb.set_model_from_list(self.rSearchByMenu, self.searchByList)
        cb.setup_typeahead(self.rSearchByMenu)
        self.rSearchByMenu.set_active(0)
        self.rSearchByMenu.connect('changed',self.search_as_you_type)
        self.sautTog = self.glade.get_widget('searchAsYouTypeToggle')
        self.sautTog.connect('toggled',self.toggleTypeSearchCB)
        self.regexpTog = self.glade.get_widget('regexpTog')
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
            'rlistReset' : self.reset_search,
            'rlistLimit' : self.limit_search,
            'search_as_you_type_toggle' : self.toggleTypeSearchCB,})
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

    def setup_search_views (self):
        """Setup our views of the database."""
        self.lsrch = ["",""]
        self.lsrchvw = self.rd.rview.select(deleted=False)
        self.searchvw = self.rd.rview.select(deleted=False)

    def make_rec_visible (self, *args):
        """Make sure recipe REC shows up in our index."""
        #if not self.rg.wait_to_filter:
        self.setup_search_views()
        #self.reset_search()
        self.redo_search()
        #debug('make_rec_visible',0)
        #self.visible.append(rec.id)
        #if not self.rg.wait_to_filter:
        #    self.rmodel_filter.refilter()
    
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

    def create_rmodel (self, vw):
        self.rmodel = RecipeModel(vw,self.rd,per_page=self.prefs.get('recipes_per_page',12))
    
    def setup_rectree (self):
        """Create our recipe treemodel."""
        self.create_rmodel(self.lsrchvw)
        self.rmodel.connect('page-changed',self.rmodel_page_changed_cb)
        self.rmodel.connect('view-changed',self.rmodel_page_changed_cb)
        # and call our handler once to update our prev/next buttons + label
        self.rmodel_page_changed_cb(self.rmodel)
        # and hook up our model
        self.rectree.set_model(self.rmodel)
        self.rectree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.selection_changed()
        self.set_reccount()
        self.setup_reccolumns()
        # this has to come after columns are added or else adding columns resets out column order!
        self.rectree_conf=te.TreeViewConf(self.rectree,
                                          hidden=self.prefs.get('rectree_hidden_columns',[]),
                                          order=self.prefs.get('rectree_column_order',{}))
        self.rectree_conf.apply_column_order()
        self.rectree_conf.apply_visibility()
        #self.rectree.connect("row-activated",self.recTreeSelectRec)#self.recTreeSelectRec)
        self.rectree.get_selection().connect("changed",self.selection_changedCB)
        self.rectree.expand_all()
        self.rectree.show()

    def set_reccount (self, *args):
        """Display the count of currently visible recipes."""
        debug("set_reccount (self, *args):",5)
        self.count = len(self.lsrchvw)
        #self.stat.push(self.contid,_("%s Recipes")%self.count)
        bottom,top,total = self.rmodel.showing()
        if top >= total and bottom==1:
            lab = ngettext('%s recipe','%s recipes',top)%top
        else:
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
                    map(lambda i: model.append([i]),self.rg.rd.get_unique_values(c,self.rg.rd.catview)
                        )
                else:
                    map(lambda i: model.append([i]),self.rg.rd.get_unique_values(c))
                renderer.set_property('model',model)
                renderer.set_property('text-column',0)
            else:
                renderer = gtk.CellRendererText()
            renderer.set_property('editable',self.editable)
            renderer.connect('edited',self.rtree_edited_cb,n, c)
            titl = self.rtcolsdic[c]
            col = gtk.TreeViewColumn('_%s'%titl,renderer, text=n)
            col.set_reorderable(True)
            col.set_resizable(True)
            #col.set_clickable(True)
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
        if widget.get_active():
            self.message('Advanced searching (regular expressions) turned on')
        else:
            self.message('Advanced searching off')

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
        debug('set_search_by',0)
        #self.rSearchByMenu.get_children()[0].set_text(str)
        cb.cb_set_active_text(self.rSearchByMenu, str)
        self.search()

    def redo_search (self, *args):
        self.lsrch = ['','']
        self.search()
    
    def search (self, *args):
        debug("search (self, *args):",5)
        txt = self.srchentry.get_text()
        searchBy = cb.cb_get_active_text(self.rSearchByMenu)
        searchBy = self.searchByDic[unicode(searchBy)]
	if txt and self.limitButton: self.limitButton.set_sensitive(True)
        elif self.limitButton: self.limitButton.set_sensitive(False)
        if [txt, searchBy] == self.lsrch:
            debug("Same search!",0)
            return
        if self.srchentry.window: self.srchentry.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        gobject.idle_add(lambda *args: self.do_search(txt, searchBy))
        
    def do_search (self, txt, searchBy):
        ## first -- are we a continuation of the previous search of not?
        debug('do_search called with txt=%s, searchBy=%s'%(txt,searchBy),5)
        # if we're not using regular expressions, we escape our text.        
        addedtextp = re.match("^%s"%re.escape(txt),self.lsrch[0]) and len(txt) > len(self.lsrch[0])
        samesearchp = self.lsrch and searchBy == self.lsrch[1]
        if not addedtextp or not samesearchp:
            # if we're not, we reset our lsrchvw (our searchvw)
            self.lsrchvw = self.searchvw
        if txt:
            if searchBy == "ingredient":
                # somewhat counterintuitive behavior (google-like search)
                #self.lsrchvw=self.rd.ings_search(txt.split(),rview=self.lsrchvw)
                # less counterintuitive (exact search)
                self.lsrchvw=self.rd.ing_search(txt,rview=self.lsrchvw,use_regexp=self.regexpp())
            elif searchBy == 'category':
                self.lsrchvw=self.rd.joined_search(self.lsrchvw,self.rd.catview,'category',txt,
                                                   use_regexp=self.regexpp())
            else:
                self.lsrchvw=self.rd.search(self.lsrchvw,searchBy,txt,use_regexp=self.regexpp())            
        else:
            self.lsrchvw = self.searchvw
        self.lsrch = [txt, searchBy]
        self.update_rmodel(self.lsrchvw)
        self.set_reccount()
        self.srchentry.window.set_cursor(None)

    def limit_search (self, *args):
        debug("limit_search (self, *args):",5)
        self.search() # make sure we've done the search...
        self.searchvw=self.lsrchvw
        self.srchLimitBar.show()
        if self.srchLimitDefaultText==self.srchLimitText:
            newtext=_(" %s contains %s")%(self.lsrch[1],self.lsrch[0])
        else:
            newtext=_(", %s contains %s")%(self.lsrch[1],self.lsrch[0])
        self.srchLimitText="%s%s"%(self.srchLimitLabel.get_text(),newtext)
        self.srchLimitLabel.set_markup("<i>%s</i>"%self.srchLimitText)
        self.srchentry.set_text("")

    def reset_search (self, *args):
        debug("reset_search (self, *args):",5)
        self.srchLimitLabel.set_text(self.srchLimitDefaultText)
        self.srchLimitText=self.srchLimitDefaultText
        self.srchLimitBar.hide()
        self.searchvw=self.rd.rview
        self.lsrch=["",""] # reset search so we redo it
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
                self.message(_("Unable to recognize %s as a time."%text))
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
                                        get_current_rec_method=lambda *args: self.recTreeSelectedRecs()[0],
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
                                        get_current_rec_method=lambda *args: self.recTreeSelectedRecs()[0],
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
                get_current_rec_method = lambda *args: self.recTreeSelectedRecs()[0],
                )
            #self.rmodel.row_changed(self.rmodel.get_path(treeiter),treeiter)
            self.rmodel.update_iter(treeiter)

    def update_modified_recipe(self,rec,attribute,text):
        """Update a modified recipe.

        Subclasses can use this to update other widgets duplicating
        the information in the index view."""
        pass

    def recTreeSelectedRecs (self):
        debug("recTreeSelectedRecs (self):",5)
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
            debug('something bizaare just happened in visibility_fun',0)
            return False
 
    def update_rmodel (self, rview):
        self.rmodel.change_view(rview)


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
        return [[self._get_value_(r,col) for col in self.columns] for r in self.view[bottom:top]]        

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
            return getattr(row,attr)
        else:
            return str(getattr(row,attr))

    def sort (self,*args,**kwargs):
        if not self.made_categories:
            self.make_categories()
        return pageable_store.PageableViewStore.sort(self,*args,**kwargs)

    def _do_sort_ (self):
        if 'category' in self.__all_sorts__:
            indx = self.__all_sorts__.index('category')
            self.__all_sorts__ = self.__all_sorts__[0:indx] + \
                                 ['categoryname'] + \
                                 self.__all_sorts__[indx+1:]
        if 'category' in self.__reverse_sorts__:
            indx = self.__reverse_sorts__.index('category')
            self.__reverse_sorts__ = self.__reverse_sorts__[0:indx] + \
                                 ['categoryname'] + \
                                 self.__reverse_sorts__[indx+1:]
        pageable_store.PageableViewStore._do_sort_(self)

    def update_recipe (self, recipe):
        """Handed a recipe (or a recipe ID), we update its display if visible."""
        if type(recipe)!=int: recipe=recipe.id # make recipe == id
        #print 'updating ',recipe
        for row in self:
            #print 'row=',row
            if row[0].id==recipe:
                #print 'update!'
                self.update_iter(row.iter)
                break

    def make_categories (self):
        # This is ugly, terrible, no good code. Among other things,
        # this is rather specifically metakit hackery which will have
        # to be reworked should another backend ever be implemented.
        sorted_catview = self.rd.catview.sort('category')
        for r in sorted_catview:
            #print r,r.id,r.category
            #print 'selecting recipe'
            #rec = self.rd.get_rec(r.id)
            #print 'rec becomes->',rec
            if r and r.category:
                #print 'setting categoryname'
                self.rd.modify_rec(r,
                                   {'categoryname':r.category})
                #rec[0].categoryname=r.category
        #print 'done making categories!'
        self.made_categories=True
