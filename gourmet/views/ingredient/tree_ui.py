from gourmet.controllers.ingredient import IngredientController
from gourmet.gdebug import debug
from gourmet import convert, Undo
from gourmet.gtk_extras import dialog_extras as de
from gourmet.gtk_extras import treeview_extras as te
from gourmet.models import Ingredient
import types
import gtk
import pango

class UndoableTreeStuff:
    def __init__ (self, ic):
        self.ic = ic

    def start_recording_additions (self):
        debug('UndoableTreeStuff.start_recording_additiong',3)
        self.added = []
        self.pre_ss = te.selectionSaver(self.ic.ingredient_editor_module.ingtree_ui.ingTree)
        self.connection = self.ic.imodel.connect('row-inserted',
                                                 self.row_inserted_cb)
        debug('UndoableTreeStuff.start_recording_additiong DONE',3)

    def stop_recording_additions (self):
        debug('UndoableTreeStuff.stop_recording_additiong',3)
        self.added = [
            # i.get_model().get_iter(i.get_path()) is how we get an
            # iter from a TreeRowReference
            self.ic.get_persistent_ref_from_iter(i.get_model().get_iter(i.get_path()))
            for i in self.added
            ]
        self.ic.imodel.disconnect(self.connection)
        debug('UndoableTreeStuff.stop_recording_additions DONE',3)

    def undo_recorded_additions (self):
        debug('UndoableTreeStuff.undo_recorded_additions',3)
        self.ic.delete_iters(
            *[self.ic.get_iter_from_persistent_ref(a) for a in self.added],
            **{'is_undo':True}
            )
        debug('UndoableTreeStuff.undo_recorded_additions DONE',3)

    def row_inserted_cb (self, tm, path, itr):
        self.added.append(gtk.TreeRowReference(tm,tm.get_path(itr)))

    def record_positions (self, iters):
        debug('UndoableTreeStuff.record_positions',3)
        self.pre_ss = te.selectionSaver(self.ic.ingredient_editor_module.ingtree_ui.ingTree)
        self.positions = []
        for i in iters:
            path = self.ic.imodel.get_path(i)
            if path[-1]==0:
                parent = path[:-1] or None
                sibling = None
            else:
                parent = None
                sibling = path[:-1] + (path[-1]-1,)
            sib_ref = sibling and self.ic.get_persistent_ref_from_path(sibling)
            parent_ref = parent and self.ic.get_persistent_ref_from_path(parent)
            ref = self.ic.get_persistent_ref_from_iter(i)
            self.positions.append((ref,sib_ref,parent_ref))
        debug('UndoableTreeStuff.record_positions DONE',3)

    def restore_positions (self):
        debug('UndoableTreeStuff.restore_positions',3)
        for ref,sib_ref,parent_ref in self.positions:
            te.move_iter(self.ic.imodel,
                         self.ic.get_iter_from_persistent_ref(ref),
                         sibling=sib_ref and self.ic.get_iter_from_persistent_ref(sib_ref),
                         parent=parent_ref and self.ic.get_iter_from_persistent_ref(parent_ref),
                         direction='after'
                         )
            self.pre_ss.restore_selections()
        debug('UndoableTreeStuff.restore_positions DONE',3)

class UndoableObjectWithInverseThatHandlesItsOwnUndo (Undo.UndoableObject):

    """A class for an UndoableObject whose Undo method already makes
    its own undo magic happen without need for our intervention.
    """
    # This is useful for making Undo's of "add"s -- we use the delete
    # methods for our Undoing nwhich already do a good job handling all
    # the Undo magic properly

    def inverse (self):
        self.history.remove(self)
        self.inverse_action()

def add_with_undo (rc,method):
    uts = UndoableTreeStuff(rc.ingtree_ui.ingController)
    def do_it ():
        uts.start_recording_additions()
        method()
        uts.stop_recording_additions()
    UndoableObjectWithInverseThatHandlesItsOwnUndo(
        do_it,
        uts.undo_recorded_additions,
        rc.history,
        widget=rc.ingtree_ui.ingController.imodel
        ).perform()

class IngredientTreeUI:

    """Handle our ingredient treeview display, drag-n-drop, etc.
    """

    head_to_att = {_('Amt'):'amount',
                   _('Unit'):'unit',
                   _('Item'):'item',
                   _('Key'):'ingkey',
                   _('Optional'):'optional',
                   #_('Shopping Category'):'shop_cat',
                   }

    def __init__ (self, ie, tree):
        self.ingredient_editor_module =ie; self.rg = self.ingredient_editor_module.rg
        self.ingController = IngredientController(self.ingredient_editor_module)
        self.ingTree = tree
        self.ingTree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)                
        self.setup_columns()
        self.ingTree.connect("row-activated",self.ingtree_row_activated_cb)
        self.ingTree.connect("key-press-event",self.ingtree_keypress_cb)
        self.selected=True
        #self.selection_changed()
        self.ingTree.get_selection().connect("changed",self.selection_changed_cb)
        self.setup_drag_and_drop()
        self.ingTree.show()
        
    # Basic setup methods

    def setup_columns (self):
        self.ingColsByName = {}
        self.ingColsByAttr = {}
        for n,head,tog,model,style,expand in [[1,_('Amt'),False,None,None,False],
                                 [2,_('Unit'),False,self.rg.umodel,None,False],
                                 [3,_('Item'),False,None,None,True],
                                 [4,_('Optional'),True,None,None,False],
                                 #[5,_('Key'),False,self.rg.inginfo.key_model,pango.STYLE_ITALIC],
                                 #[6,_('Shopping Category'),False,self.shopmodel,pango.STYLE_ITALIC],
                                 ]:        
            # Toggle setup
            if tog:
                renderer = gtk.CellRendererToggle()
                renderer.set_property('activatable',True)
                renderer.connect('toggled',self.ingtree_toggled_cb,n,'Optional')
                col=gtk.TreeViewColumn(head, renderer, active=n)
            # Non-Toggle setup
            else:
                if model:
                    debug('Using CellRendererCombo, n=%s'%n,0)
                    renderer = gtk.CellRendererCombo()
                    renderer.set_property('model',model)
                    renderer.set_property('text-column',0)
                else:
                    debug('Using CellRendererText, n=%s'%n,0)
                    renderer = gtk.CellRendererText()
                renderer.set_property('editable',True)
                renderer.connect('edited',self.ingtree_edited_cb,n,head)
                # If we have gtk > 2.8, set up text-wrapping
                try:
                    renderer.get_property('wrap-width')
                except TypeError:
                    pass
                else:
                    renderer.set_property('wrap-mode',pango.WRAP_WORD)
                    renderer.set_property('wrap-width',150)
                if head==_('Key'):
                    try:
                        renderer.connect('editing-started',
                                         self.ingtree_start_keyedit_cb)
                    except:
                        debug('Editing-started connect failed. Upgrade GTK for this functionality.',0)
                if style:
                    renderer.set_property('style',style)
                # Create Column
                col=gtk.TreeViewColumn(head, renderer, text=n)
            if expand: col.set_expand(expand)
            # Register ourselves...
            self.ingColsByName[head]=col
            if self.head_to_att.has_key(head):
                self.ingColsByAttr[self.head_to_att[head]]=n
            # All columns are reorderable and resizeable
            col.set_reorderable(True)
            col.set_resizable(True)
            col.set_alignment(0)
            col.set_min_width(45) 
            #if n==2:     #unit
            #    col.set_min_width(80) 
            if n==3:     #item
                col.set_min_width(130) 
            if n==5:     #key
                col.set_min_width(130)
            self.ingTree.append_column(col)

    def setup_drag_and_drop (self):
        ## add drag and drop support
        targets=[('GOURMET_INTERNAL', gtk.TARGET_SAME_WIDGET, 0),
                 ('text/plain',0,1),
                 ('STRING',0,2),
                 ('STRING',0,3),
                 ('COMPOUND_TEXT',0,4),
                 ('text/unicode',0,5),]
        self.ingTree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                              targets,
                                              gtk.gdk.ACTION_DEFAULT |
                                              gtk.gdk.ACTION_COPY |
                                              gtk.gdk.ACTION_MOVE)
        self.ingTree.enable_model_drag_dest(targets,
                                            gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.ingTree.connect("drag_data_received",self.dragIngsRecCB)
        self.ingTree.connect("drag_data_get",self.dragIngsGetCB)
        self.ingTree.connect('drag-begin',
                             lambda *args: setattr(self,'ss',te.selectionSaver(self.ingTree,0))
                             )
        self.ingTree.connect('drag-end',
                             lambda *args: self.ss.restore_selections()
                             )
    # End of setup methods

    # Callbacks and the like

    def my_isearch (self, mod, col, key, iter, data=None):
        # we ignore column info and search by item
        val = mod.get_value(iter,3)
        # and by key
        if val:
            val += mod.get_value(iter,5)
            if val.lower().find(key.lower()) != -1:
                return False
            else:
                return True
        else:
            val = mod.get_value(iter,1)
            if val and val.lower().find(key.lower())!=-1:
                return False
            else:
                return True
        
    def ingtree_row_activated_cb (self, tv, path, col, p=None):
        debug("ingtree_row_activated_cb (self, tv, path, col, p=None):",5)
        itr=self.get_selected_ing()
        i = self.ingController.imodel.get_value(itr,0)
        if isinstance(i,RecRef) or (hasattr(i,'refid') and i.refid):
            rec=self.rg.rd.get_referenced_rec(i)
            if rec:
                self.rg.open_rec_card(rec)
            else:
                de.show_message(parent=self.edit_window,
                                label=_("The recipe %s (ID %s) is not in our database.")%(i.item,
                                                                                          i.refid)
                                )
        else:
            d = self.ingController.get_ingredient(itr)
            #self.re.ie.show(i,d)
            #self.re.ie.ieExpander.set_expanded(True)

    def ingtree_keypress_cb (self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == 'Delete' or keyname == 'BackSpace':
            self.ingredient_editor_module.delete_cb()
            return True
                             

    def selection_changed_cb (self, *args):
        model,rows=self.ingTree.get_selection().get_selected_rows()
        self.selection_changed(rows and True)
        #if self.re.ie.ieExpander.get_expanded():
        #    itr = self.get_selected_ing()
        #    if itr:
        #        i = self.ingController.imodel.get_value(itr,0)
        #        d = self.ingController.get_ingredient(itr)
        #        if i: self.re.ie.show(i,d)
        #        else: self.re.ie.new()
        return True
    
    def selection_changed (self, selected=False):
        if selected != self.selected:
            if selected: self.selected=True
            else: self.selected=False
            if hasattr(self.ingredient_editor_module,'ingredientEditorOnRowActionGroup'):
                self.ingredient_editor_module.ingredientEditorOnRowActionGroup.set_sensitive(self.selected)

    def ingtree_toggled_cb (self, cellrenderer, path, colnum, head):
        debug("ingtree_toggled_cb (self, cellrenderer, path, colnum, head):",5)
        store=self.ingTree.get_model()
        iter=store.get_iter(path)
        val = store.get_value(iter,colnum)
        obj = store.get_value(iter,0)
        if type(obj) in types.StringTypes and obj.find('GROUP')==0:
            print 'Sorry, whole groups cannot be toggled to "optional"'
            return
        newval = not val
        ref = self.ingController.get_persistent_ref_from_iter(iter)
        u = Undo.UndoableObject(
            lambda *args: store.set_value(self.ingController.get_iter_from_persistent_ref(ref),
                                          colnum,newval),
            lambda *args: store.set_value(self.ingController.get_iter_from_persistent_ref(ref),
                                          colnum,val),
            self.ingredient_editor_module.history,
            widget=self.ingController.imodel
            )
        u.perform()
        
    def ingtree_start_keyedit_cb (self, renderer, cbe, path_string):
        debug('ingtree_start_keyedit_cb',0)
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.ingTree.get_model()
        iter = store.get_iter(path)
        itm=store.get_value(iter,self.ingColsByAttr['item'])
        mod = renderer.get_property('model')
        myfilter=mod.filter_new()
        cbe.set_model(myfilter)
        myKeys = self.rg.rd.key_search(itm)
        vis = lambda m, iter: m.get_value(iter,0) and (m.get_value(iter,0) in myKeys or m.get_value(iter,0).find(itm) > -1)
        myfilter.set_visible_func(vis)
        myfilter.refilter()

    def ingtree_edited_cb (self, renderer, path_string, text, colnum, head):
        indices = path_string.split(':')
        path = tuple( map(int, indices))
        store = self.ingTree.get_model()
        iter = store.get_iter(path)
        ing=store.get_value(iter,0)
        d = Ingredient()
        if type(ing) in [str,unicode]:
            debug('Changing group to %s'%text,2)
            self.change_group(iter, text)
            return
        else:       
            attr=self.head_to_att[head]
            try:
                setattr(d, attr, text)
            except ValueError:
                de.show_amount_error(text)
                raise

            if attr=='unit':
                amt,msg=self.changeUnit(text,self.ingController.get_ingredient(iter))
                if amt:
                    d.amount = amt
                #if msg:
                #    self.re.message(msg)
            elif attr=='item':
                d.ingkey = self.rg.rd.km.get_key(text)
            ref = self.ingController.get_persistent_ref_from_iter(iter)
            self.ingController.undoable_update_ingredient_row(ref,d)

    # Drag-n-Drop Callbacks
    
    def dragIngsRecCB (self, widget, context, x, y, selection, targetType,
                         time):
        debug("dragIngsRecCB (self=%s, widget=%s, context=%s, x=%s, y=%s, selection=%s, targetType=%s, time=%s)"%(self, widget, context, x, y, selection, targetType, time),3)
        drop_info=self.ingTree.get_dest_row_at_pos(x,y)
        mod=self.ingTree.get_model()
        if drop_info:
            path, position = drop_info
            dref = self.ingController.get_persistent_ref_from_path(path)
            dest_ing=mod.get_value(mod.get_iter(path),0)
            if type(dest_ing) in [str,unicode]: group=True
            else: group=False
        else:
            dref = None
            group = False
            position = None
        if str(selection.target) == 'GOURMET_INTERNAL':
            # if this is ours, we move it
            uts = UndoableTreeStuff(self.ingController)
            selected_iter_refs = [
                self.ingController.get_persistent_ref_from_iter(i) for i in self.selected_iter
                ]
            def do_move ():
                debug('do_move - inside dragIngsRecCB ',3)
                debug('do_move - get selected_iters from - %s '%selected_iter_refs,3)
                if dref:
                    diter = self.ingController.get_iter_from_persistent_ref(dref)
                else:
                    diter = None
                selected_iters = [
                    self.ingController.get_iter_from_persistent_ref(r) for r in selected_iter_refs
                    ]
                uts.record_positions(selected_iters)                
                debug('do_move - we have selected_iters - %s '%selected_iters,3)
                selected_iters.reverse()
                if (group and
                    (position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                     or
                     position==gtk.TREE_VIEW_DROP_INTO_OR_AFTER)
                    ):
                    for i in selected_iters:
                        te.move_iter(mod,i,direction="before",parent=diter)
                elif (position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                      or
                      position==gtk.TREE_VIEW_DROP_BEFORE):
                    for i in selected_iters:
                        te.move_iter(mod,i,sibling=diter,direction="before")
                else:
                    for i in selected_iters:
                        te.move_iter(mod,i,sibling=diter,direction="after")
                debug('do_move - inside dragIngsRecCB - move selections',3)
                self.ingTree.get_selection().unselect_all()
                for r in selected_iter_refs:
                    i = self.ingController.get_iter_from_persistent_ref(r)
                    if not i:
                        print 'Odd - I get no iter for ref',r
                        import traceback; traceback.print_stack()
                        print 'Strange indeed! carry on...'                        
                    else:
                        self.ingTree.get_selection().select_iter(i)
                debug('do_move - inside dragIngsRecCB - DONE',3)
            Undo.UndoableObject(
                do_move,
                uts.restore_positions,
                self.ingredient_editor_module.history,
                widget=self.ingController.imodel).perform()
               #self.ingTree.get_selection().select_iter(new_iter)
        else:
            # if this is external, we copy
            debug('external drag!',2)
            lines = selection.data.split("\n")
            lines.reverse()
            if (position==gtk.TREE_VIEW_DROP_BEFORE or
                position==gtk.TREE_VIEW_DROP_INTO_OR_BEFORE and not group):
                pre_path = te.path_next(self.ingController.get_path_from_persistent_ref(dref),-1)
                if pre_path:
                    itr_ref = self.ingController.get_persistent_ref_from_path(pre_path)
                else:
                    itr_ref = None
            else:
                itr_ref = dref
            def do_add ():
                for l in lines:
                    if group: 
                        self.ingredient_editor_module.add_ingredient_from_line(
                            l,
                            group_iter=self.ingController.get_iter_from_persistent_ref(itr_ref)
                            )
                    else:
                        self.ingredient_editor_module.add_ingredient_from_line(
                            l,
                            prev_iter=self.ingController.get_iter_from_persistent_ref(itr_ref)
                            )
            add_with_undo(self.ingredient_editor_module,do_add)
        #self.commit_positions()
        debug("restoring selections.")
        debug("done restoring selections.")        

    def dragIngsGetCB (self, tv, context, selection, info, timestamp):
        def grab_selection (model, path, iter, args):
            strings, iters = args            
            str = ""
            amt = model.get_value(iter,1)
            if amt:
                str="%s "%amt
            unit = model.get_value(iter,2)
            if unit:
                str="%s%s "%(str,unit)
            item = model.get_value(iter,3)
            if item:
                str="%s%s"%(str,item)
            debug("Dragged string: %s, iter: %s"%(str,iter),3)
            iters.append(iter)
            strings.append(str)
        strings=[]
        iters=[]
        tv.get_selection().selected_foreach(grab_selection,(strings,iters))
        str=string.join(strings,"\n")
        selection.set('text/plain',0,str)
        selection.set('STRING',0,str)
        selection.set('GOURMET_INTERNAL',8,'blarg')
        self.selected_iter=iters

    # Move-item callbacks

    def get_selected_refs (self):
        ts,paths = self.ingTree.get_selection().get_selected_rows()
        return [self.ingController.get_persistent_ref_from_path(p) for p in paths]
    
    def ingUpCB (self, *args):
        refs = self.get_selected_refs()
        u=Undo.UndoableObject(lambda *args: self.ingUpMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              lambda *args: self.ingDownMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              self.ingredient_editor_module.history,
                              widget=self.ingController.imodel,
                              )
        u.perform()

    def ingDownCB (self, *args):
        refs = self.get_selected_refs()
        u=Undo.UndoableObject(lambda *args: self.ingDownMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              lambda *args: self.ingUpMover(
            [self.ingController.get_path_from_persistent_ref(r) for r in refs]
            ),
                              self.ingredient_editor_module.history)
        u.perform()

    def ingUpMover (self, paths):
        ts = self.ingController.imodel
        def moveup (ts, path, itera):
            if itera:
                prev=te.path_next(path,-1)
                prev_iter=ts.get_iter(prev)
                te.move_iter(ts,itera,sibling=prev_iter,direction="before")
                #self.ingTree.get_selection().unselect_path(path)
                #self.ingTree.get_selection().select_path(prev)
        paths.reverse()
        tt = te.selectionSaver(self.ingTree)        
        for p in paths:
            itera = ts.get_iter(p)
            moveup(ts,p,itera)
        tt.restore_selections()
        
    def ingDownMover (self, paths):
        ts = self.ingController.imodel
        def movedown (ts, path, itera):
            if itera:
                next = ts.iter_next(itera)
                te.move_iter(ts,itera,sibling=next,direction="after")
                #if next:
                #    next_path=ts.get_path(next)
                #else:
                #    next_path=path
        paths.reverse()
        tt = te.selectionSaver(self.ingTree)
        for p in paths:
            itera = ts.get_iter(p)
            movedown(ts,p,itera)
        tt.restore_selections()

    def get_previous_iter_and_group_iter (self):
        """Return prev_iter,group_iter"""
        # If there is a selected iter, we treat it as a group to put
        # our entry into or after
        selected_iter = self.getSelectedIter()
        if not selected_iter:
            # default behavior (put last)
            group_iter = None
            prev_iter = None
        elif type(self.ingController.imodel.get_value(selected_iter,0)) in types.StringTypes:
            # if we are a group
            group_iter = selected_iter
            prev_iter = None
        else:
            # then we are a previous iter...
            group_iter = None
            prev_iter = selected_iter
        return prev_iter,group_iter

    # Edit Callbacks
    def changeUnit (self, new_unit, ingredient):
        """Handed a new unit and an ingredient, we decide whether to convert and return:
        None (don't convert) or Amount (new amount)
        Message (message for our user) or None (no message for our user)"""
        key=ingredient.ingkey
        old_unit=ingredient.unit
        old_amt=ingredient.amount
        if type(old_amt)==str:
            old_amt = convert.frac_to_float(old_amt)
        density=None
        conversion = self.rg.conv.converter(old_unit,new_unit,key)
        if conversion and conversion != 1:
            new_amt = old_amt*conversion
            opt1 = _("Converted: %(amt)s %(unit)s")%{'amt':convert.float_to_frac(new_amt),
                                                     'unit':new_unit}
            opt2 = _("Not Converted: %(amt)s %(unit)s")%{'amt':convert.float_to_frac(old_amt),
                                                         'unit':new_unit}
            CONVERT = 1
            DONT_CONVERT = 2
            choice = de.getRadio(label=_('Changed unit.'),
                                 sublabel=_('You have changed the unit for %(item)s from %(old)s to %(new)s. Would you like the amount converted or not?')%{
                'item':ingredient.item,
                'old':old_unit,
                'new':new_unit},
                                 options=[(opt1,CONVERT),
                                          (opt2,DONT_CONVERT),]
                                 )
            if not choice:
                raise Exception("User cancelled")
            if choice==CONVERT:
                return (new_amt,
                        _("Converted %(old_amt)s %(old_unit)s to %(new_amt)s %(new_unit)s"%{
                    'old_amt':old_amt,
                    'old_unit':old_unit,
                    'new_amt':new_amt,
                    'new_unit':new_unit,})
                        )
            else:
                return (None,
                        None)
        if conversion:
            return (None,None)
        return (None,
                _("Unable to convert from %(old_unit)s to %(new_unit)s"%{'old_unit':old_unit,
                                                                         'new_unit':new_unit}
                  ))


    # End Callbacks

    # Convenience methods / Access to the Tree

    # Accessing the selection

    def getSelectedIters (self):
        if len(self.ingController.imodel)==0:
            return None
        ts,paths = self.ingTree.get_selection().get_selected_rows()
        return [ts.get_iter(p) for p in paths]

    def getSelectedIter (self):
        debug("getSelectedIter",4)
        if len(self.ingController.imodel)==0:
            return None
        try:
            ts,paths=self.ingTree.get_selection().get_selected_rows()
            lpath=paths[-1]
            group=ts.get_iter(lpath)
        except:
            debug("getSelectedIter: there was an exception",0)            
            group=None
        return group

    def get_selected_ing (self):
        """get selected ingredient"""
        debug("get_selected_ing (self):",5)
        path, col = self.ingTree.get_cursor()
        if path:
            itera = self.ingTree.get_model().get_iter(path)
        else:
            tv,rows = self.ingTree.get_selection().get_selected_rows()
            if len(rows) > 0:
                itera = rows[0]
            else:
                itera=None
        return itera
        #if itera:
        #    return self.ingTree.get_model().get_value(itera,0)
        #else: return None

    def set_tree_for_rec (self, rec):
        self.ingTree.set_model(
            self.ingController.create_imodel(rec)
            )
        self.selection_changed()
        self.ingTree.expand_all()

    def ingNewGroupCB (self, *args):
        group_name = de.getEntry(label=_('Adding Ingredient Group'),
                                 sublabel=_('Enter a name for new subgroup of ingredients'),
                                 entryLabel=_('Name of group:'),
                                 )
        selected_iters=self.getSelectedIters() or []
        undo_info = []
        for i in selected_iters:
            deleted_dic,prev_ref,ing_obj = self.ingController._get_undo_info_for_iter_(i)
            undo_info.append((deleted_dic,prev_ref,ing_obj,[],False))
        selected_iter_refs = [self.ingController.get_persistent_ref_from_iter(i)\
                              for i in selected_iters]
        pitr=self.getSelectedIter()
        if pitr:
            prev_iter_ref = self.ingController.get_persistent_ref_from_iter(pitr)
        else:
            prev_iter_ref = None
        def do_add_group ():
            itr = self.ingController.add_group(
                group_name,
                children_iters=[
                self.ingController.get_iter_from_persistent_ref(r) for r in selected_iter_refs
                ],
                prev_iter=(prev_iter_ref and self.ingController.get_iter_from_persistent_ref(prev_iter_ref))
                )
            gi = self.ingController.get_persistent_ref_from_iter(itr)
            self.ingTree.expand_row(self.ingController.imodel.get_path(itr),True)
        def do_unadd_group ():
            gi = 'GROUP '+group_name  #HACK HACK HACK
            self.ingController.imodel.remove(
                self.ingController.get_iter_from_persistent_ref(gi)
                )
            self.ingController.do_undelete_iters(undo_info)
        u = Undo.UndoableObject(do_add_group,
                           do_unadd_group,
                           self.ingredient_editor_module.history)
        u.perform()

    def change_group (self, itr, text):
        debug('Undoable group change: %s %s'%(itr,text),3)
        model = self.ingController.imodel
        oldgroup0 = model.get_value(itr,0)
        oldgroup1 = model.get_value(itr,1)
        def get_group_iter (old_value):
            # Somewhat hacky -- our persistent references are stored in
            # the "0" column, which is simply "GROUP text". This means
            # that we can't properly "persist" groups since this chunk of
            # text changes when the group's name changes. In order to
            # remedy, we're relying on the hackish "GROUP name" value +
            # knowing what the previous group value was to make the
            # "persistent" reference work.
            return self.ingController.get_iter_from_persistent_ref("GROUP %s"%old_value)
        def change_my_group ():
            itr = get_group_iter(oldgroup1)
            self.ingController.imodel.set_value(itr,0,"GROUP %s"%text)
            self.ingController.imodel.set_value(itr,1,text)
        def unchange_my_group ():
            itr = get_group_iter(text)
            self.ingController.imodel.set_value(itr,0,oldgroup0)
            self.ingController.imodel.set_value(itr,1,oldgroup1)
        obj = Undo.UndoableObject(change_my_group,unchange_my_group,self.ingredient_editor_module.history)
        obj.perform()