#!/usr/bin/env python
import gtk.glade, gtk, time, re, gtk.gdk 
import WidgetSaver, Undo
import dialog_extras as de
import treeview_extras as te
import cb_extras as cb
from gglobals import *
from gdebug import debug

class RecIndex:
    """We handle the 'index view' of recipes, which puts
    a recipe model into a tree and allows it to be searched
    and sorted. We're a separate class from the main recipe
    program so that we can be created again (e.g. in the recSelector
    dialog called from a recipe card."""
    def __init__ (self, model, glade, rd, rg, visible=1):
        self.visible = 1 # can equal 1 or 2
        self.rtcols=rg.rtcols
        self.rtcolsdic=rg.rtcolsdic
        self.prefs=rg.prefs
        self.glade = glade
        self.rmodel = model
        self.rd = rd
        self.rg = rg
        self.srchentry=self.glade.get_widget('rlistSearchbox')
	self.limitButton = self.glade.get_widget('rlAddButton')
        # allow for special keybindings
        self.srchentry.connect('key_press_event',self.srchentry_keypressCB)
        self.searchByDic = {
            _('title'):'title',
            _('ingredient'):'ingredient',
            _('category'):'category',
            _('cuisine'):'cuisine',
            _('rating'):'rating',
            _('source'):'source',
            }
        print self.searchByDic
        self.searchByList = [_('title'),_('ingredient'),_('category'),_('cuisine'),_('rating'),_('source')]
        self.SEARCH_KEY_DICT = {
            "t":_("title"),
            "i":_("ingredient"),
            "c":_("category"),
            "u":_("cuisine"),
            "r":_("rating"),
            's':_("source"),
            }
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
        self.sautTog = self.glade.get_widget('searchAsYouTypeToggle')
        self.sautTog.connect('toggled',self.toggleTypeSearchCB)
        self.regexpTog = self.glade.get_widget('regexpTog')
        self.rectree = self.glade.get_widget('recTree')
        self.rectree.connect('start-interactive-search',lambda *args: self.srchentry.grab_focus())
        self.stat = self.glade.get_widget('statusbar')
        self.contid = self.stat.get_context_id('main')
        self.lsrch = ["",""]
        self.lsrchvw = self.rd.rview
        self.searchvw = self.rd.rview
        self.setup_rectree()
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
        # lastly, this seems to be necessary to get updates
        # to show up accurately...
        self.rd.add_hooks.append(self.make_rec_visible)
        # and we update our count with each new recipe!
        self.rd.add_hooks.append(self.set_reccount)
        # and we update our count with each deletion.
        self.rd.delete_hooks.append(self.set_reccount)
        self.rd.modify_hooks.append(self.update_reccards)
        # setup a history
        self.uim=self.glade.get_widget('undo_menu_item')
        self.rim=self.glade.get_widget('redo_menu_item')
        self.raim=self.glade.get_widget('reapply_menu_item')
        self.history = Undo.UndoHistoryList(self.uim,self.rim,self.raim)

    def srchentry_keypressCB (self, widget, event):
        if event.state==gtk.gdk.MOD1_MASK:
            if self.SEARCH_KEY_DICT.has_key(event.string):
                self.set_search_by(self.SEARCH_KEY_DICT[event.string])
            elif self.SEARCH_MENU_KEY == event.string:
                self.rSearchByMenu.popup()

    def make_rec_visible (self, rec):
        debug('make_rec_visible',0)
        self.visible.append(rec.id)
        if not self.rg.wait_to_filter:
            self.rmodel_filter.refilter()
    
    def setup_rectree (self):
        self.rmodel_filter = self.rmodel.filter_new()
        #self.rmodel_filter.set_modify_func(types, self.add_recipe_attr)
        # we allow filtering for searches...
        self.visible = map(lambda x: x.id, self.rd.rview)
        # visibility_fun checks to see if the Rec ID is in self.visible
        self.rmodel_filter.set_visible_func(self.visibility_fun)
        # make sortable...
        self.rmodel_sortable = gtk.TreeModelSort(self.rmodel_filter)
        self.rectree.set_model(self.rmodel_sortable)
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
        debug("set_reccount (self, *args):",5)
        self.count = len(self.lsrchvw)
        self.stat.push(self.contid,_("%s Recipes")%self.count)
        if self.count == 1:
            self.rectree.get_selection().select_path((0,))

    def setup_reccolumns (self):
        renderer = gtk.CellRendererPixbuf()
        col = gtk.TreeViewColumn("",renderer,pixbuf=1)
        self.rectree.append_column(col)
        n = 2
        for c in self.rtcols:
            renderer = gtk.CellRendererText()
            renderer.set_property('editable',gtk.TRUE)
            renderer.connect('edited',self.rtree_edited_cb,n, c)
            titl = self.rtcolsdic[c]
            col = gtk.TreeViewColumn(titl,renderer, text=n)
            col.set_reorderable(gtk.TRUE)
            col.set_resizable(gtk.TRUE)
            #col.set_clickable(gtk.TRUE)
            #col.connect('clicked', self.column_sort)
            self.rectree.append_column(col)
            col.set_sort_column_id(n)
            debug("Column %s is %s->%s"%(n,c,self.rtcolsdic[c]),5)
            n += 1

    def toggleTypeSearchCB (self, widget):
        if widget.get_active():
            self.search_as_you_type=True
            self.searchButton.hide()
        else:
            self.search_as_you_type=False
            self.searchButton.show()

    def toggleRegexpCB (self, widget):
        if widget.get_active():
            self.message('Advanced searching (regular expressions) turned on')
        else:
            self.message('Advanced searching off')

    def regexpp (self):
        if self.regexpTog.get_active():
            return True
        else:
            return False

    def search_as_you_type (self, *args):
        if self.search_as_you_type:
            self.search()

    def set_search_by (self, str):
        """Manually set the search by label to str"""
        debug('set_search_by',0)
        #self.rSearchByMenu.get_children()[0].set_text(str)
        cb.cb_set_active_text(self.rSearchByMenu, str)
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
        gtk.idle_add(lambda *args: self.do_search(txt, searchBy))
        
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

    def rtree_edited_cb (self, renderer, path_string, text, colnum, attribute):
        debug("rtree_edited_cb (self, renderer, path_string, text, colnum, attribute):",5)
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.rectree.get_model()
        iter = store.get_iter(path)
        self.rmodel.set_value(iter, colnum, text)
        rec=self.get_rec_from_iter(iter)
        #self.rd.modify_rec(rec,{attribute:text})
        self.rd.undoable_modify_rec(rec,{attribute:text},self.history,
                                 get_current_rec_method=lambda *args: self.recTreeSelectedRecs()[0],
                                 )
        # for metakit, which isn't automitting very nicely...
        self.rd.save()

    def update_reccards (self, rec):
        if self.rc.has_key(rec.id):
            rc=self.rc[rec.id]
            rc.updateRecipe(rec,show=False)
            self.updateViewMenu()

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
        self.rectree.get_selection().selected_foreach(foreach,recs)
        return recs

    def selection_changedCB (self, *args):
        """We pass along true or false to selection_changed
        to say whether there is a selection or not."""
        debug("selection_changed (self, *args):",5)
        v=self.rectree.get_selection().get_selected_rows()[1]
        if v: selected=gtk.TRUE
        else: selected=gtk.FALSE
        self.selection_changed(v)

    def selection_changed (self, selected=False):
        """This is a way to act whenever the selection changes."""
        pass

    def visibility_fun (self, model, iter):
        if (model.get_value(iter,0) and
            not model.get_value(iter,0).deleted and
            model.get_value(iter, 0).id in self.visible):
            return True
        else: return False
 
    def update_rmodel (self, rview):
        debug('update_rmodel... changing filtering criteria',0)
        self.visible = map(lambda r: r.id, rview)
        debug('visible=%s'%self.visible,0)
        debug('refiltering')
        self.rmodel_filter.refilter()
        debug('update_rmodel finished')


