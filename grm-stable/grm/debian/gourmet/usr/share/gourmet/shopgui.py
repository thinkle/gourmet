 #!/usr/bin/env python
import gtk.glade, gtk, gobject, pango, sys, os.path, time, os, string
import recipeManager, convert, WidgetSaver, reccard
import dialog_extras as de
import treeview_extras as te
import exporters.printer as printer
from gdebug import *
from gglobals import *
from gettext import gettext as _
from nutrition.nutritionLabel import NutritionLabel
from nutrition.nutrition import NutritionInfoList
from FauxActionGroups import ActionManager
import mnemonic_manager

class ShopGui (ActionManager):
    """A class to manage our shopping window."""
    def __init__ (self, RecGui, conv=None):
        debug("__init__ (self, RecGui):",5)
        self.glade = gtk.glade.XML(os.path.join(gladebase,'shopList.glade'))
        self.init_action_manager()
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.add_glade(self.glade)
        self.mm.fix_conflicts_peacefully()
        self.conv=conv
        self.rg = RecGui
        self.nd = self.rg.nd # convenient reference to our nutrition
        self.recs = {}
        self.extras = []
        self.data,self.pantry=self.grabIngsFromRecs([])
        self.setup_popup()
        self.create_slTree(self.data)
        self.create_pTree(self.pantry)
        self.create_rtree()
        ## We need to keep track of including/excluding options...
        ## Here's our solution: we have a dictionary where we can lookg
        ## up ingredients by recipe by key
        ## {'recipe_id' : {'key1' : False
        ##                 'key2  : True}} ... where true and false mean include/exclude
        self.includes = {}
        self.widget = self.glade.get_widget('shopList')
        self.stat = self.glade.get_widget('statusbar1')
        self.contid = self.stat.get_context_id('main')
        self.conf = [] #WidgetSavers...
        self.conf.append(WidgetSaver.WindowSaver(self.widget,
                                            self.rg.prefs.get('shopGuiWin',{}),
                                                 show=False))
        panes = ['vpaned1','hpaned1']
        for p in panes:
            w=self.glade.get_widget(p)
            self.conf.append(WidgetSaver.WidgetSaver(
                w,
                self.rg.prefs.get('shop%s'%p,{'position':w.get_position()})
                ))
        self.setup_shop_dialog()
        self.glade.signal_autoconnect({
            'shopHide' : self.hide,
            'shopSave' : self.save,
            'shopPrint' : self.printList,
            'shopClear' : self.clear,
            'move_to_shopping' : self.rem_selection_from_pantry,
            'move_to_pantry' : self.add_selection_to_pantry,
            'show_help': lambda *args: de.show_faq(HELP_FILE,jump_to='Shopping'),
            'show_nutritional_info': self.show_nutritional_info,
            })

    def init_action_manager (self):
        ActionManager.__init__(
            self,self.glade,
            {'shopGroup':[{'shopRemove':[{'tooltip':_('Move selected items from shopping list to "pantry" list. You can also move items by dragging and dropping.')},
                                         # widgets
                                         ['moveToPantryButton',
                                          'remove_from_shopping_list_menuitem',
                                          'add_to_pantry_popup_menuitem',
                                          ],
                                         ]},
                          {'pantryRemove':[{'tooltip':_('Move selected items back to the shopping list. You can also move items by dragging and dropping.')},
                                           # widgets
                                           ['moveToShoppingListButton',
                                            'add_to_sl_popup_menuitem',
                                            'return_to_shopping_menuitem',
                                            ]],
                           }                 
                          ],
             },
            # callbacks
            [('pantryRemove',self.rem_selection_from_pantry),
             ('shopRemove',self.add_selection_to_pantry),
             ])

    def create_rtree (self):
        debug("create_rtree (self):",5)
        self.rmodel = self.create_rmodel()
        #self.rectree = gtk.TreeView(self.rmodel)
        self.rectree = self.glade.get_widget('shopRTree')
        self.glade.signal_connect('ingmen_pantry',self.add_selection_to_pantry)
        self.glade.signal_connect('panmen_remove',self.rem_selection_from_pantry)        
        self.rectree.set_model(self.rmodel)
        renderer = gtk.CellRendererText()

        #renderer.set_property('editable',True)
        #renderer.connect('edited',tst)
        titl = gtk.TreeViewColumn(_("Title"),renderer,text=1)
        mult = gtk.TreeViewColumn(_("x"),renderer,text=2)
        self.rectree.append_column(titl)
        self.rectree.append_column(mult)
        titl.set_resizable(True)
        titl.set_clickable(True)
        titl.set_reorderable(True)
        mult.set_resizable(True)
        mult.set_clickable(True)
        mult.set_reorderable(True)
        self.rectree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.rectree.show()
        
    def create_rmodel (self):
        debug("create_rmodel (self):",5)
        mod = gtk.TreeStore(gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_STRING)
        for r,mult in self.recs.values():
            iter = mod.append(None)
            mod.set_value(iter,0,r)
            mod.set_value(iter,1,r.title)
            mod.set_value(iter,2,convert.float_to_frac(mult))
        return mod

    def show_nutritional_info (self, *args):
        """Show nutritional information for this shopping list.
        """
        nl = NutritionLabel(self.rg.prefs,
                            custom_label=_('Nutritional Information for Shopping List')
                            )
        ings = []
        for d in [self.sh.dic,self.sh.mypantry]:
            for k,units in d.items():
                for a,u in units:
                    ings.append([k,a,u])
        nutinfo = NutritionInfoList(
            [self.nd.get_nutinfo_for_item(*i) for i in ings]
            )
        nl.set_nutinfo(nutinfo)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(nl)
        sw.show(); nl.show()
        md = de.ModalDialog(title=_("Nutritional Information for Shopping List"),modal=False)
        md.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        md.vbox.pack_start(sw,fill=True,expand=True)
        md.set_default_size(600,500)
        nl.show()
        md.show()

    def save (self, *args):
        debug("save (self, *args):",5)
        self.message('Saving')
        self.doSave(de.select_file(_("Save Shopping List As..."),
                                   filename=os.path.join(os.path.expanduser("~"),
                                                         "%s %s"%(_('Shopping List'),
                                                                  time.strftime("%x").replace("/","-"),
                                                                  )),
                                   action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                   ))
        self.message(_('Saved!'))
        
    def doSave (self, filename):
        debug("doSave (self, filename):",5)
        #of = open(filename,'w')
        #self.writeHeader(of,)
        #self.sh.pretty_print(of)
        #self.doTextPrint(of)
        #of.close()
        import exporters.lprprinter
        self._printList(exporters.lprprinter.SimpleWriter,file=filename,show_dialog=False)

    def printList (self, *args):
        debug("printList (self, *args):",0)
        self._printList(printer.SimpleWriter,dialog_parent=self.widget)
        
    def _printList (self, printer, *args, **kwargs):
        w = printer(*args,**kwargs)
        w.write_header(_("Shopping list for %s")%time.strftime("%x"))
        w.write_subheader(_("For the following recipes:"))
        for r,mult in self.recs.values():
            itm = "%s"%r.title
            if mult != 1:
                itm += _(" x%s")%mult
            w.write_paragraph(itm)
        write_itm = lambda a,i: w.write_paragraph("%s %s"%(a,i))
        self.sh.list_writer(w.write_subheader,write_itm)
        w.close()

    def getSelectedRecs (self):
        """Return each recipe in list"""
        def foreach(model,path,iter,recs):
            debug("foreach(model,path,iter,recs):",5)
            try:
                rec=model.get_value(iter,0)
                recs.append(rec)
            except:
                debug("DEBUG: There was a problem with iter: %s path: %s"%(iter,path),1)
        recs=[]
        self.rectree.get_selection().selected_foreach(foreach,recs)
        debug("%s selected recs: %s"%(len(recs),recs),3)
        return recs

    def clear (self, *args):
        debug("clear (self, *args):",5)
        selectedRecs=self.getSelectedRecs()
        if selectedRecs:
            for t in selectedRecs:
                self.recs.__delitem__(t.id)
                debug("clear removed %s"%t,3)
            self.resetSL()
        elif de.getBoolean(label=_("No recipes selected. Do you want to clear the entire list?")):
            self.recs = {}
            self.extras = []
            self.resetSL()            
        else:
            debug("clear cancelled",2)
        
    def addRec (self, rec, mult, includes={}):
        debug("addRec (self, rec, mult, includes={}):",5)
        """Add recipe to our list, assuming it's not already there.
        includes is a dictionary of optional items we want to include/exclude."""
        self.recs[rec.id]=(rec,mult)
        self.includes[rec.id]=includes
        self.resetSL()

    def commit_category_orders(self,tv,space_before=None,
                               space_after=None):
        """Commit the order of categories to memory.
        We allow for making room before or after a given
        iter, in which case"""
        mod=tv.get_model()
        iter=mod.get_iter_first()
        prev_pos = -100
        while iter:
            cat=mod.get_value(iter,0)
            if self.sh.catorder_dic.has_key(cat):
                # positions are all integers -- this allows changing positions
                # to be neatly dropped in as 0.5s
                pos = int(self.sh.catorder_dic[cat])
            else:
                pos = 0
            if pos <= prev_pos:
                pos=prev_pos+1
            self.sh.catorder_dic[cat]=pos
            iter=mod.iter_next(iter)
            prev_pos=pos
        
    def resetSL (self):
        debug("resetSL (self):",5)
        self.data,self.pantry = self.grabIngsFromRecs(self.recs.values(),self.extras)
        self.slMod = self.createIngModel(self.data)
        self.pMod = self.createIngModel(self.pantry)
        self.slTree.set_model(self.slMod)
        self.pTree.set_model(self.pMod)
        self.rectree.set_model(self.create_rmodel())
        self.slTree.expand_all()
        self.pTree.expand_all()
        self.pTree_sel_changed_cb(self.pTree.get_selection())
        self.slTree_sel_changed_cb(self.slTree.get_selection())

    def create_slTree (self, data):
        debug("create_slTree (self, data):",5)
        self.slMod = self.createIngModel(data)
        self.slTree = self.create_ingTree(self.glade.get_widget('shopITree'),
                                     self.slMod)
        self.slTree.connect('popup-menu',self.popup_ing_menu)
        def slTree_popup_cb (tv, event):
            debug("slTree_popup_cb (tv, event):",5)
            if event.button==3 or event.type == gtk.gdk._2BUTTON_PRESS:
                self.popup_ing_menu(tv,event)
                return True
        self.slTree.connect('button-press-event',slTree_popup_cb)
        self.slTree.get_selection().connect('changed',self.slTree_sel_changed_cb)
        # reset the first time
        self.slTree_sel_changed_cb(self.slTree.get_selection())

    def create_pTree (self, data):
        debug("create_pTree (self, data):",5)
        self.pMod = self.createIngModel(data)
        self.pTree = self.create_ingTree(self.glade.get_widget('pantryTree'),
                                    self.pMod)
        self.pTree.connect('popup-menu',self.popup_pan_menu)
        self.pTree.get_selection().connect('changed',self.pTree_sel_changed_cb)
        # reset the first time...
        self.pTree_sel_changed_cb(self.pTree.get_selection())
        def pTree_popup_cb (tv, event):
            debug("pTree_popup_cb (tv, event):",5)
            if event.button==3 or event.type == gtk.gdk._2BUTTON_PRESS:
                self.popup_pan_menu(tv,event)
                return True
            
        self.pTree.connect('button-press-event',pTree_popup_cb)
        
    def create_ingTree (self, widget, model):
        debug("create_ingTree (self, widget, model):",5)
        #self.slTree = gtk.TreeView(self.slMod)
        tree=widget
        tree.set_model(self.slMod)
        ## add multiple selections
        tree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        ## adding drag and drop functionality
        targets = [('GOURMET_SHOPPER_SW', gtk.TARGET_SAME_WIDGET, 0),
                   ('GOURMET_SHOPPER', gtk.TARGET_SAME_APP, 1),
                   ('text/plain',0,2),
                   ('STRING',0,3),
                   ('STRING',0,4),
                   ('COMPOUND_TEXT',0,5),
                   ('text/unicode',0,6),]
        tree.drag_source_set(gtk.gdk.BUTTON1_MASK, targets,
                             gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        tree.enable_model_drag_dest(targets,
                                    gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        tree.connect('drag_begin', self.on_drag_begin)
        #tree.connect('drag_data_get', self.on_drag_data_get)
        tree.connect('drag_data_received', self.on_drag_data_received)
        #tree.connect('drag_motion', self.on_drag_motion)
        #tree.connect('drag_drop', self.on_drag_drop)
        renderer = gtk.CellRendererText()
        for n,t in [[0,'Item'],[1,'Amount']]:
            col = gtk.TreeViewColumn(t,renderer,text=n)
            col.set_resizable(True)
            tree.append_column(col)
        tree.expand_all()
        tree.show()
        return tree

    def slTree_sel_changed_cb (self, selection):
        """Callback handler for selection change on shopping treeview."""
        if selection.count_selected_rows()>0:
            self.shopRemove.set_sensitive(True)
            # if we have items selected, the pantry tree should not
            # this makes these feel more like one control/list divided
            # into two sections.            
            self.pTree.get_selection().unselect_all()
        else:
            self.shopRemove.set_sensitive(False)

    def pTree_sel_changed_cb (self, selection):
        """Callback handler for selection change on pantry treeview"""
        if selection.count_selected_rows()>0:
            self.pantryRemove.set_sensitive(True)
            # if we have items selected, the shopping tree should not.
            # this makes these feel more like one control/list divided
            # into two sections.
            self.slTree.get_selection().unselect_all()
        else:
            self.pantryRemove.set_sensitive(False)

    def on_drag_begin(self, tv, context):
        debug("on_drag_begin(self, tv, context):",5)
        self.tv=tv
        self.ssave=te.selectionSaver(self.slTree,1)
        self.pssave=te.selectionSaver(self.pTree,1)

    def on_drag_motion (self, tv, context, x, y, time):
        debug("on_drag_motion (self, tv, context, x, y, time):",5)
        pass

    def on_drag_data_get (self, tv, context, selection, info, time):
        debug("on_drag_data_get (self, tv, context, selection, info, time):",5)
        debug('on_drag_data_get %s %s %s %s %s'%(tv,context,selection,info,time),5)
        self.drag_selection=selection
        debug("Selection data: %s %s %s %s"%(self.dragged,
                                             self.drag_selection.data,
                                             dir(self.drag_selection),
                                             self.drag_selection.get_text()),5)

    def ingSelection (self,return_iters=False):
        """A way to find out what's selected. By default, we simply return
        the list of ingredient keys. If return_iters is True, we return the selected
        iters themselves as well (returning a list of [key,iter]s)"""
        debug("ingSelection (self):",5)
        def foreach(model,path,iter,selected):
            debug("foreach(model,path,iter,selected):",5)
            selected.append(iter)
        selected=[]
        self.tv.get_selection().selected_foreach(foreach,selected)
        debug("multiple selections = %s"%selected,3)
        #ts,itera=self.tv.get_selection().get_selected()
        selected_keys=[]
        for itera in selected:
            key=self.tv.get_model().get_value(itera, 0)
            if return_iters:
                selected_keys.append((key,itera))
            else:
                selected_keys.append(key)
        debug("ingSelection returns: %s"%selected_keys,3)
        return selected_keys

    def popup_ing_menu (self, tv, event=None, *args):
        debug("popup_ing_menu (self, tv, *args):",5)
        self.tv = tv
        if not event:
            event = gtk.get_current_event()
        t = (event and hasattr(event,'time') and getattr(event,'time')
                or 0)
        btn = (event and hasattr(event,'button') and getattr(event,'button')
               or 0)
        print 'self.pop.popup(None,None,None,',btn,t,')'        
        self.pop.popup(None,None,None,btn,t)
        return True

    def popup_pan_menu (self, tv, event=None, *args):
        debug("popup_pan_menu (self, tv, *args):",5)
        self.tv = tv
        if not event:
            event = gtk.get_current_event()
        t = (event and hasattr(event,'time') and getattr(event,'time')
                or 0)
        btn = (event and hasattr(event,'button') and getattr(event,'button')
               or 0)
        print 'self.panpop.popup(None,None,None,',btn,t,')'
        self.panpop.popup(None,None,None,btn,t)
        return True

    def setup_popup (self):
        debug("setup_popup (self):",5)
        def make_popup (pop):
            debug("make_popup (pop):",5)
            catitm = gtk.MenuItem("_Change Category")
            popcats=gtk.Menu()
            catitm.set_submenu(popcats)
            catitm.show()
            popcats.show()
            pop.add(catitm)
            for i in self.sh.get_orgcats():
                itm = gtk.MenuItem(i)
                popcats.append(itm)
                itm.connect('activate',self.popup_callback,i)
                itm.show()
            create = gtk.MenuItem('New Category')
            popcats.append(create)
            create.connect('activate',self.add_sel_to_newcat)
            create.show()
        self.pop=self.glade.get_widget('ingmen')
        make_popup(self.pop)        
        self.panpop = self.glade.get_widget('panmen')
        make_popup(self.panpop)
        
    def popup_callback (self, menuitem, string):
        debug("popup_callback (self, menuitem, string):",5)
        kk=self.ingSelection()
        if self.sh.get_orgcats().__contains__(string):
            for k in kk:
                self.sh.orgdic[k]=string
        else:
            debug("WARNING: orgcats %s does not contain %s" %(self.sh.get_orgcats(), string),4)
        ssave=te.selectionSaver(self.slTree,1)
        pssave=te.selectionSaver(self.pTree,1)
        self.resetSL()
        ssave.restore_selections(tv=self.slTree)
        pssave.restore_selections(tv=self.slTree)        

    def add_sel_to_newcat (self, menuitem, *args):
        debug("add_sel_to_newcat (self, menuitem, *args):",5)
        kk=self.ingSelection()
        sublab = ', '.join(kk)
        cat = de.getEntry(label=_('Enter Category'),
                          sublabel=_("Category to add %s to") %sublab,
                          entryLabel=_('Category:'),
                          parent=self.widget)
        if cat:
            for k in kk:
                self.sh.orgdic[k]=cat
            self.pop.get_children()[-1].hide()
            self.panpop.get_children()[-1].hide()
            self.setup_popup()
            ssave=te.selectionSaver(self.slTree,1)
            pssave=te.selectionSaver(self.pTree,1)
            self.resetSL()
            ssave.restore_selections(tv=self.slTree)
            pssave.restore_selections(tv=self.slTree)        

    def add_selection_to_pantry (self, *args):
        """Add selected items to pantry."""
        debug("add_selection_to_pantry (self, *args):",5)
        self.tv = self.slTree
        self.ssave=te.selectionSaver(self.slTree,1)
        self.pssave=te.selectionSaver(self.pTree,1)
        kk = self.ingSelection()
        for k in kk:
            self.sh.add_to_pantry(k)
        self.resetSL()
        self.ssave.restore_selections(tv=self.pTree)
        
    def rem_selection_from_pantry (self, *args):
        """Add selected items to shopping list."""
        debug("rem_selection_from_pantry (self, *args):",5)
        self.tv = self.pTree
        self.ssave=te.selectionSaver(self.slTree,1)
        self.pssave=te.selectionSaver(self.pTree,1)
        for k in self.ingSelection():
            self.sh.remove_from_pantry(k)
        self.resetSL()
        self.pssave.restore_selections(tv=self.slTree)

    def on_drag_data_received(self, tv, context,x,y,selection,info,time):
        debug("on_drag_data_received(self, tv,context,x,y,selection,info,time):",5)
        if str(selection.target) == 'GOURMET_SHOPPER_SW':
            ## in this case, we're recategorizing
            #try:
            dest = tv.get_dest_row_at_pos(x,y)
            if dest:
                path,drop_where = dest
                iter=tv.get_model().get_iter((path[0])) #grab the category (outside of tree)
                cat=tv.get_model().get_value(iter,0)
                for sel,iter in self.ingSelection(return_iters=True):
                    path=tv.get_model().get_path(iter)
                    if len(path) == 1:
                        # if we're moving an entire category, then we
                        # need to reorder categories.
                        debug("Saving new category orders",0)
                        self.commit_category_orders(tv)
                        # and now we need to move our new category into place...
                        if drop_where==gtk.TREE_VIEW_DROP_AFTER or drop_where==gtk.TREE_VIEW_DROP_INTO_OR_AFTER:
                            new_pos=self.sh.catorder_dic[cat]+0.5
                        else:
                            new_pos=self.sh.catorder_dic[cat]-0.5
                        self.sh.catorder_dic[sel] = new_pos
                        debug("%s moved to position %s"%(sel,self.sh.catorder_dic[sel]),0)
                        debug("The current order is: %s"%self.sh.catorder_dic)
                    else:
                        self.sh.orgdic[sel]=cat
                self.resetSL()
                self.ssave.restore_selections(tv=self.slTree)
                self.pssave.restore_selections(tv=self.pTree)        
            #except TypeError:
            else:
                debug("Out of range!",0)
        elif str(selection.target) == 'GOURMET_SHOPPER':
            ## in this case, we're moving
            if tv == self.pTree:
                self.add_selection_to_pantry()
            else:
                self.rem_selection_from_pantry()
        
    def on_drag_drop (self, tv, context, x, y, time):
        debug("on_drag_drop (self, tv, context, x, y, time):",5)        
        #model = tv.get_model()
        otv,oselection=self.dragged
        if otv==self.pTree and tv==self.slTree:
            self.rem_selection_from_pantry()
        elif otv==self.slTree and tv==self.pTree:
            self.add_selection_to_pantry()
        else:
            try:
                path,drop_where = tv.get_dest_row_at_pos(x,y)
                iter=tv.get_model().get_iter((path[0])) #grab the category (outside of tree)
                cat=tv.get_model().get_value(iter,0)
                for sel in oselection:
                    self.sh.orgdic[sel]=cat
                self.resetSL()
            except TypeError, e:
                self.message("Out of range! %s")
        return False

    def createIngModel (self, data):
        debug("createIngModel (self, data):",5)
        """Data is a list of lists, where each item is [ing amt]"""
        mod = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        for c,lst in data:
            catiter = mod.append(None)
            mod.set_value(catiter, 0, c)
            for i in lst:
                ing = i[0]
                amt = i[1]
                iter = mod.append(catiter)
                mod.set_value(iter, 0, ing)
                mod.set_value(iter, 1, amt)
        return mod
        
    def grabIngsFromRecs (self, recs, start=[]):
        debug("grabIngsFromRecs (self, recs):",5)
        """Handed an array of (rec . mult)s, we combine their ingredients.
        recs may be IDs or objects."""
        lst = start[0:]
        for rec,mult in recs:
            lst.extend(self.grabIngFromRec(rec,mult=mult))
        self.sh = recipeManager.mkShopper(lst, self.rg.rd, conv=self.conv)
        data = self.sh.organize(self.sh.dic)
        pantry = self.sh.organize(self.sh.mypantry)
        debug("returning: data=%s pantry=%s"%(data,pantry),5)
        return data,pantry
            
    def grabIngFromRec (self, rec, mult=1):
        """Get an ingredient from a recipe and return a list with our amt,unit,key"""
        """We will need [[amt,un,key],[amt,un,key]]"""
        debug("grabIngFromRec (self, rec=%s, mult=%s):"%(rec,mult),5)
        # Grab all of our ingredients
        ings = self.rg.rd.get_ings(rec)
        lst = []
        # this constant should be 'ask',or rdatabase.RecData.AMT_MODE_LOW|AMT_MODE_AVERAGE|AMT_MODE_HIGH
        # this is handled in preferences (see prefsGui.py)
        #RESOLVE_RANGE_METHOD=self.rg.prefs.get('shop_handle_ranges','ask')
        include_dic = self.includes.get(rec.id) or {}
        for i in ings:
            if hasattr(i,'refid'): refid=i.refid
            else: refid=None
            debug("adding ing %s, %s"%(i.item,refid),4)
            if i.optional:
                # handle boolean includes value which applies to ALL ingredients
                if not include_dic or (include_dic != True and 
                                       (not include_dic.has_key(i.ingkey)
                                        or not include_dic[i.ingkey])
                                       ):
                    # we ignore our ingredient (don't add it)
                    continue
            if self.rg.rd.get_amount(i):
                amount=self.rg.rd.get_amount(i,mult=mult)                
            else: amount=None            
            if refid:
                ## a reference tells us to get another recipe
                ## entirely.  it has two parts: i.item (regular name),
                ## i.refid, i.refmult (amount we multiply recipe by)
                ## if we don't have the reference (i.refid), we just
                ## output the recipe name
                debug("Grabbing recipe as ingredient!",2)
                # disallow recursion
                subrec = self.rg.rd.get_referenced_rec(i)
                if subrec.id == rec.id:
                    de.show_message(
                        label=_('Recipe calls for itself as an ingredient.'),
                        sublabel=_('Ingredient %s will be ignored.')%rec.title + _('Infinite recursion is not allowed in recipes!'))
                    continue
                if subrec:
                    # recipe refs need an amount. We'll
                    # assume if need be.
                    amt = self.rg.rd.get_amount_as_float(i)
                    if not amt: amount=amt
                    refmult=mult*amt
                    if not include_dic.has_key(subrec.id):
                        d = getOptionalIngDic(self.rg.rd.get_ings(subrec),
                                              refmult,
                                              self.rg.prefs,
                                              self.rg)
                        include_dic[subrec.id]=d
                    nested_list=self.grabIngFromRec(subrec,
                                                    refmult)
                    lst.extend(nested_list)
                    continue
                else:
                    # it appears we don't have this recipe
                    debug("We don't have recipe %s"%i.item,0)
                    if not i.unit:
                        i.unit='recipe'
                    if not i.ingkey:
                        i.ingkey=i.item
            lst.append([amount,i.unit,i.ingkey])
        debug("grabIngFromRec returning %s"%lst,5)
        return lst

    def show (self, *args):
        debug("show (self, *args):",5)
        self.widget.show()
        try:
            self.widget.present()
        except:
            self.widget.grab_focus()

    def hide (self, *args):
        debug("hide (self, *args):",5)
        for c in self.conf:
            c.save_properties()
        self.widget.hide()
        self.sie.sdW.hide()
        return True

    def setup_shop_dialog (self):
        self.orgdic = self.sh.orgdic
        self.sie = shopIngredientEditor(self.rg, self)

    def message (self, txt):
        debug("message (self, txt): %s"%txt,5)
        self.stat.push(self.contid,txt)
        self.rg.message(txt)
    
class OptionalIngDialog (de.ModalDialog):
    """A dialog to query the user about whether to use optional ingredients."""
    def __init__ (self,vw,prefs,rg,mult=1,default=False):
        debug("__init__ (self,vw,default=False):",5)
        self.rg=rg
        de.ModalDialog.__init__(
            self, default,
            label=_("Select optional ingredients."),
            sublabel=_("Please specify which of the following optional ingredients you'd like to include on your shopping list."))
        self.mult = mult
        self.vw=vw
        self.ret = {}
        self.create_tree()
        self.cb = gtk.CheckButton("Always use these settings")
        self.cb.set_active(prefs.get('remember_optionals_by_default',False))
        alignment = gtk.Alignment()
        alignment.set_property('xalign',1.0)
        alignment.add(self.cb)
        self.vbox.add(alignment)
        alignment.show()
        self.cb.show()
        
    def create_model (self):
        """Create the TreeModel to show optional ingredients."""
        debug("create_model (self):",5)
        self.mod = gtk.TreeStore(gobject.TYPE_PYOBJECT, #the ingredient obj
                                 gobject.TYPE_STRING, #amount
                                 gobject.TYPE_STRING, #unit
                                 gobject.TYPE_STRING, #item
                                 gobject.TYPE_BOOLEAN) #include
        for i in self.vw:
            iter=self.mod.append(None)
            self.mod.set_value(iter,0,i)
            if self.mult==1:
                self.mod.set_value(iter,1,
                                   self.rg.rd.get_amount_as_string(i)
                                   )
            else:
                self.mod.set_value(iter,1,
                                   self.rg.rd.get_amount_as_string(i,float(self.mult))
                                   )
            self.mod.set_value(iter,2,i.unit)
            self.mod.set_value(iter,3,i.item)
            self.mod.set_value(iter,4,self.default)
            self.ret[i.ingkey]=self.default

    def create_tree (self):
        """Create our TreeView and populate it with columns."""
        debug("create_tree (self):",5)
        self.create_model()
        self.tree = gtk.TreeView(self.mod)
        txtr = gtk.CellRendererText()
        togr = gtk.CellRendererToggle()
        togr.set_property('activatable',True)
        togr.connect('toggled',self.toggle_ing_cb)
        #togr.start_editing()
        for n,t in [[1,'Amount'],[2,'Unit'],[3,'Item']]:
            col = gtk.TreeViewColumn(t,txtr,text=n)
            col.set_resizable(True)
            self.tree.append_column(col)
        bcol = gtk.TreeViewColumn('Add to Shopping List',
                                  togr, active=4)
        self.tree.append_column(bcol)
        self.vbox.add(self.tree)
        self.tree.show()

    def toggle_ing_cb (self, cellrenderertoggle, path, *args):
        debug("toggle_ing_cb (self, cellrenderertoggle, path, *args):",5)
        crt=cellrenderertoggle
        iter=self.mod.get_iter(path)
        val = self.mod.get_value(iter,4)
        newval = not val
        self.ret[self.mod.get_value(iter,0).ingkey]=newval
        self.mod.set_value(iter,4,newval)

    def run (self):
        self.show()
        if self.modal: gtk.main()
        if self.cb.get_active() and self.ret:
            # if we are saving our settings permanently...
            # we add ourselves to the shopoptional attribute
            for row in self.mod:
                ing = row[0]
                ing_include = row[4]
                if ing_include: ing.shopoptional=2
                else: ing.shopoptional=1
        return self.ret

class shopIngredientEditor (reccard.IngredientEditor):
    def __init__ (self, RecGui, ShopGui):
        self.sg = ShopGui
        self.last_key = ""
        reccard.IngredientEditor.__init__(self, RecGui, None)
        #self.ingBox = self.keyBox

    def init_dics (self):
        self.orgdic = self.sg.sh.orgdic
        self.shopcats = self.sg.sh.get_orgcats()

    def setup_glade (self):
        self.glade = self.sg.glade
        #self.glade.signal_connect('ieApply', self.apply)
        #self.ieBox.hide()
        self.amountBox = self.glade.get_widget('sdAmount')
        self.unitBox = self.glade.get_widget('sdUnit')
        self.keyBox = self.glade.get_widget('sdKey')
        self.shopBox = self.glade.get_widget('sdShopCat')
        # add some of our own signals...
        self.glade.signal_connect('sdAdd',self.add)
        self.sdToggle = False
        self.glade.signal_connect('shopAdd',self.showShopDialog)
        self.glade.signal_connect('sdHide',self.hideShopDialog)
        self.glade.signal_connect('sdAdd',self.add)
        self.sdW = self.glade.get_widget('ShopDialog')
        self.keyBox.get_children()[0].connect('changed',self.setKeyList)

    def setKeyList (self, *args):
        self.curkey = self.keyBox.entry.get_text()
        if self.curkey == self.last_key:
            return
        def vis (m, iter):
            x= m.get_value(iter,0)
            if x.find(self.curkey) > -1:
                return True
            else: return False
        self.keyBox.get_model().set_visible_func(vis)
        self.keyBox.get_model().refilter()
        self.last_key=self.curkey
        
    def add (self, *args):
        amt = self.amountBox.get_text()
        if amt:
            try:
                amt=convert.frac_to_float(amt)
            except:
                reccard.show_amount_error(amt)
                raise
        unit = self.unitBox.entry.get_text()
        key=self.getKey()
        shopcat = self.shopBox.child.get_text()
        if shopcat:
            self.rg.sl.sh.add_org_itm(key,shopcat)
        if key:
            itm = [amt, unit, key]
            self.sg.extras.append(itm)
            self.sg.resetSL()
            self.new()

    def returned (self, *args):
        self.add()
        self.amountBox.grab_focus()
        
    def toggleShopDialog (self, *args):
        if self.sdToggle: self.showShopDialog()
        else: self.hideShopDialog()
        
    def showShopDialog (self,*args):
        self.sdW.present()
        self.sdToggle=True

    def hideShopDialog (self,*args):
        self.sdW.hide()
        self.sdToggle=False
        return True


def getOptionalIngDic (ivw, mult, prefs, rg):
    """Return a dictionary of optional ingredients with a TRUE|FALSE value

    Alternatively, we return a boolean value, in which case that is
    the value for all ingredients.

    The dictionary will tell us which ingredients to add to our shopping list.
    We look at prefs to see if 'shop_always_add_optional' is set, in which case
    we don't ask our user."""    
    debug("getOptionalIngDic (ivw):",5)
    #vw = ivw.select(optional=True)
    vw = filter(lambda r: r.optional==True, ivw)
    # optional_mode: 0==ask, 1==add, -1==dont add
    optional_mode=prefs.get('shop_handle_optional',0)
    if optional_mode:
        if optional_mode==1:
            return True
        elif optional_mode==-1:
            return False
    elif len(vw) > 0:
        if not None in [i.shopoptional for i in vw]:
            # in this case, we have a simple job -- load our saved
            # defaults
            dic = {}
            for i in vw:
                if i.shopoptional==2: dic[i.ingkey]=True
                else: dic[i.ingkey]=False
            return dic
        # otherwise, we ask our user
        print 'Run OID with ',vw,prefs,rg,mult
        oid=OptionalIngDialog(vw, prefs, rg,mult )
        retval = oid.run()
        if retval:
            return retval
        else:
            raise "Option Dialog cancelled!"
