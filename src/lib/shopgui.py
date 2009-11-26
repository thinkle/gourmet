#!/usr/bin/env python
import gtk.glade, gtk, gobject, pango, sys, os.path, time, os, string
import recipeManager, convert, reccard, prefs
from gtk_extras import WidgetSaver, mnemonic_manager
from gtk_extras import dialog_extras as de
from gtk_extras import treeview_extras as te
from gtk_extras import fix_action_group_importance
from exporters.printer import get_print_manager
from gdebug import *
from gglobals import *
from gettext import gettext as _
#from nutrition.nutritionLabel import NutritionLabel
#from nutrition.nutrition import NutritionInfoList
from gtk_extras.FauxActionGroups import ActionManager
import plugin_loader, plugin

ui = '''
<ui>
  <menubar name="ShoppingListMenuBar">
    <menu name="File" action="File">
      <menuitem action="Save"/>
      <menuitem action="Print"/>
      <separator/>
      <placeholder name="ExtraFileStuff"/>
      <separator/>
      <menuitem action="Close"/>	
    </menu>
    <menu name="Edit" action="Edit">
      <menuitem action="AddNewItems"/>      
      <menuitem action="RemoveRecipes"/>
      <separator/>
      <menuitem action="ItemToPantry"/>
      <menuitem action="ItemToShoppingList"/>
      <menuitem action="ChangeCategory"/>
    </menu>
    <menu name="HelpMenu" action="HelpMenu">
      <menuitem action="Help"/>
    </menu>
  </menubar>
  <popup name="ShopPop">
    <menuitem action="ItemToPantry"/>
    <menu action="ChangeCategoryPop">
      <placeholder name="categories"/>
      <menuitem action="newCategory"/>
    </menu>
  </popup>
  <popup name="PanPop">
    <menuitem name="ItemToShoppingList" action="ItemToShoppingList"/>
    <menu name="ChangeCategoryPop" action="ChangeCategoryPop">
      <placeholder name="categories"/>
      <menuitem name="newCategory" action="newCategory"/>
    </menu>
  </popup>
  <popup action="ChangeCategoryPopup">
     <placeholder name="categories"/>
     <menuitem name="newCategory" action="newCategory"/>
  </popup>
  <toolbar name="ShoppingListTopToolBar">
    <toolitem action="Save"/>
    <toolitem action="Print"/>
    <separator/>
    <toolitem action="RemoveRecipes"/>
  </toolbar>
  <toolbar name="ShoppingListActionToolBar">
    <toolitem action="AddNewItems"/>
    <separator/>
    <toolitem action="ChangeCategory"/>
    <separator/>
    <toolitem action="ItemToShoppingList"/>
    <toolitem action="ItemToPantry"/>
  </toolbar>
</ui>
'''

# Convenience functions
def setup_frame_w_accel_label (txt, target_widget=None):
    '''Return a frame with a mnemonic label'''
    l =  gtk.Label(txt)
    l.set_use_underline(True)
    f = gtk.Frame()
    f.set_label_widget(l); l.show()
    if target_widget:
	l.set_mnemonic_widget(target_widget)
    return f

def setup_sw (child):
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    sw.add(child)
    child.show(); sw.show()
    return sw
# end convenience functions

class IngredientAndPantryList:
    '''A subclass to handle all TreeView code for moving items between
    shopping and pantry list
    '''

    def __init__ (self):
	if hasattr(self,'rg'):
	    self.rd = self.rg.rd
	else:
	    self.rd = recipeManager.get_recipe_manager()
        # We need to keep track of including/excluding options...
        # Here's our solution: we have a dictionary where we can lookg
        # up ingredients by recipe by key
        # {'recipe_id' : {'key1' : False
        #                 'key2  : True}} ... where true and false mean include/exclude
	self.includes = {}
        self.setup_ui_manager()
	self.setup_actions()
	self.create_popups()

    def setup_ui_manager (self):
	self.ui_manager = gtk.UIManager()
	self.ui_manager.add_ui_from_string(ui)

    def setup_actions (self):
	self.pantryActions = gtk.ActionGroup('PantryActions')
        self.shoppingActions = gtk.ActionGroup('ShoppingActions')
	self.pantryOrShoppingActions = gtk.ActionGroup('PantryOrShoppingActions')
	self.pantryOrShoppingActions.add_actions([
	    ('ChangeCategoryPop',None,_('Change _Category')),
	    ('newCategory',None,_('Create new category'),None,None,
	     lambda *args: self.pantryOrShoppingActions.get_action('ChangeCategory').set_active(True)),
	    ])
	self.pantryOrShoppingActions.add_toggle_actions([
	    ('ChangeCategory',
             None,
             _('Change _Category'),
             None,
	     _('Change the category of the currently selected item'),
	     self.change_category
	     ),
	    ]
							)
	self.pantryActions.add_actions([
	    ('PantryPopup',None,_('Pantry')),
	    ('ItemToShoppingList',# name
	     'add-to-shopping-list',# stock
	     _('Move to _Shopping List'), # text
	     _('<Ctrl>B'), # key-command
	     None, # tooltip
	     lambda *args: self.rem_selection_from_pantry() # callback
	     ),
	    ])
	self.shoppingActions.add_actions([
	    ('ShopPopup',None,_('Shopping List')),
	    ('ItemToPantry',# name
	     gtk.STOCK_UNDO,# stock
	     _('Move to _pantry'), # text
	     _('<Ctrl>D'), # key-command
	     _('Remove from shopping list'), # tooltip
	     lambda *args: self.add_selection_to_pantry() # callback
	     ),
	    ])
        fix_action_group_importance(self.pantryActions)
	self.ui_manager.insert_action_group(self.pantryActions,0)
        fix_action_group_importance(self.shoppingActions)
	self.ui_manager.insert_action_group(self.shoppingActions,0)
        fix_action_group_importance(self.pantryOrShoppingActions)
	self.ui_manager.insert_action_group(self.pantryOrShoppingActions,0)	

    def setup_category_ui (self):
	self.cats_setup = True
	catUI = '''<placeholder name="categories">'''
	def my_cb (widget, cat):
	    self.change_to_category(cat)
	for n,category in enumerate(self.sh.get_orgcats()):
	    actionName = 'category'+str(n)
	    catUI += '<menuitem action="%s"/>'%actionName
	    self.pantryOrShoppingActions.add_actions([
		(actionName,None,category,
		 None,_('Move selected items into %s')%category,
		 None)
		]
		)
	    self.pantryOrShoppingActions.get_action(actionName).connect('activate',my_cb,category)
	    self.get_catmodel().append([category])
	catUI += '</placeholder>'
	catUI = '''<ui>
	<menubar action="ShoppingListMenu">
	  <menu action="Edit">
	    <menu action="ChangeCategoryPop">
	      %(ph)s
	    </menu>
	  </menu>
	</menubar>
	<popup action="ShopPop">
	    <menu action="ChangeCategoryPop">
	    %(ph)s
	    </menu>
	</popup>
	<popup name="PanPop">
	  <menu name="ChangeCategoryPop" action="ChangeCategoryPop">
	  %(ph)s
	  </menu>
	</popup>
	<popup name="ChangeCategoryPopup">
	  %(ph)s
	</popup>	
	</ui>'''%{'ph':catUI}
	self.last_category_merge = self.ui_manager.add_ui_from_string(catUI)
	self.ui_manager.ensure_update()

    # Base GUI Setup
    def setup_paned_view (self):
	self.create_pTree()
	self.create_slTree()
	hp =  gtk.HPaned(); hp.set_position(400)
        f1 = setup_frame_w_accel_label(_('_Shopping List'),self.slTree)
        f2 = setup_frame_w_accel_label(_('Already Have (_Pantry Items)'),self.pTree)
	f1.add(setup_sw(self.slTree)); f1.show_all()
	f2.add(setup_sw(self.pTree)); f2.show_all()
        hp.add1(f1)
        hp.add2(f2)
	return hp

    # TreeView and TreeModel setup
    def create_pTree (self):
        debug("create_pTree (self, data):",5)
        self.pMod = self.createIngModel(self.pantry)
	self.pTree = self.create_ingTree(gtk.TreeView(),
					  self.pMod)
        #self.pTree.connect('popup-menu',self.popup_pan_menu)
        self.pTree.get_selection().connect('changed',self.pTree_sel_changed_cb)
        # reset the first time...
        self.pTree_sel_changed_cb(self.pTree.get_selection())
        def pTree_popup_cb (tv, event):
            debug("pTree_popup_cb (tv, event):",5)
            if event.button==3 or event.type == gtk.gdk._2BUTTON_PRESS:
                self.popup_pan_menu(tv,event)
                return True
            
        self.pTree.connect('button-press-event',pTree_popup_cb)

    def create_slTree (self):
        debug("create_slTree (self, data):",5)
        self.slMod = self.createIngModel(self.data)
	self.slTree = self.create_ingTree(gtk.TreeView(),
					  self.slMod)
	self.slTree.show()
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

    def create_ingTree (self, widget, model):
        debug("create_ingTree (self, widget, model):",5)
        #self.slTree = gtk.TreeView(self.slMod)
        tree=widget
        tree.set_model(model)
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
        tree.connect('drag_data_get', self.on_drag_data_get)
        tree.connect('drag_data_received', self.on_drag_data_received)
        tree.connect('drag_motion', self.on_drag_motion)
        tree.connect('drag_drop', self.on_drag_drop)
        renderer = gtk.CellRendererText()
        for n,t in [[0,'Item'],[1,'Amount']]:
            col = gtk.TreeViewColumn(t,renderer,text=n)
            col.set_resizable(True)
            tree.append_column(col)
        tree.expand_all()
        tree.show()
        return tree

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

    # ---- TreeView callbacks...
    def slTree_sel_changed_cb (self, selection):
        """Callback handler for selection change on shopping treeview."""
        if selection.count_selected_rows()>0:
            self.shoppingActions.set_sensitive(True)
            # if we have items selected, the pantry tree should not
            # this makes these feel more like one control/list divided
            # into two sections.
	    self.tv = self.slTree
            self.pTree.get_selection().unselect_all()
        else:
            self.shoppingActions.set_sensitive(False)

    def pTree_sel_changed_cb (self, selection):
        """Callback handler for selection change on pantry treeview"""
        if selection.count_selected_rows()>0:
            self.pantryActions.set_sensitive(True)
            # if we have items selected, the shopping tree should not.
            # this makes these feel more like one control/list divided
            # into two sections.
	    self.tv = self.pTree
            self.slTree.get_selection().unselect_all()
        else:
            self.pantryActions.set_sensitive(False)

    # Popup menu setup
    def create_popups (self):
	self.shoppop = self.ui_manager.get_widget('/ShopPop')
	self.panpop = self.ui_manager.get_widget('/PanPop')

    # Drag-and-drop
    def on_drag_begin(self, tv, context):
        debug("on_drag_begin(self, tv, context):",5)
        self.tv=tv
        self.ssave=te.selectionSaver(self.slTree,1)
        self.pssave=te.selectionSaver(self.pTree,1)

    def on_drag_motion (self, tv, context, x, y, time):
        pass

    def on_drag_data_get (self, tv, context, selection, info, time):
        self.drag_selection=selection
        
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
                for sel,iter in self.get_selected_ingredients(return_iters=True):
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
    # end drag-n-drop methods

    # ---- end TreeView callbacks
    
    # -- End TreeView and TreeModel setup

    # Callbacks for moving data back and forth
    def resetSL (self):
        debug("resetSL (self):",5)
        self.data,self.pantry = self.organize_list(self.lst)
        self.slMod = self.createIngModel(self.data)
        self.pMod = self.createIngModel(self.pantry)
        self.slTree.set_model(self.slMod)
        self.pTree.set_model(self.pMod)
        #self.rectree.set_model(self.create_rmodel())
        self.slTree.expand_all()
        self.pTree.expand_all()
        #self.pTree_sel_changed_cb(self.pTree.get_selection())
        #self.slTree_sel_changed_cb(self.slTree.get_selection())

    def add_selection_to_pantry (self, *args):
        """Add selected items to pantry."""
        debug("add_selection_to_pantry (self, *args):",5)
        self.tv = self.slTree
        self.ssave=te.selectionSaver(self.slTree,1)
        self.pssave=te.selectionSaver(self.pTree,1)
        kk = self.get_selected_ingredients()
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
        for k in self.get_selected_ingredients():
            self.sh.remove_from_pantry(k)
        self.resetSL()
        self.pssave.restore_selections(tv=self.slTree)

    def change_to_category (self, category):
	'''Change selected recipes to category category'''
	do_reset = category not in self.sh.get_orgcats()
	kk=self.get_selected_ingredients()
	for k in kk:
	    self.sh.orgdic[k]=category
	ssave=te.selectionSaver(self.slTree,1)
	pssave=te.selectionSaver(self.pTree,1)
	self.resetSL()
	ssave.restore_selections(tv=self.slTree)
	pssave.restore_selections(tv=self.slTree)
	if do_reset:
	    self.reset_categories()

    def reset_categories (self):
	self.ui_manager.remove_ui(self.last_category_merge)
	self.get_catmodel().clear()
	self.setup_category_ui()
	self.create_popups()

    def add_sel_to_newcat (self, menuitem, *args):
        debug("add_sel_to_newcat (self, menuitem, *args):",5)
        kk=self.get_selected_ingredients()
        sublab = ', '.join(kk)
        cat = de.getEntry(label=_('Enter Category'),
                          sublabel=_("Category to add %s to") %sublab,
                          entryLabel=_('Category:'),
                          parent=self.widget)
        if cat:
            for k in kk:
                self.sh.orgdic[k]=cat
            self.shoppop.get_children()[-1].hide()
            self.panpop.get_children()[-1].hide()
            self.setup_popup()
            ssave=te.selectionSaver(self.slTree,1)
            pssave=te.selectionSaver(self.pTree,1)
            self.resetSL()
            ssave.restore_selections(tv=self.slTree)
            pssave.restore_selections(tv=self.slTree)        
    
    # Popup methods...
    def popup_ing_menu (self, tv, event=None, *args):
        debug("popup_ing_menu (self, tv, *args):",5)
        self.tv = tv
        if not event:
            event = gtk.get_current_event()
        t = (event and hasattr(event,'time') and getattr(event,'time')
                or 0)
        btn = (event and hasattr(event,'button') and getattr(event,'button')
               or 0)
        self.shoppop.popup(None,None,None,btn,t)
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
        self.panpop.popup(None,None,None,btn,t)
        return True

    # Data convenience methods
    def get_selected_ingredients (self,return_iters=False):
        """A way to find out what's selected. By default, we simply return
        the list of ingredient keys. If return_iters is True, we return the selected
        iters themselves as well (returning a list of [key,iter]s)"""
        debug("get_selected_ingredients (self):",5)
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
        debug("get_selected_ingredients returns: %s"%selected_keys,3)
        return selected_keys

    def grabIngsFromRecs (self, recs, start=[]):
        debug("grabIngsFromRecs (self, recs):",5)
        """Handed an array of (rec . mult)s, we combine their ingredients.
        recs may be IDs or objects."""
        self.lst = start[0:]
        for rec,mult in recs:
            self.lst.extend(self.grabIngFromRec(rec,mult=mult))
	return self.organize_list(self.lst)
    
    def organize_list (self, lst):
        self.sh = recipeManager.DatabaseShopper(lst, self.rd)
	if not hasattr(self,'cats_setup') or not self.cats_setup:
	    self.setup_category_ui()
        data = self.sh.organize(self.sh.dic)
        pantry = self.sh.organize(self.sh.mypantry)
        debug("returning: data=%s pantry=%s"%(data,pantry),5)
        return data,pantry

    def grabIngFromRec (self, rec, mult=1):
        """Get an ingredient from a recipe and return a list with our amt,unit,key"""
        """We will need [[amt,un,key],[amt,un,key]]"""
        debug("grabIngFromRec (self, rec=%s, mult=%s):"%(rec,mult),5)
        # Grab all of our ingredients
	rd = self.rd
	ings = rd.get_ings(rec)
        lst = []
        include_dic = self.includes.get(rec.id) or {}
        for i in ings:
            if hasattr(i,'refid'): refid=i.refid
            else: refid=None
            debug("adding ing %s, %s"%(i.item,refid),4)
            if i.optional:
                # handle boolean includes value which applies to ALL ingredients
                if not include_dic:
                    continue
                if type(include_dic) == dict :
                    # Then we have to look at the dictionary itself...
                    if ((not include_dic.has_key(i.ingkey))
                        or
                        not include_dic[i.ingkey]):
                        # we ignore our ingredient (don't add it)
                        continue
            if rd.get_amount(i):
                amount=rd.get_amount(i,mult=mult)                
            else: amount=None            
            if refid:
                ## a reference tells us to get another recipe
                ## entirely.  it has two parts: i.item (regular name),
                ## i.refid, i.refmult (amount we multiply recipe by)
                ## if we don't have the reference (i.refid), we just
                ## output the recipe name
                debug("Grabbing recipe as ingredient!",2)
                # disallow recursion
                subrec = rd.get_referenced_rec(i)
                if subrec.id == rec.id:
                    de.show_message(
                        label=_('Recipe calls for itself as an ingredient.'),
                        sublabel=_('Ingredient %s will be ignored.')%rec.title + _('Infinite recursion is not allowed in recipes!'))
                    continue
                if subrec:
                    # recipe refs need an amount. We'll
                    # assume if need be.
                    amt = rd.get_amount_as_float(i)
                    if not amt: amount=amt
                    refmult=mult*amt
                    if not include_dic.has_key(subrec.id):
                        d = getOptionalIngDic(rd.get_ings(subrec),
                                              refmult,
                                              self.prefs,
					      )
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

class ShopGui (plugin_loader.Pluggable, IngredientAndPantryList):

    def __init__ (self):
	IngredientAndPantryList.__init__(self)
	self.prefs = prefs.get_prefs()
	self.conf = []	
        self.w = gtk.Window(); self.main = gtk.VBox()
	self.w.set_title(_('Shopping List'))
	self.w.set_default_size(800,600)
        self.w.connect('delete-event',self.hide)
	from GourmetRecipeManager import get_application
        self.recs = {}; self.extras = []
	self.data,self.pantry=self.grabIngsFromRecs([])
        self.setup_ui_manager()
        self.setup_actions()
        self.setup_main()
	self.conf.append(WidgetSaver.WindowSaver(self.w,
						 self.prefs.get('shopGuiWin',{}),
						 show=False)
			 )
	self.conf.append(
	    WidgetSaver.WidgetSaver(self.vp,
				    self.prefs.get('shopvpaned1',{'position':self.vp.get_position()})
				    )
	    )
	self.conf.append(
	    WidgetSaver.WidgetSaver(self.hp,
				    self.prefs.get('shophpaned1',{'position':self.hp.get_position()})
				    )
	    )
	    
	plugin_loader.Pluggable.__init__(self,
					 [plugin.ShoppingListPlugin])
    # Create interface...
    
    def setup_ui_manager (self):
        self.ui_manager = gtk.UIManager()
        self.ui_manager.add_ui_from_string(ui)

    def setup_main (self):
        mb = self.ui_manager.get_widget('/ShoppingListMenuBar')
        self.main.pack_start(mb,fill=False,expand=False)
        ttb = self.ui_manager.get_widget('/ShoppingListTopToolBar')
        self.main.pack_start(ttb,fill=False,expand=False)
        self.vp = gtk.VPaned(); self.vp.show(); self.vp.set_position(150)
	self.create_rtree()
        self.top_frame = setup_frame_w_accel_label(_('_Recipes'),self.rectree)
	self.top_frame.add(setup_sw(self.rectree)); self.top_frame.show()
        self.vp.add1(self.top_frame)
        vb = gtk.VBox(); vb.show()
        self.vp.add2(vb)
        slatb = self.ui_manager.get_widget('/ShoppingListActionToolBar'); slatb.show()
        vb.pack_start(slatb,expand=False,fill=False)
	self.setup_add_box()
	vb.pack_start(self.add_box,expand=False,fill=False)
	self.setup_cat_box()
	vb.pack_start(self.cat_box,expand=False,fill=False)
	self.hp = self.setup_paned_view(); self.hp.show()
	vb.pack_start(self.hp)
	self.main.pack_start(self.vp); self.vp.show()
	vb.show()
	self.w.add(self.main)
	self.main.show()
	self.w.add_accel_group(self.ui_manager.get_accel_group())

    def setup_add_box (self):
	# Setup add-ingredient widget
	self.add_box = gtk.HBox()
	self.add_entry = gtk.Entry()
	add_label = gtk.Label(_('_Add items:')); add_label.set_use_underline(True)
	add_label.set_mnemonic_widget(self.add_entry)
	self.add_box.pack_start(add_label,expand=False,fill=False); add_label.show()	
	self.add_box.pack_start(self.add_entry); self.add_entry.show()
	self.add_button = gtk.Button(stock=gtk.STOCK_ADD)
	self.add_box.pack_start(self.add_button,expand=False,fill=False); self.add_button.show()
	self.add_entry.connect('activate',self.item_added)
	self.add_button.connect('clicked',self.item_added)

    def get_catmodel (self):
	if hasattr(self,'catmodel'): return self.catmodel
	else:
	    self.catmodel = gtk.ListStore(str)
	    return self.catmodel

    def setup_cat_box (self):
	# Setup change-category widget
	self.cat_box = gtk.HBox(); #self.cat_box.set_spacing(6)
	self.cat_cbe = gtk.ComboBoxEntry()
	self.cat_cbe.set_model(self.get_catmodel())
	self.cat_cbe.set_text_column(0)
	self.cat_entry = self.cat_cbe.child	
	self.cat_button = gtk.Button(stock=gtk.STOCK_APPLY)
	self.cat_label = gtk.Label('_Category: '); self.cat_label.set_use_underline(True)
	self.cat_label.set_mnemonic_widget(self.cat_entry)
	comp = gtk.EntryCompletion()
	comp.set_model(self.get_catmodel()); comp.set_text_column(0)
	self.cat_entry.set_completion(comp)
	self.cat_box.pack_start(self.cat_label,expand=False,fill=False); self.cat_label.show()
	self.cat_box.pack_start(self.cat_cbe); self.cat_cbe.show()	
	self.cat_box.pack_start(self.cat_button,expand=False,fill=False); self.cat_button.show()
	self.cat_entry.connect('activate',self.category_changed)
	self.cat_button.connect('clicked',self.category_changed)
        
    def setup_actions (self):
        self.mainActionGroup = gtk.ActionGroup('MainActions')
        self.recipeListActions = gtk.ActionGroup('RecipeListActions')
	self.recipeListActions.add_actions([
	    ('RemoveRecipes',gtk.STOCK_REMOVE,_('Remove Recipes'),
	     '<Control>Delete',_('Remove recipes from shopping list'),
	     self.clear_recipes,
	    )])
        self.mainActionGroup.add_actions([
	    ('Edit',None,_('_Edit')),
            ('Save',# name
             gtk.STOCK_SAVE,# stock
             None, # text
             None, # key-command
             None, # tooltip
             self.save# callback
             ),
            ('Print'   ,# name
             gtk.STOCK_PRINT,# stock
             None, # text
             '<Ctrl>P', # key-command
             None, # tooltip
             self.printList # callback
             ),
            ('Close'   ,# name
             gtk.STOCK_CLOSE,# stock
             None, # text
             None, # key-command
             None, # tooltip
             self.hide# callback
             ),
            ('File',None,_('_File')),
            ('Help',gtk.STOCK_HELP,_('_Help'),None,None,
             lambda *args: de.show_faq(HELP_FILE,jump_to='Shopping')),		
            ('HelpMenu',None,_('_Help')),
		])
	self.mainActionGroup.add_toggle_actions([
		('AddNewItems',
		 gtk.STOCK_ADD,
		 _('Add items'),
		 '<Ctrl>plus',
		 _('Add arbitrary items to shopping list'),
		 self.add_item
		 ),
		#(   ,# name
                #    ,# stock
                #    , # text
                #    , # key-command
                #    , # tooltip
                #     # callback
                #    ),
                ])

        fix_action_group_importance(self.mainActionGroup)
	self.ui_manager.insert_action_group(self.mainActionGroup,0)
        fix_action_group_importance(self.recipeListActions)
	self.ui_manager.insert_action_group(self.recipeListActions,0)
	IngredientAndPantryList.setup_actions(self)

    # -- TreeView and TreeModel setup
    def create_rtree (self):
        debug("create_rtree (self):",5)
        self.rmodel = self.create_rmodel()
        self.rectree = gtk.TreeView(self.rmodel)
        #self.glade.signal_connect('ingmen_pantry',self.add_selection_to_pantry)
        #self.glade.signal_connect('panmen_remove',self.rem_selection_from_pantry)        
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
	self.rectree.connect('row-activated',self.rectree_activated_cb)	
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

    def rectree_activated_cb (self, tv, path, vc):
	rec = tv.get_model()[path][0]
	from GourmetRecipeManager import get_application
	get_application().open_rec_card(rec)

    # End UI Set-up

    # Convenience methods for handling our data
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

    def commit_category_orders (self, tv, space_before=None, space_after=None):
        """Commit the order of categories to memory.
        We allow for making room before or after a given
        iter, in which case"""
	mod = tv.get_model()
	iter = mod.get_iter_first()
	last_val = -100
	while iter:
	    cat = mod.get_value(iter,0)
	    if self.sh.catorder_dic.has_key(cat):
		val = self.sh.catorder_dic[cat]
	    else:
		val = 0
	    if val <= last_val:
		val = last_val + 10
		self.sh.catorder_dic[cat] = val
	    last_val = val
	    iter = mod.iter_next(iter)

    # Saving and printing
    def doSave (self, filename):
        debug("doSave (self, filename):",5)
        #import exporters.lprprinter
        #self._printList(exporters.lprprinter.SimpleWriter,file=filename,show_dialog=False)
        ofi = file(filename,'w')
        ofi.write(_("Shopping list for %s")%time.strftime("%x") + '\n\n')
        ofi.write(_("For the following recipes:"+'\n'))
        ofi.write('--------------------------------\n')
        for r,mult in self.recs.values():
            itm = "%s"%r.title
            if mult != 1:
                itm += _(" x%s")%mult
            ofi.write(itm+'\n')
        write_itm = lambda a,i: ofi.write("%s %s"%(a,i) + '\n')
        write_subh = lambda h: ofi.write('\n_%s_\n'%h)
        self.sh.list_writer(write_subh,write_itm)
        ofi.close()

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

    # Setting up recipe...
    def addRec (self, rec, mult, includes={}):
        debug("addRec (self, rec, mult, includes={}):",5)
        """Add recipe to our list, assuming it's not already there.
        includes is a dictionary of optional items we want to include/exclude."""
        self.recs[rec.id]=(rec,mult)
        self.includes[rec.id]=includes
	self.reset()
	
    def reset (self):
	self.grabIngsFromRecs(self.recs.values(),self.extras)
        self.resetSL()
	self.rectree.set_model(self.create_rmodel())

    # Callbacks
    def hide (self, *args):
	self.w.hide()
        return True
        
    def show (self, *args):
	self.w.show()

    def clear_recipes (self, *args):
        debug("clear_recipes (self, *args):",5)
        selectedRecs=self.getSelectedRecs()
        if selectedRecs:
            for t in selectedRecs:
                self.recs.__delitem__(t.id)
                debug("clear removed %s"%t,3)
            self.reset()
        elif de.getBoolean(label=_("No recipes selected. Do you want to clear the entire list?")):
            self.recs = {}
            self.extras = []
            self.reset()            
        else:
            debug("clear cancelled",2)
	
    
    def save (self, *args):
        debug("save (self, *args):",5)
        self.doSave(de.select_file(_("Save Shopping List As..."),
                                   filename=os.path.join(os.path.expanduser("~"),
                                                         "%s %s"%(_('Shopping List'),
                                                                  time.strftime("%x").replace("/","-"),
                                                                  )),
                                   action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                   ))

    def printList (self, *args):
        debug("printList (self, *args):",0)
        self._printList(get_print_manager().get_simple_writer(),dialog_parent=self.w)

    def add_item (self, toggleWidget):
	if toggleWidget.get_active():
	    self.add_box.show()
	    self.add_entry.grab_focus()
	    if self.pantryOrShoppingActions.get_action('ChangeCategory').get_active():
		self.pantryOrShoppingActions.get_action('ChangeCategory').set_active(False)
	else:
	    self.add_box.hide()

    def change_category (self, toggleWidget):
	if toggleWidget.get_active():
	    self.cat_box.show()
	    self.cat_entry.grab_focus()
	    if self.mainActionGroup.get_action('AddNewItems').get_active():
		self.mainActionGroup.get_action('AddNewItems').set_active(False)
	else:
	    self.cat_box.hide()

    def item_added (self, *args):
	txt = self.add_entry.get_text()
	dct = self.rd.ingredient_parser(txt)
	if not dct: dct = {'amount':None,'unit':None,'item':txt}
	self.extras.append([dct.get('amount'),dct.get('unit'),dct.get('item')])
        # Make sure it doesn't end up in the pantry...        
        self.sh.remove_from_pantry(dct.get('item')) 
	self.grabIngsFromRecs(self.recs.values(),self.extras)
	self.resetSL()
	self.add_entry.set_text('')

    def category_changed (self, *args):
	cat = self.cat_entry.get_text()
	self.change_to_category(cat)
	self.cat_entry.set_text('')
    
class OptionalIngDialog (de.ModalDialog):
    """A dialog to query the user about whether to use optional ingredients."""
    def __init__ (self,vw,prefs,mult=1,default=False):
        debug("__init__ (self,vw,default=False):",5)
	self.rd = recipeManager.get_recipe_manager()
        de.ModalDialog.__init__(
            self, default,
            label=_("Select optional ingredients"),
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
                                   self.rd.get_amount_as_string(i)
                                   )
            else:
                self.mod.set_value(iter,1,
                                   self.rd.get_amount_as_string(i,float(self.mult))
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
                if ing_include: self.rd.modify_ing(ing,{'shopoptional':2})
                else: self.rd.modify_ing(ing,{'shopoptional':1})
        return self.ret

def getOptionalIngDic (ivw, mult, prefs, rg=None):
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
        oid=OptionalIngDialog(vw, prefs, mult)
        retval = oid.run()
        if retval:
            return retval
        else:
            raise "Option Dialog cancelled!"

if __name__ == '__main__':
    class TestIngredientAndPantryList (IngredientAndPantryList):

	def __init__ (self):
	    IngredientAndPantryList.__init__(self)
	    #self.data = [('Dairy',[('milk','1 gal'),('cheese, cheddar','1 lb'),
	    #('cottage cheese','8 oz'),
	    #('yogurt','8 oz')]),
	    #('Pastas',[('rotini','1 lb')]),]
	    #self.pantry = [('Dairy',[('eggs','1/2 doz')]),
	    #('Frozen',[('ice cream','1 gal')]),
	    #]
	    rm = recipeManager.get_recipe_manager()
	    recs = [(r,1) for r in rm.fetch_all(rm.recipe_table)[:2]]
	    self.data,self.pantry =  self.grabIngsFromRecs(recs)
	    self.w = gtk.Window(); self.w.set_title(_('Shopping List'))
	    self.w.add(self.setup_paned_view())
	    self.w.show_all()
	    self.w.connect('delete-event',gtk.main_quit)
    #tst = TestIngredientAndPantryList()
    sg = ShopGui()
    rm = recipeManager.get_recipe_manager()
    recs = [(r,1) for r in rm.fetch_all(rm.recipe_table)[:2]]
    for r,mult in recs:
	sg.addRec(r,mult)
    gtk.main()
	    


    #sg = ShopGui()
    #sg.show()
    sg.w.connect('delete-event',gtk.main_quit)
    gtk.main()
