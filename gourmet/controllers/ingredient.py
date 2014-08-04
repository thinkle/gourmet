from gourmet.plugin_loader import Pluggable, pluggable_method
from gourmet.plugin import IngredientControllerPlugin
from gourmet.gdebug import debug
from gourmet.models.ingredient import RecRef, Ingredient
from gourmet.gtk_extras.treeview_extras import path_next, move_iter
from gourmet.importers.importer import parse_range
from gourmet import Undo
import gtk
import gobject
import types

class IngredientController (Pluggable):

    """Handle updates to our ingredient model.

    Changes are not reported as they happen; rather, we use the
    commit_ingredients method to do sync up our database with what
    we're showing as our database.
    """

    ING_COL = 0
    AMT_COL = 1
    UNIT_COL = 2
    ITEM_COL = 3
    OPTIONAL_COL = 4

    def __init__ (self, ingredient_editor_module):
        self.ingredient_editor_module = ingredient_editor_module;
        self.rg = self.ingredient_editor_module.rg
        self.re = self.ingredient_editor_module.re
        self.new_item_count = 0
        self.commited_items_converter = {}
        Pluggable.__init__(self,
                                         [IngredientControllerPlugin])

    # Setup methods
    def create_imodel (self, rec):
        self.ingredient_objects = []        
        self.current_rec=rec
        ## now we continue with our regular business...
        debug("%s ings"%len(rec.ingredients),3)
        self.imodel = gtk.TreeStore(gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_BOOLEAN,
                                    #gobject.TYPE_STRING,
                                    #gobject.TYPE_STRING
                                    )
        for g,ings in rec.the_ingredients:
            if g:
                g=self.add_group(g)
            for i in ings:
                debug('adding ingredient %s'%i.item,0)
                self.add_ingredient(i, group_iter=g)
        return self.imodel

    def _new_iter_ (self,
                    group_iter=None,
                    prev_iter=None,
                    fallback_on_append=True):
        iter = None
        if group_iter and not prev_iter:
            if type(self.imodel.get_value(group_iter, 0)) not in types.StringTypes:
                prev_iter = group_iter
                print 'fix this old code!'
                import traceback; traceback.print_stack()
                print '(not a real traceback, just a hint for fixing the old code)'
            else:
                iter = self.imodel.append(group_iter)
        if prev_iter:
            iter = self.imodel.insert_after(None, prev_iter, None)
        if not iter:
            if fallback_on_append: iter = self.imodel.append(None)
            else: iter = self.imodel.prepend(None)
        return iter
    
    # Add recipe info...
    def add_ingredient_from_kwargs (self, group_iter=None, prev_iter=None,
                                    fallback_on_append=True, undoable=False,
                                    placeholder=None, # An ingredient
                                                      # object count
                                                      # (number)
                                    ingredient=Ingredient()):
        iter = self._new_iter_(group_iter=group_iter,prev_iter=prev_iter,
                               fallback_on_append=fallback_on_append)
        if ingredient.recipe_ref:
            self.imodel.set_value(iter,0,
                                  RecRef(ingredient.recipe_ref,ingredient.item)
                                  )
        elif placeholder is not None:
            self.imodel.set_value(iter,0,placeholder)
        else:
            self.imodel.set_value(iter,0,self.new_item_count)
            self.new_item_count+=1
        self.update_ingredient_row(
            iter,ingredient.amt, ingredient.unit, ingredient.item, ingredient.optional
            )
        return iter

    def add_new_ingredient (self,                            
                            *args,
                            **kwargs
                            ):
        ret = self.add_ingredient_from_kwargs(*args,**kwargs)
        return ret

    def undoable_update_ingredient_row (self, ref, d):
        itr = self.ingredient_editor_module.ingtree_ui.ingController.get_iter_from_persistent_ref(ref)
        orig = self.ingredient_editor_module.ingtree_ui.ingController.get_rowdict(itr)
        Undo.UndoableObject(
            lambda *args: self.update_ingredient_row(itr,**d),
            lambda *args: self.update_ingredient_row(itr,**orig),
            self.ingredient_editor_module.history,
            widget=self.imodel,
            ).perform()

    def update_ingredient_row (self,iter,
                               amount=None,
                               unit=None,
                               item=None,
                               optional=None,
                               ingkey=None,
                               shop_cat=None,
                               refid=None,
                               undoable=False
                               ):
        if amount is not None: self.imodel.set_value(iter,1,amount)
        if unit is not None: self.imodel.set_value(iter,2,unit)
        if item is not None: self.imodel.set_value(iter,3,item)
        if optional is not None: self.imodel.set_value(iter,4,optional)
        #if ingkey is not None: self.imodel.set_value(iter,5,ingkey)
        #if shop_cat:
        #    self.imodel.set_value(iter,6,shop_cat)
        #elif ingkey and self.re.rg.sl.orgdic.has_key(ingkey):
        #    self.imodel.set_value(iter,6,self.re.rg.sl.orgdic[ingkey])
                
    def add_ingredient (self, ing, prev_iter=None, group_iter=None,
                        fallback_on_append=True, shop_cat=None,
                        is_undo=False):
        """add an ingredient to our model based on an ingredient
        object.

        group_iter is an iter to put our ingredient inside of.

        prev_iter is an ingredient after which we insert our ingredient

        fallback_on_append tells us whether to append or (if False)
        prepend when we have no group_iter.

        is_undo asks if this is part of an UNDO action. If it is, we
        don't add the object to our list of ingredient_objects (which
        is designed to reflect the current state of the database).
        """
        i = ing
        # Append our ingredient object to a list so that we will be able to notice if it has been deleted...
        if not is_undo: self.ingredient_objects.append(ing)
        iter = self._new_iter_(prev_iter=prev_iter,group_iter=group_iter,fallback_on_append=fallback_on_append)
        amt = i.amt
        unit = i.unit
        self.imodel.set_value(iter, 0, i)
        self.imodel.set_value(iter, 1, unicode(amt))
        self.imodel.set_value(iter, 2, unit)
        self.imodel.set_value(iter, 3, i.item)
        if i.optional:
            opt=True
        else:
            opt=False
        self.imodel.set_value(iter, 4, opt)
        #self.imodel.set_value(iter, 5, i.ingkey)
        #if shop_cat:
        #    self.imodel.set_value(iter, 6, shop_cat)
        #elif self.rg.sl.orgdic.has_key(i.ingkey):
        #    debug("Key %s has category %s"%(i.ingkey,self.rg.sl.orgdic[i.ingkey]),5)
        #    self.imodel.set_value(iter, 6, self.rg.sl.orgdic[i.ingkey])
        #else:
        #    self.imodel.set_value(iter, 6, None)
        return iter

    def add_group (self, name, prev_iter=None, children_iters=[], fallback_on_append=True):
        if not prev_iter:
            if fallback_on_append: groupiter = self.imodel.append(None)
            else: groupiter = self.imodel.prepend(None)
        else:
            # ALLOW NO NESTING!
            while self.imodel.iter_parent(prev_iter):
                prev_iter = self.imodel.iter_parent(prev_iter)
            groupiter = self.imodel.insert_after(None,prev_iter,None)
        self.imodel.set_value(groupiter, 0, "GROUP %s"%name)
        self.imodel.set_value(groupiter, 1, name)
        children_iters.reverse()
        for c in children_iters:
            move_iter(self.imodel,c,None,parent=groupiter,direction='after')
            #self.rg.rd.undoable_modify_ing(self.imodel.get_value(c,0),
            #                               {'inggroup':name},
            #                               self.history)
        debug('add_group returning %s'%groupiter,5)
        return groupiter

    #def change_group (self, name,
    def delete_iters (self, *iters, **kwargs):
        """kwargs can have is_undo"""
        is_undo = kwargs.get('is_undo',False)
        refs = []
        undo_info = []
        try:
            paths = [self.imodel.get_path(i) for i in iters]
        except TypeError:
            print 'Odd we are failing to get_paths for ',iters
            print 'Our undo stack looks like this...'
            print self.ingredient_editor_module.history
            raise
        for itr in iters:
            orig_ref = self.get_persistent_ref_from_iter(itr)
            # We don't want to add children twice, once as a
            # consequent of their parents and once because they've
            # been selected in their own right.
            parent = self.imodel.iter_parent(itr)
            parent_path =  parent and self.imodel.get_path(parent)
            if parent_path in paths:
                # If our parent is in the iters to be deleted -- we
                # don't need to delete it individual
                continue
            refs.append(orig_ref)
            deleted_dic,prev_ref,ing_obj = self._get_undo_info_for_iter_(itr)
            child = self.imodel.iter_children(itr)
            children = []
            if child:
                expanded = self.ingredient_editor_module.ingtree_ui.ingTree.row_expanded(
                    self.imodel.get_path(itr)
                    )
            else:
                expanded = False
            while child:
                children.append(self._get_undo_info_for_iter_(child))
                child = self.imodel.iter_next(child)
            undo_info.append((deleted_dic,prev_ref,ing_obj,children,expanded))
    
        u = Undo.UndoableObject(
            lambda *args: self.do_delete_iters(refs),
            lambda *args: self.do_undelete_iters(undo_info),
            self.ingredient_editor_module.history,
            widget=self.imodel,
            is_undo=is_undo
            )
        debug('IngredientController.delete_iters Performing deletion of %s'%refs,2)
        u.perform()

    def _get_prev_path_ (self, path):
        if path[-1]==0:
            if len(path)==1:
                prev_path = None
            else:
                prev_path = tuple(path[:-1])
        else:
            prev_path = path_next(path,-1)
        return prev_path

    def _get_undo_info_for_iter_ (self, iter):
        deleted_dic = self.get_rowdict(iter)
        path = self.imodel.get_path(iter)
        prev_path = self._get_prev_path_(path)
        if prev_path:
            prev_ref = self.get_persistent_ref_from_path(prev_path)
        else:
            prev_ref = None
        ing_obj = self.imodel.get_value(iter,0)
        return deleted_dic,prev_ref,ing_obj

    def do_delete_iters (self, iters):
        for ref in iters:
            i = self.get_iter_from_persistent_ref(ref)
            if not i: print 'Failed to get reference from',i
            else: self.imodel.remove(i)

    def do_undelete_iters (self, rowdicts_and_iters):
        for rowdic,prev_iter,ing_obj,children,expanded in rowdicts_and_iters:
            prev_iter = self.get_iter_from_persistent_ref(prev_iter)
            # If ing_obj is a string, then we are a group
            if ing_obj and type(ing_obj) in types.StringTypes:
                itr = self.add_group(rowdic['amount'],prev_iter,fallback_on_append=False)
            elif type(ing_obj) == int or not ing_obj:        
                itr = self.add_ingredient_from_kwargs(prev_iter=prev_iter,
                                                      fallback_on_append=False,
                                                      placeholder=ing_obj,
                                                      **rowdic)
            #elif ing_obj not in self.ingredient_objects:
            #    # If we have an ingredient object, but it's not one we
            #    # recall, then we must be recalling the object from
            #    # before a deletion -- we'll 
            else:
                # Otherwise, we must have an ingredient object
                itr = iter = self.add_ingredient(ing_obj,prev_iter,
                                                 fallback_on_append=False,
                                                 is_undo=True)
                self.update_ingredient_row(iter,**rowdic)
            if children:
                first = True
                for rd,pi,io in children:
                    pi = self.get_iter_from_persistent_ref(pi)
                    if first:
                        gi = itr
                        pi = None
                        first = False
                    else:
                        gi = None    
                    if io and type(io) not in [str,unicode,int] and not isinstance(io,RecRef):
                        itr = self.add_ingredient(io,
                                                  group_iter=gi,
                                                  prev_iter=pi,
                                                  fallback_on_append=False,
                                                  is_undo = True)
                        self.update_ingredient_row(itr,**rd)
                    else:
                        itr = self.add_ingredient_from_kwargs(group_iter=gi,
                                                              prev_iter=pi,
                                                              fallback_on_append=False,
                                                              **rd)
                        self.imodel.set_value(itr,0,io)
            if expanded:
                self.ingredient_editor_module.ingtree_ui.ingTree.expand_row(self.imodel.get_path(itr),True)

    # Get a dictionary describing our current row
    def get_rowdict (self, iter):
        d = {}
        for k,n in [('amount',1),
                    ('unit',2),
                    ('item',3),
                    ('optional',4),
                    ]:
            d[k] = self.imodel.get_value(iter,n)
        ing_obj = self.imodel.get_value(iter,0)
        self.get_extra_ingredient_attributes(
            ing_obj,
            d)
        return d

    @pluggable_method
    def get_extra_ingredient_attributes (self, ing_obj, ingdict):
        if not hasattr(ing_obj,'ingkey') or not ing_obj.ingkey:
            if ingdict['item']:
                ingdict['ingkey'] = ingdict['item'].split(';')[0]
        else:
            ingdict['ingkey'] = ing_obj.ingkey

    # Get persistent references to items easily

    def get_persistent_ref_from_path (self, path):
        return self.get_persistent_ref_from_iter(
            self.imodel.get_iter(path)
            )

    def get_persistent_ref_from_iter (self, iter):
        uid = self.imodel.get_value(iter,0)
        return uid

    def get_path_from_persistent_ref (self, ref):
        itr = self.get_iter_from_persistent_ref(ref)
        if itr:
            return self.imodel.get_path(
                itr
                )
    
    #@debug_decorator
    def get_iter_from_persistent_ref (self, ref):
        try:
            if self.commited_items_converter.has_key(ref):
                ref = self.commited_items_converter[ref]
        except TypeError:
            # If ref is unhashable, we don't care
            pass
        itr = self.imodel.get_iter_first()
        while itr:
            v = self.imodel.get_value(itr,0)
            if v == ref or self.rg.rd.row_equal(v,ref):
                return itr
            child = self.imodel.iter_children(itr)
            if child:
                itr = child
            else:
                next = self.imodel.iter_next(itr)
                if next:
                    itr = next
                else:
                    parent = self.imodel.iter_parent(itr)
                    if parent:
                        itr = self.imodel.iter_next(parent)
                    else:
                        itr = None

    def commit_ingredients (self):
        """Commit ingredients as they appear in tree to database."""
        iter = self.imodel.get_iter_first()
        n = 0
        # Start with a list of all ingredient object - we'll eliminate
        # each object as we come to it in our tree -- any items not
        # eliminated have been deleted.
        deleted = self.ingredient_objects[:]
        
        # We use an embedded function rather than a simple loop so we
        # can recursively crawl our tree -- so think of commit_iter as
        # the inside of the loop, only better

        def commit_iter (iter, pos, group=None):
            ing = self.imodel.get_value(iter,0)
            # If ingredient is a string, than this is a group
            if type(ing) in [str,unicode]:
                group = self.imodel.get_value(iter,1)
                i = self.imodel.iter_children(iter)
                while i:
                    pos = commit_iter(i,pos,group)
                    i = self.imodel.iter_next(i)
                return pos
            # Otherwise, this is an ingredient...
            else:
                d = self.get_rowdict(iter)
                # Get the amount as amount and rangeamount
                if d['amount']:
                    amt,rangeamount = parse_range(d['amount'])
                    d['amount']=amt
                    if rangeamount: d['rangeamount']=rangeamount
                else:
                    d['amount']=None
                # Get category info as necessary
                if d.has_key('shop_cat'):
                    self.rg.sl.orgdic[d['ingkey']] = d['shop_cat']
                    del d['shop_cat']
                d['position']=pos
                d['inggroup']=group
                # If we are a recref...
                if isinstance(ing,RecRef):
                    d['refid'] = ing.refid
                # If we are a real, old ingredient
                if type(ing) != int and not isinstance(ing,RecRef):
                    for att in ['amount','unit','item','ingkey','position','inggroup','optional']:
                        # Remove all unchanged attrs from dict...
                        if hasattr(d,att):
                            if getattr(ing,att)==d[att]:
                                del d[att]
                    if ing in deleted:
                        # We have not been deleted...
                        deleted.remove(ing)
                    else:
                        # In this case, we have an ingredient object
                        # that is not reflected in our
                        # ingredient_object list. This means the user
                        # Deleted us, saved, and then clicked undo,
                        # resulting in the trace object. In this case,
                        # we need to set ing.deleted to False
                        d['deleted'] = False
                    if ing.deleted: # If somehow our object is
                                    # deleted... (shouldn't be
                                    # possible, but why not check!)
                        d['deleted']=False
                    if d:
                        self.ingredient_editor_module.rg.rd.modify_ing_and_update_keydic(ing,d)
                else:
                    d['recipe_id'] = self.ingredient_editor_module.current_rec.id
                    self.commited_items_converter[ing] = self.rg.rd.add_ing_and_update_keydic(d)
                    self.imodel.set_value(iter,0,self.commited_items_converter[ing])
                    # Add ourself to the list of ingredient objects so
                    # we will notice subsequent deletions.
                    self.ingredient_objects.append(self.commited_items_converter[ing])
                return pos+1
        # end commit iter

        while iter:
            n = commit_iter(iter,n)
            iter = self.imodel.iter_next(iter)
        # Now delete all deleted ings...  (We're not *really* deleting
        # them -- we're just setting a handy flag to delete=True. This
        # makes Undo faster. It also would allow us to allow users to
        # go back through their "ingredient Trash" if we wanted to put
        # in a user interface for them to do so.
        for i in deleted: self.ingredient_objects.remove(i)
        self.rg.rd.modify_ings(deleted,{'deleted':True})
