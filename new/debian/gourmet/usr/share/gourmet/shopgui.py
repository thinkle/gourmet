#!/usr/bin/env python
import gtk.glade, gtk, gobject, pango, sys, os.path, time, os
import rmetakit, convert, WidgetSaver, reccard
import dialog_extras as de
import treeview_extras as te
import printer
from gdebug import *
from gglobals import *
from gettext import gettext as _

class ShopGui:
    """A class to manage our shopping window."""
    def __init__ (self, RecGui, conv=None):
        debug("__init__ (self, RecGui):",5)
        self.glade = gtk.glade.XML(os.path.join(gladebase,'shopList.glade'))
        self.conv=conv
        self.rg = RecGui
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
            })

    def create_rtree (self):
        debug("create_rtree (self):",5)
        self.rmodel = self.create_rmodel()
        #self.rectree = gtk.TreeView(self.rmodel)
        self.rectree = self.glade.get_widget('shopRTree')
        self.glade.signal_connect('ingmen_pantry',self.add_selection_to_pantry)
        self.glade.signal_connect('panmen_remove',self.rem_selection_from_pantry)        
        self.rectree.set_model(self.rmodel)
        renderer = gtk.CellRendererText()
        #renderer.set_property('editable',gtk.TRUE)
        #renderer.connect('edited',tst)
        titl = gtk.TreeViewColumn(_("Title"),renderer,text=1)
        mult = gtk.TreeViewColumn(_("x"),renderer,text=2)
        self.rectree.append_column(titl)
        self.rectree.append_column(mult)
        titl.set_resizable(gtk.TRUE)
        titl.set_clickable(gtk.TRUE)
        titl.set_reorderable(gtk.TRUE)
        mult.set_resizable(gtk.TRUE)
        mult.set_clickable(gtk.TRUE)
        mult.set_reorderable(gtk.TRUE)
        self.rectree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.rectree.show()
        
    def create_rmodel (self):
        debug("create_rmodel (self):",5)
        mod = gtk.TreeStore(gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_STRING)
        for r,mult in self.recs.items():
            iter = mod.append(None)
            mod.set_value(iter,0,r)
            mod.set_value(iter,1,r.title)
            mod.set_value(iter,2,convert.float_to_frac(mult))
        return mod

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
        import lprprinter
        self._printList(lprprinter.SimpleWriter,file=filename,show_dialog=False)
    def printList (self, *args):
        debug("printList (self, *args):",0)
        self._printList(printer.SimpleWriter,dialog_parent=self.widget)
        
    def _printList (self, printer, *args, **kwargs):
        #w=printer.SimpleWriter(*args,**kwargs)
        w = printer(*args,**kwargs)
        w.write_header(_("Shopping list for %s")%time.strftime("%x"))
        w.write_subheader(_("For the following recipes:"))
        for r,mult in self.recs.items():
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
                self.recs.__delitem__(t)
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
        self.recs[rec]=mult
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
        self.data,self.pantry = self.grabIngsFromRecs(self.recs.items(),self.extras)
        self.slMod = self.createIngModel(self.data)
        self.pMod = self.createIngModel(self.pantry)
        self.slTree.set_model(self.slMod)
        self.pTree.set_model(self.pMod)
        self.rectree.set_model(self.create_rmodel())
        self.slTree.expand_all()
        self.pTree.expand_all()

    def create_slTree (self, data):
        debug("create_slTree (self, data):",5)
        self.slMod = self.createIngModel(data)
        self.slTree = self.create_ingTree(self.glade.get_widget('shopITree'),
                                     self.slMod)
        self.slTree.connect('row-activated',self.popup_ing_menu)
        self.slTree.connect('popup-menu',self.popup_ing_menu)
        def slTree_popup_cb (tv, event):
            debug("slTree_popup_cb (tv, event):",5)
            if event.button==3:
                self.popup_ing_menu(tv)
                return gtk.TRUE
        self.slTree.connect('button-press-event',slTree_popup_cb)

    def create_pTree (self, data):
        debug("create_pTree (self, data):",5)
        self.pMod = self.createIngModel(data)
        self.pTree = self.create_ingTree(self.glade.get_widget('pantryTree'),
                                    self.pMod)
        self.pTree.connect('row-activated',self.popup_pan_menu)
        self.pTree.connect('popup-menu',self.popup_pan_menu)
        def pTree_popup_cb (tv, event):
            debug("pTree_popup_cb (tv, event):",5)
            if event.button==3:
                self.popup_pan_menu(tv)
                return gtk.TRUE
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
            col.set_resizable(gtk.TRUE)
            tree.append_column(col)
        tree.expand_all()
        tree.show()
        return tree

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
        debug("Selection data: %s %s %s %s"%(self.dragged, self.drag_selection.data, dir(self.drag_selection), self.drag_selection.get_text()),5)

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

    def popup_ing_menu (self, tv, *args):
        debug("popup_ing_menu (self, tv, *args):",5)
        self.tv = tv
        self.pop.popup(None,None,None,0,0)

    def popup_pan_menu (self, tv, *args):
        debug("popup_pan_menu (self, tv, *args):",5)
        self.tv = tv
        self.panpop.popup(None,None,None,0,0)

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
        str=kk[0]
        if len(kk) > 1:
            for k in kk[1:]:
                str="%s, %s"%str,k
        cat = de.getEntry(label=_("Category to add %s to") %str, parent=self.widget)
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
        debug("add_selection_to_pantry (self, *args):",5)
        kk = self.ingSelection()
        for k in kk:
            self.sh.add_to_pantry(k)
        self.resetSL()
        self.ssave.restore_selections(tv=self.pTree)
        
    def rem_selection_from_pantry (self, *args):
        debug("rem_selection_from_pantry (self, *args):",5)
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
        return gtk.FALSE

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
        for r in recs:
            if len(r) > 1:
                lst.extend(self.grabIngFromRec(r[0],mult=r[1]))
            else:
                lst.extend(self.grabIngFromRec(r[0]))
        self.sh = rmetakit.mkShopper(lst, self.rg.rd, conv=self.conv)
        data = self.sh.organize(self.sh.dic)
        pantry = self.sh.organize(self.sh.mypantry)
        debug("returning: data=%s pantry=%s"%(data,pantry),5)
        return data,pantry
            
    def grabIngFromRec (self, rec, mult=1):
        debug("grabIngFromRec (self, rec=%s(%s), mult=%s):"%(rec.title,rec.id,mult),5)
        """We will need [[amt,un,key],[amt,un,key]]"""
        if type(rec) == type(""):
            rec = self.rg.rd.get_rec(rec)
        ings = self.rg.rd.get_ings(rec)
        lst = []
        for i in ings:
            try:
                refid=i.refid
            except:
                refid=None
            debug("adding ing %s, %s"%(i.item,refid),4)
            if i.optional=='yes':
                if (self.includes.has_key(rec.id) and
                    (not self.includes[rec.id].has_key(i.key) or not self.includes[rec.id][i.key])
                    ):
                    continue
            if i.amount:
                amount=float(i.amount)*mult
            else: amount=None            
            if refid:
                ## a reference tells us to get another recipe entirely.
                ## it has two parts:
                ## i.item (regular name), i.refid, i.refmult (amount we multiply recipe by)
                ## if we don't have the reference (i.refid), we just output the recipe name
                debug("Grabbing recipe as ingredient!",2)
                # disallow recursion
                if refid == rec.id:
                    de.show_message(
                        label=_('Recipe calls for itself as an ingredient.'),
                        sublabel=_('Ingredient %s will be ignored.')%rec.title + _('Infinite recursion is not allowed in recipes!'))
                    continue

                subrec = self.rg.rd.get_rec(i.refid)
                if subrec:
                    # recipe refs need an amount. We'll
                    # assume if need be.
                    if not i.amount: i.amount=1
                    refmult=mult*i.amount
                    if not self.includes.has_key(subrec.id):
                        d = getOptionalIngDic(self.rg.rd.get_ings(subrec),refmult)
                        self.includes[subrec.id]=d
                    nested_list=self.grabIngFromRec(subrec,refmult)
                    lst.extend(nested_list)
                    continue
                else:
                    # it appears we don't have this recipe
                    debug("We don't have recipe %s"%i.item,0)
                    if not i.unit:
                        i.unit='recipe'
                    if not i.key:
                        i.key=i.item
            lst.append([amount,i.unit,i.key])
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
    
class OptionalIngDialog (de.mDialog):
    def __init__ (self,vw,mult=1,default=False):
        debug("__init__ (self,vw,default=False):",5)
        #gtk.Dialog.__init__(self)
        de.mDialog.__init__(self, default, label=_("Select optional ingredients."), sublabel=_("Please specify which of the following optional ingredients you'd like to include on your shopping list."))
        self.mult = mult
        self.vw=vw
        self.ret = {}
        #self.default = default #whether we default to adding ingredients
        self.create_tree()
        
    def create_model (self):
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
                self.mod.set_value(iter,1,i.amount)
            else:
                self.mod.set_value(iter,1,float(i.amount)*float(self.mult))
            self.mod.set_value(iter,2,i.unit)
            self.mod.set_value(iter,3,i.item)
            self.mod.set_value(iter,4,self.default)
            self.ret[i.key]=self.default

    def create_tree (self):
        debug("create_tree (self):",5)
        self.create_model()
        self.tree = gtk.TreeView(self.mod)
        txtr = gtk.CellRendererText()
        togr = gtk.CellRendererToggle()
        togr.set_property('activatable',gtk.TRUE)
        togr.connect('toggled',self.toggle_ing_cb)
        #togr.start_editing()
        for n,t in [[1,'Amount'],[2,'Unit'],[3,'Item']]:
            col = gtk.TreeViewColumn(t,txtr,text=n)
            col.set_resizable(gtk.TRUE)
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
        self.ret[self.mod.get_value(iter,0).key]=newval
        self.mod.set_value(iter,4,newval)

class shopIngredientEditor (reccard.IngredientEditor):
    def __init__ (self, RecGui, ShopGui):
        self.sg = ShopGui
        self.last_key = ""
        reccard.IngredientEditor.__init__(self, RecGui, None)

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
        
def getOptionalIngDic (ivw, mult):
    debug("getOptionalIngDic (ivw):",5)
    vw = ivw.select(optional='yes')
    if len(vw) > 0:
        oid=OptionalIngDialog(vw, mult)
        return oid.run()
        #return {} #until we write this, we'll exclude ingredients
    else:
        return {}
