import os.path
from gourmet.gdebug import debug, TimeAction
import re, pickle, string, os.path, string
from gettext import gettext as _
import gourmet.gglobals
from gourmet import Undo, keymanager, convert, shopping
from gourmet.defaults import lang as defaults
import gourmet.nutrition.parser_data
import StringIO
from gourmet import ImageExtras

# This is our base class for rdatabase.  All functions needed by
# Gourmet to access the database should be defined here and
# implemented by subclasses.  This was designed around metakit, so
# Gourmet requires an object-attribute style syntax for accessing
# database information.  For the time being, this is built in
# throughout Gourmet. Non-metakit backends, such as sql, have to
# implement this syntax themselves (which is fine by me because that
# means I have abstracted ways to handle e.g. SQLite in the
# future). See PythonicSQL.py and other files for the glue between SQL
# and the object/attribute style required by Gourmet.

class RecData:

    """RecData is our base class for handling database connections.

    Subclasses implement specific backends, such as metakit, sqlite, etc."""
    # constants for determining how to get amounts when there are ranges.
    AMT_MODE_LOW = 0
    AMT_MODE_AVERAGE = 1
    AMT_MODE_HIGH = 2
    
    # MAGIC COLUMNS
    #
    # Each column in this list will be normalized. In the table defs,
    # it should be defined as an integer, but for all intents and
    # purposes, it will look like a string, thanks to some very dark
    # magic.
    NORMALIZED_COLS = ['ingkey',
                       'source',
                       'category',
                       'cuisine',
                       'unit',
                       'item',
                       'inggroup',
                       'foodgroup',
                       'word',
                       'shopcategory'
                       ]

    NORMALIZED_TABLES = [(k,[('id','int',['AUTOINCREMENT']),(k,'text',[])],k) for k in NORMALIZED_COLS]

    INGKEY_LOOKUP_TABLE_DESC = ('keylookup',
                                [('word','int',[]),
                                 ('item','int',[]),
                                 ('ingkey','int',[]),
                                 ('count','int',[])]
                                )

    RECIPE_TABLE_DESC = ('recipe',
                  [('id',"int",['AUTOINCREMENT']),
                   ('title',"text",[]),
                   ('instructions',"text",[]),
                   ('modifications',"text",[]),
                   ('cuisine',"int",[]),
                   ('rating',"int",[]),
                   ('description',"text",[]),
                   ('source',"int",[]),
                   ('preptime','int',[]),
                   ('cooktime','int',[]),
                   ('servings',"char(50)",[]),
                   ('image',"binary",[]),
                   ('thumb','binary',[]),
                   ('deleted','bool',[]),
                   ],
                         'id' # key
                         ) 
    CATEGORY_TABLE_DESC = ('categories',
                      [('id','int',[]),
                       ('category','int',[])]
                      )

    INGREDIENTS_TABLE_DESC=('ingredients',
                [('id','int',[]),
                 ('refid','int',[]),
                 ('unit','int',[]),
                 ('amount','float',[]),
                 ('rangeamount','float',[]),
                 ('item','int',[]),
                 ('ingkey','int',[]),
                 ('optional','bool',[]),
                 ('shopoptional','int',[]), #Integer so we can distinguish unset from False
                 ('inggroup','int',[]),
                 ('position','int',[]),
                 ('deleted','bool',[]),
                 ],
                )
    SHOPCATS_TABLE_DESC = ('shopcats',
                  [('ingkey','int',[]),
                   ('shopcategory','int',[]),
                   ('position','int',[])],
                  'ingkey' #key
                  )
    SHOPCATSORDER_TABLE_DESC = ('shopcatsorder',
                   [('shopcategory','int',[]),
                    ('position','int',[]),
                    ],
                   'shopcategory' #key
                   )
    PANTRY_TABLE_DESC = ('pantry',
                  [('ingkey','int',[]),
                   ('pantry','bool',[])],
                  'ingkey' #key
                  )
    DENSITY_TABLE_DESC = ("density",
                   [('dkey','char(150)',[]),
                    ('value','char(150)',[])],'dkey' #key
                   )
    CROSSUNITDICT_TABLE_DESC = ("crossunitdict",
                   [('cukey','char(150)',[]),
                    ('value','char(150)',[])],'cukey' #key
                   )
    UNITDICT_TABLE_DESC = ("unitdict",
                  [('ukey','char(150)',[]),
                   ('value','char(150)',[])],'ukey' #key
                  )
    CONVTABLE_TABLE_DESC = ("convtable",
                  [('ckey','char(150)',[]),
                   ('value','char(150)',[])],'ckey' #key
                  )
    
    NUTRITION_TABLE_DESC = (
        "nutrition",
        [(name,typ,[]) for lname,name,typ in gourmet.nutrition.parser_data.NUTRITION_FIELDS] + \
        [('foodgroup','int',[])]
        )
    NUTRITION_ALIASES_TABLE_DESC = (
        'nutritionaliases',
        [('ingkey','int',[]),
         ('ndbno','int',[]),],
        'ingkey')

    NUTRITION_CONVERSIONS = (
        'nutritionconversions',
        [('ingkey','int',[]),
         ('unit','int',[]), 
         ('factor','float',[]),],
        'ingkey')

    
    
    def __init__ (self):
        # hooks run after adding, modifying or deleting a recipe.
        # Each hook is handed the recipe, except for delete_hooks,
        # which is handed the ID (since the recipe has been deleted)
        self.add_hooks = []
        self.modify_hooks = []
        self.delete_hooks = []
        self.add_ing_hooks = []
        timer = TimeAction('initialize_connection + setup_tables',2)
        self.initialize_connection()
        self.setup_tables()        
        timer.end()

    # Basic setup functions

    def initialize_connection (self):
        """Initialize our database connection."""
        raise NotImplementedError

    def save (self):
        """Save our database (if we have a separate 'save' concept)"""
        pass

    def setup_tables (self):
        """Setup all of our tables by calling setup_table for each one.

        Subclasses should do any necessary adjustments/tweaking before calling
        this function."""
        self.normalizations={}
        for desc in self.NORMALIZED_TABLES:
            self.normalizations[desc[0]]=self.setup_table(*desc)
            
        self.rview = self._setup_table(*self.RECIPE_TABLE_DESC)
        self.iview = self._setup_table(*self.INGREDIENTS_TABLE_DESC)
        self.catview = self._setup_table(*self.CATEGORY_TABLE_DESC)
        self.iview_not_deleted = self.iview.select(deleted=False)
        self.iview_deleted = self.iview.select(deleted=True)
        self.ikview = self._setup_table(*self.INGKEY_LOOKUP_TABLE_DESC)
        self.sview = self._setup_table(*self.SHOPCATS_TABLE_DESC)
        self.scview = self._setup_table(*self.SHOPCATSORDER_TABLE_DESC)
        self.pview = self._setup_table(*self.PANTRY_TABLE_DESC)
        # converter items
        self.cdview = self._setup_table(*self.DENSITY_TABLE_DESC)
        self.cview = self._setup_table(*self.CONVTABLE_TABLE_DESC)
        self.cuview = self._setup_table(*self.CROSSUNITDICT_TABLE_DESC)
        self.uview = self._setup_table(*self.UNITDICT_TABLE_DESC)
        self.nview = self._setup_table(*self.NUTRITION_TABLE_DESC)
        self.naliasesview = self._setup_table(*self.NUTRITION_ALIASES_TABLE_DESC)
        self.nconversions = self._setup_table(*self.NUTRITION_CONVERSIONS)

    def _setup_table (self, *args,**kwargs):
        return NormalizedView(self.setup_table(*args,**kwargs),self,self.normalizations)
        
    def setup_table (self, name, data, key=None):
        """Create and return an object representing a table/view of our database.

        Name is the name of our table.
        Data is a list of tuples of column names and data types.
        Key is the column of the table that should be indexed.
        """
        raise NotImplementedError

    def run_hooks (self, hooks, *args):
        """A basic hook-running function. We use hooks to allow parts of the application
        to tag onto data-modifying events and e.g. update the display"""
        for h in hooks:
            t = TimeAction('running hook %s with args %s'%(h,args),3)
            h(*args)
            t.end()

    # basic DB access functions

    def fetch_one (self, table, *args, **kwargs):
        """Fetch one item from table and arguments"""
        # this is only a special method because metakit doesn't have
        # this functionality by default so we have to implement it by
        # hand here. Our PythonicSQL derivatives should have table
        # objects with fetch_one methods, which we'll use here.
        return table.fetch_one(*args,**kwargs)

    def search (self, table, colname, text, exact=0, use_regexp=True):

        """Search colname of table for text, optionally using regular
        expressions and/or requiring an exact match."""

        raise NotImplementedError
    

    def filter (self, table, func):
        """Return a table representing filtered with func.

        func is called with each row of the table.
        """
        raise NotImplementedError

    def get_unique_values (self, colname,table=None):
        """Get list of unique values for column in table."""
        if not table: table=self.rview
        if self.normalizations.has_key(colname):
            lst = [getattr(o,colname) for o in self.normalizations[colname]]
        else:
            lst = []
            def add_to_dic (row):
                a=getattr(row,colname)
                if not a in lst: lst.append(a)
            table.filter(add_to_dic)
        if defaults.fields.has_key(colname):
            for v in defaults.fields[colname]:
                if not v in lst: lst.append(v)
        # Hideous hackery ahead... ack!
        if colname=='category':
            new_lst = []
            for i in lst:
                if i.find(',')>0:
                    new_lst.extend([ii.strip() for ii in i.split(',')])
                else:
                    new_lst.append(i)
            lst = new_lst
        return lst

    # Metakit has no AUTOINCREMENT, so it has to do special magic here
    def increment_field (self, table, field):
        """Increment field in table, or return None if the DB will do
        this automatically.
        """
        return None

    def delete_by_criteria (self, table, criteria):
        """Table is our table.
        Criteria is a dictionary of critiera to delete by.
        """
        raise NotImplementedError

    # Metakit has no AUTOINCREMENT, so it has to do special magic here
    def increment_field (self, table, field):
        """Increment field in table, or return None if the DB will do
        this automatically.
        """
        return None

    # convenience DB access functions for working with ingredients,
    # recipes, etc.

    def delete_ing (self, ing):
        """Delete ingredient permanently."""
        raise NotImplementedError

    def modify_rec (self, rec, dic):
        """Modify recipe based on attributes/values in dictionary.

        Return modified recipe.
        """
        self.validate_recdic(dic)
        debug('validating dictionary',3)
        if dic.has_key('category'):
            cats = dic['category'].split(', ')
            self.delete_by_criteria(self.catview,{'id':rec.id})
            for c in cats:
                self.do_add_cat({'id':rec.id,'category':c})
            del dic['category']
        debug('do modify rec',3)
        return self.do_modify_rec(rec,dic)
    
    def validate_recdic (self, recdic):
        if recdic.has_key('image') and not recdic.has_key('thumb'):
            # if we have an image but no thumbnail, we want to create the thumbnail.
            try:
                img = ImageExtras.get_image_from_string(recdic['image'])
                thumb = ImageExtras.resize_image(img,40,40)
                ofi = StringIO.StringIO()
                thumb.save(ofi,'JPEG')
                recdic['thumb']=ofi.getvalue()
                ofi.close()
            except:
                del recdic['image']
                print """Warning: gourmet couldn't recognize the image.

                Proceding anyway, but here's the traceback should you
                wish to investigate.
                """
                import traceback
                traceback.print_stack()
        for k,v in recdic.items():
            try:
                recdic[k]=v.strip()
            except:
                pass

    def modify_ings (self, ings, ingdict):
        # allow for the possibility of doing a smarter job changing
        # something for a whole bunch of ingredients...
        for i in ings: self.modify_ing(i,ingdict)

    def modify_ing (self, ing, ingdict):
        self.validate_ingdic(ingdict)
        if ing.item!=ingdict.get('item',ing.item) or ing.ingkey!=ingdict.get('ingkey',ing.ingkey):
            if ing.item and ing.ingkey:
                self.remove_ing_from_keydic(ing.item,ing.ingkey)
            self.add_ing_to_keydic(ingdict.get('item',ing.item),
                                   ingdict.get('ingkey',ing.ingkey))
        return self.do_modify_ing(ing,ingdict)

    # Lower level DB access functions -- hopefully subclasses can
    # stick to implementing these    

    def add_rec (self, dic):
        cats = []
        if dic.has_key('category'):
            cats = dic['category'].split(', ')
            del dic['category']
        self.validate_recdic(dic)
        try:
            ret = self.do_add_rec(dic)
        except:
            print 'Problem adding ',dic
            raise
        else:
            ID = ret.id
            for c in cats:
                self.do_add_cat({'id':ID,'category':c})
            return ret

    def add_ing (self, dic):
        self.validate_ingdic(dic)
        try:            
            if dic.has_key('item') and dic.has_key('ingkey'):
                self.add_ing_to_keydic(dic['item'],dic['ingkey'])
            return self.do_add_ing(dic)
        except:
            print 'Problem adding',dic
            raise

    def do_add_ing (self,dic):
        raise NotImplementedError

    def do_add_cat (self, dic):
        raise NotImplementedError

    def validate_ingdic (self,dic):
        """Do any necessary validation and modification of ingredient dictionaries."""
        pass

    def do_modify_rec (self, rec, dic):
        """This is what other DBs should subclass."""
        raise NotImplementedError

    def do_modify_ing (self, ing, ingdict):
        """modify ing based on dictionary of properties and new values."""
        #self.delete_ing(ing)
        #return self.add_ing(ingdict)
        for k,v in ingdict.items():
            if hasattr(ing,k):
                self.changed=True
                setattr(ing,k,v)
            else:
                debug("Warning: ing has no attribute %s (attempted to set value to %s" %(k,v),0)
        return ing

    def get_ings (self, rec):
        """Handed rec, return a list of ingredients.

        rec should be an ID or an object with an attribute ID)"""
        if hasattr(rec,'id'):
            id=rec.id
        else:
            id=rec
        return self.iview.select(id=id,deleted=False)

    def get_cats (self, rec):
        svw = self.catview.select(id=rec.id)
        cats =  [c.category or '' for c in svw]
        # hackery...
        while '' in cats:
            #print "wtf - there's an empty category for recipe ",rec.id
            cats.remove('')
        return cats

    def get_referenced_rec (self, ing):
        """Get recipe referenced by ingredient object."""
        if hasattr(ing,'refid') and ing.refid:
            rec = self.get_rec(ing.refid)
            if rec: return rec
        # otherwise, our reference is no use! Something's been
        # foobared. Unfortunately, this does happen, so rather than
        # screwing our user, let's try to look based on title/item
        # name (the name of the ingredient *should* be the title of
        # the recipe, though the user could change this)
        if hasattr(ing,'item'):
            recs=self.search(self.rview,'title',ing.item,exact=True,use_regexp=False)
            if len(recs)==0:
                self.modify_ing(ing,{'idref':recs[0].id})
                return recs[0]
            else:
                debug("""Warning: there is more than one recipe titled"%(title)s"
                and our id reference to %(idref)s failed to match any
                recipes.  We are going to assume recipe ID %(id)s is
                the correct one."""%{'title':ing.item,
                                     'idref':ing.refid,
                                     'id':recs[0].id},
                      0)
                return recs[0]

    def get_rec (self, id, rview=None):
        """Handed an ID, return a recipe object."""
        if rview:
            print 'handing get_rec an rview is deprecated'
            print 'Ignoring rview handed to get_rec'
        rview=self.rview
        return self.fetch_one(self.rview, id=id)

    def do_add_rec (self, rdict):
        """Add a recipe based on a dictionary of properties and values."""
        self.changed=True
        if not rdict.has_key('deleted'):
            rdict['deleted']=0
        if not rdict.has_key('id'):
            rdict['id']=self.new_id()
        try:
            debug('Adding recipe %s'%rdict, 4)
            self.rview.append(rdict)
            debug('Running add hooks %s'%self.add_hooks,2)
            if self.add_hooks: self.run_hooks(self.add_hooks,self.rview[-1])
            return self.rview[-1]
        except:
            debug("There was a problem adding recipe%s"%rdict,-1)
            raise

    def delete_rec (self, rec):
        """Delete recipe object rec from our database."""
        if type(rec)!=int: rec=rec.id
        debug('deleting recipe ID %s'%rec,0)
        self.delete_by_criteria(self.rview,{'id':rec})
        self.delete_by_criteria(self.catview,{'id':rec})
        self.delete_by_criteria(self.iview,{'id':rec})
        debug('deleted recipe ID %s'%rec,0)
        #raise NotImplementedError

    def new_rec (self):
        """Create and return a new, empty recipe"""
        blankdict = {'id':self.new_id(),
                     'title':_('New Recipe'),
                     #'servings':'4'}
                     }
        return self.add_rec(blankdict)


    def new_id (self):
        return self.increment_field('recipe','id')

    # Convenience functions for dealing with ingredients

    def order_ings (self, iview):
        """Handed a view of ingredients, we return an alist:
        [['group'|None ['ingredient1', 'ingredient2', ...]], ... ]
        """
        defaultn = 0
        groups = {}
        group_order = {}
        for i in iview:
            # defaults
            if not hasattr(i,'inggroup'):
                group=None
            else:
                group=i.inggroup
            if not hasattr(i,'position'):
                i.position=defaultn
                defaultn += 1
            if groups.has_key(group): 
                groups[group].append(i)
                # the position of the group is the smallest position of its members
                # in other words, positions pay no attention to groups really.
                if i.position < group_order[group]: group_order[group]=i.position
            else:
                groups[group]=[i]
                group_order[group]=i.position
        # now we just have to sort an i-listify
        def sort_groups (x,y):
            if group_order[x[0]] > group_order[y[0]]: return 1
            elif group_order[x[0]] == group_order[y[0]]: return 0
            else: return -1
        alist=groups.items()
        alist.sort(sort_groups)
        def sort_ings (x,y):
            if x.position > y.position: return 1
            elif x.position == y.position: return 0
            else: return -1
        for g,lst in alist:
            lst.sort(sort_ings)
        return alist

    def replace_ings (self, ingdicts):
        """Add a new ingredients and remove old ingredient list."""
        ## we assume (hope!) all ingdicts are for the same ID
        id=ingdicts[0]['id']
        debug("Deleting ingredients for recipe with ID %s"%id,1)
        #ings = self.get_ings(id)
        #for i in ings:
        #    debug("Deleting ingredient: %s"%i.ingredient,5)
        #    self.delete_ing(i)
        self.delete_by_criteria(self.iview,{'id':id})
        for ingd in ingdicts:
            self.add_ing(ingd)
    
    def ingview_to_lst (self, view):
        """Handed a view of ingredient data, we output a useful list.
        The data we hand out consists of a list of tuples. Each tuple contains
        amt, unit, key, alternative?"""
        for i in view:
            ret.append([self.get_amount(i), i.unit, i.ingkey,])
        return ret

    def get_amount (self, ing, mult=1):
        """Given an ingredient object, return the amount for it.

        Amount may be a tuple if the amount is a range, a float if
        there is a single amount, or None"""
        amt=getattr(ing,'amount')
        try:
            ramt = getattr(ing,'rangeamount')
        except:
            # this blanket exception is here for our lovely upgrade
            # which requires a working export with a out-of-date DB
            ramt = None
        if mult != 1:
            if amt: amt = amt * mult
            if ramt: ramt = ramt * mult
        if ramt:
            return (amt,ramt)
        else:
            return amt

    def get_amount_and_unit (self, ing, mult=1, conv=None,fractions=convert.FRACTIONS_ALL):
        """Return a tuple of strings representing our amount and unit.
        
        If we are handed a converter interface, we will adjust the
        units to make them readable.
        """
        amt=self.get_amount(ing,mult)
        unit=ing.unit
        ramount = None
        if type(amt)==tuple: amt,ramount = amt
        if conv:
            amt,unit = conv.adjust_unit(amt,unit)
            if ramount and unit != ing.unit:
                # if we're changing units... convert the upper range too
                ramount = ramount * conv.converter(ing.unit, unit)
        if ramount: amt = (amt,ramount)
        return (self._format_amount_string_from_amount(amt,fractions=fractions),unit)
        
    def get_amount_as_string (self,
                              ing,
                              mult=1,
                              fractions=convert.FRACTIONS_ALL
                              ):
        """Return a string representing our amount.
        If we have a multiplier, multiply the amount before returning it.        
        """
        amt = self.get_amount(ing,mult)
        return self._format_amount_string_from_amount(amt, fractions=fractions)

    def _format_amount_string_from_amount (self, amt, fractions=convert.FRACTIONS_ALL):
        """Format our amount string given an amount tuple.

        If you're thinking of using this function from outside, you
        should probably just use a convenience function like
        get_amount_as_string or get_amount_and_unit
        """
        if type(amt)==tuple:
            return "%s-%s"%(convert.float_to_frac(amt[0],fractions=fractions).strip(),
                            convert.float_to_frac(amt[1],fractions=fractions).strip())
        elif type(amt)==float:
            return convert.float_to_frac(amt,fractions=fractions)
        else: return ""

    def get_amount_as_float (self, ing, mode=1): #1 == self.AMT_MODE_AVERAGE
        """Return a float representing our amount.

        If we have a range for amount, this function will ignore the range and simply
        return a number.  'mode' specifies how we deal with the mode:
        self.AMT_MODE_AVERAGE means we average the mode (our default behavior)
        self.AMT_MODE_LOW means we use the low number.
        self.AMT_MODE_HIGH means we take the high number.
        """
        amt = self.get_amount(ing)
        if type(amt) in [float, type(None)]:
            return amt
        else:
            # otherwise we do our magic
            amt=list(amt)
            amt.sort() # make sure these are in order
            low,high=amt
            if mode==self.AMT_MODE_AVERAGE: return (low+high)/2.0
            elif mode==self.AMT_MODE_LOW: return low
            elif mode==self.AMT_MODE_HIGH: return high # mode==self.AMT_MODE_HIGH
            else:
                raise ValueError("%s is an invalid value for mode"%mode)
    
    def add_ing_to_keydic (self, item, key):
        if not item or not key: return
        row = self.fetch_one(self.ikview, item=item, ingkey=key)
        if row:
            row.count+=1
        else:
            self.ikview.append({'item':item,'ingkey':key,'count':1})
        # and add words...
        for w in re.split('\W+',item):
            w=w.lower().strip()
            row = self.fetch_one(self.ikview,word=w,ingkey=key)
            if row:
                row.count+=1
            else:
                self.ikview.append({'word':w,'ingkey':key,'count':1})

    def remove_ing_from_keydic (self, item, key):
        row = self.fetch_one(self.ikview,item=item,ingkey=key)
        if row:
            row.count -= 1
        for w in re.split('\W+',item):
            w=w.lower()
            row = self.fetch_one(self.ikview,item=item,ingkey=key)
            if row:
                row.count -= 1

    def ing_shopper (self, view):
        return mkShopper(self.ingview_to_lst(view))

    # functions to undoably modify tables 

    def get_dict_for_obj (self, obj, keys):
        orig_dic = {}
        for k in keys:
            if k=='category':
                v = ", ".join(self.get_cats(obj))
            else:
                v=getattr(obj,k)
            orig_dic[k]=v
        return orig_dic

    def undoable_modify_rec (self, rec, dic, history=[], get_current_rec_method=None,
                             select_change_method=None):
        """Modify our recipe and remember how to undo our modification using history."""
        orig_dic = self.get_dict_for_obj(rec,dic.keys())
        reundo_name = "Re_apply"
        reapply_name = "Re_apply "
        reundo_name += string.join(["%s <i>%s</i>"%(k,v) for k,v in orig_dic.items()])
        reapply_name += string.join(["%s <i>%s</i>"%(k,v) for k,v in dic.items()])
        redo,reundo=None,None
        if get_current_rec_method:
            def redo (*args):
                r=get_current_rec_method()
                odic = self.get_dict_for_obj(r,dic.keys())
                return ([r,dic],[r,odic])
            def reundo (*args):
                r = get_current_rec_method()
                odic = self.get_dict_for_obj(r,orig_dic.keys())
                return ([r,orig_dic],[r,odic])

        def action (*args,**kwargs):
            """Our actual action allows for selecting changes after modifying"""
            self.modify_rec(*args,**kwargs)
            if select_change_method:
                select_change_method(*args,**kwargs)
                
        obj = Undo.UndoableObject(action,action,history,
                                  action_args=[rec,dic],undo_action_args=[rec,orig_dic],
                                  get_reapply_action_args=redo,
                                  get_reundo_action_args=reundo,
                                  reapply_name=reapply_name,
                                  reundo_name=reundo_name,)
        obj.perform()

    def undoable_delete_recs (self, recs, history, make_visible=None):
        """Delete recipes by setting their 'deleted' flag to True and add to UNDO history."""
        def do_delete ():
            for rec in recs:
                debug('rec %s deleted=True'%rec.id,1)
                self.modify_rec(rec,{'deleted':True})
            if make_visible: make_visible(recs)
        def undo_delete ():
            for rec in recs:
                debug('rec %s deleted=False'%rec.id,1)
                self.modify_rec(rec,{'deleted':False})
            if make_visible: make_visible(recs)
        obj = Undo.UndoableObject(do_delete,undo_delete,history)
        obj.perform()

    def undoable_modify_ing (self, ing, dic, history, make_visible=None):
        """modify ingredient object ing based on a dictionary of properties and new values.

        history is our undo history to be handed to Undo.UndoableObject
        make_visible is a function that will make our change (or the undo or our change) visible.
        """
        orig_dic = self.get_dict_for_obj(ing,dic.keys())
        def do_action ():
            debug('undoable_modify_ing modifying %s'%dic,2)
            self.modify_ing(ing,dic)
            if make_visible: make_visible(ing,dic)
        def undo_action ():
            debug('undoable_modify_ing unmodifying %s'%orig_dic,2)
            self.modify_ing(ing,orig_dic)
            if make_visible: make_visible(ing,orig_dic)
        obj = Undo.UndoableObject(do_action,undo_action,history)
        obj.perform()
        
    def undoable_delete_ings (self, ings, history, make_visible=None):
        """Delete ingredients in list ings and add to our undo history."""
        def do_delete():
            for i in ings:
                i.deleted=True
            if make_visible:
                make_visible(ings)
        def undo_delete ():
            for i in ings: i.deleted=False
            if make_visible: make_visible(ings)
        obj = Undo.UndoableObject(do_delete,undo_delete,history)
        obj.perform()
    
    def get_default_values (self, colname):
        try:
            return defaults.fields[colname]
        except:
            return []

    
class RecipeManager (RecData):
    
    def __init__ (self):
        debug('recipeManager.__init__()',3)
        RecData.__init__(self)
        self.km = keymanager.KeyManager(rm=self)
        
    def key_search (self, ing):
        """Handed a string, we search for keys that could match
        the ingredient."""
        result=self.km.look_for_key(ing)
        if type(result)==type(""):
            return [result]
        elif type(result)==type([]):
            # look_for contains an alist of sorts... we just want the first
            # item of every cell.
            if len(result)>0 and result[0][1]>0.8:
                return map(lambda a: a[0],result)
            else:
                ## otherwise, we make a mad attempt to guess!
                k=self.km.generate_key(ing)
                l = [k]
                l.extend(map(lambda a: a[0],result))
                return l
        else:
            return None
            
    def ingredient_parser (self, s, conv=None, get_key=True):
        """Handed a string, we hand back a dictionary representing a parsed ingredient (sans recipe ID)"""
        debug('ingredient_parser handed: %s'%s,0)
        s = unicode(s) # convert to unicode so our ING MATCHER works properly
        s=s.strip("\n\t #*+-")
        debug('ingredient_parser handed: "%s"'%s,1)
        m=convert.ING_MATCHER.match(s)
        if m:
            debug('ingredient parser successfully parsed %s'%s,1)
            d={}
            g=m.groups()
            a,u,i=(g[convert.ING_MATCHER_AMT_GROUP],
                   g[convert.ING_MATCHER_UNIT_GROUP],
                   g[convert.ING_MATCHER_ITEM_GROUP])
            if a:
                asplit = convert.RANGE_MATCHER.split(a)
                if len(asplit)==2:
                    d['amount']=convert.frac_to_float(asplit[0].strip())
                    d['rangeamount']=convert.frac_to_float(asplit[1].strip())
                else:
                    d['amount']=convert.frac_to_float(a.strip())
            if u:
                if conv and conv.unit_dict.has_key(u.strip()):
                    # Don't convert units to our units!
                    d['unit']=u.strip()
                else:
                    # has this unit been used
                    prev_uses = self.normalizations['unit'].select(
                        unit=str(u.strip()))
                    if len(prev_uses)>0:
                        d['unit']=u
                    else:
                        # otherwise, unit is not a unit
                        i = u + i
            if i:
                optmatch = re.search('\s+\(?[Oo]ptional\)?',i)
                if optmatch:
                    d['optional']=True
                    i = i[0:optmatch.start()] + i[optmatch.end():]
                d['item']=i.strip()
                if get_key: d['ingkey']=self.km.get_key(i.strip())
            debug('ingredient_parser returning: %s'%d,0)
            return d
        else:
            debug("Unable to parse %s"%s,0)
            return None

    def ing_search (self, ing, keyed=None, rview=None, use_regexp=True, exact=False):
        """Search for an ingredient."""
        if not rview: rview = self.rview
        vw = self.joined_search(rview,self.iview,'ingkey',ing,use_regexp=use_regexp,exact=exact)
        if not keyed:
            vw2 = self.joined_search(rview,self.iview,'item',ing,use_regexp=use_regexp,exact=exact)
            if vw2 and vw: vw = vw.union(vw2)
            else: vw = vw2
        return vw

    def joined_search (self, table1, table2, search_by, search_str, use_regexp=True, exact=False, join_on='id'):
        raise NotImplementedError

    def ings_search (self, ings, keyed=None, rview=None, use_regexp=True, exact=False):
        """Search for multiple ingredients."""
        raise NotImplementedError

    def clear_remembered_optional_ings (self, recipe=None):
        """Clear our memories of optional ingredient defaults.

        If handed a recipe, we clear only for the recipe we've been
        given.

        Otherwise, we clear *all* recipes.
        """
        if recipe:
            vw = self.get_ings(recipe)
        else:
            vw = self.iview
        # this is ugly...
        vw1 = vw.select(shopoptional=1)
        vw2 = vw.select(shopoptional=2)
        for v in vw1,vw2:
            for i in v: self.modify_ing(i,{'shopoptional':0})

class mkConverter(convert.converter):
    def __init__ (self, db):
        self.db = db
        convert.converter.__init__(self)
    ## still need to finish this class and then
    ## replace calls to convert.converter with
    ## calls to rmetakit.mkConverter

    def create_conv_table (self):
        self.conv_table = dbDic('ckey','value',self.db.cview, self.db,
                                pickle_key=True)
        for k,v in defaults.CONVERTER_TABLE.items():
            if not self.conv_table.has_key(k):
                self.conv_table[k]=v

    def create_density_table (self):
        self.density_table = dbDic('dkey','value',
                                   self.db.cdview,self.db)
        for k,v in defaults.DENSITY_TABLE.items():
            if not self.density_table.has_key(k):
                self.density_table[k]=v

    def create_cross_unit_table (self):
        self.cross_unit_table=dbDic('cukey','value',self.db.cuview,self.db)
        for k,v in defaults.CROSS_UNIT_TABLE:
            if not self.cross_unit_table.has_key(k):
                self.cross_unit_table[k]=v

    def create_unit_dict (self):
        self.units = defaults.UNITS
        self.unit_dict=dbDic('ukey','value',self.db.uview,self.db)
        for itm in self.units:
            key = itm[0]
            variations = itm[1]
            self.unit_dict[key] = key
            for v in variations:
                self.unit_dict[v] = key
                
class dbDic:
    def __init__ (self, keyprop, valprop, view, db, pickle_key=False, pickle_val=True):
        """Create a dictionary interface to a database table."""
        self.pickle_key = pickle_key
        self.pickle_val = pickle_val
        self.vw = view
        self.kp = keyprop
        self.vp = valprop
        self.db = db
        self.just_got = {}

    def has_key (self, k):
        try:
            self.just_got = {k:self.__getitem__(k)}
            return True
        except:
            try:
                self.__getitem__(k)
                return True
            except:
                return False
        
    def __setitem__ (self, k, v):
        if self.pickle_key:
            k=pickle.dumps(k)
        if self.pickle_val: store_v=pickle.dumps(v)
        else: store_v = v
        row = self.vw.select(**{self.kp:k})
        if len(row)>0:
            setattr(row[0],self.vp,store_v)
        else:
            self.vw.append({self.kp:k,self.vp:store_v})
        self.db.changed=True
        return v
    
    def __getitem__ (self, k):
        if self.just_got.has_key(k): return self.just_got[k]
        if self.pickle_key:
            k=pickle.dumps(k)
        v = getattr(self.vw.select(**{self.kp:k})[0],self.vp)        
        if v and self.pickle_val:
            try:
                return pickle.loads(v)
            except:
                print "Problem unpickling ",v                
                raise
        else:
            return v
    
    def __repr__ (self):
        str = "<dbDic> {"
        for i in self.vw:
            if self.pickle_key:
                str += "%s"%pickle.loads(getattr(i,self.kp))
            else:
                str += getattr(i,self.kp)
            str += ":"
            if self.pickle_val:
                str += "%s"%pickle.loads(getattr(i,self.vp))
            else:
                str += "%s"%getattr(i,self.vp)
            str += ", "
        str += "}"
        return str

    def keys (self):
        ret = []
        for i in self.vw:
            ret.append(getattr(i,self.kp))
        return ret

    def values (self):
        ret = []
        for i in self.vw:
            val = getattr(i,self.vp)
            if val and self.pickle_val: val = pickle.loads(val)
            ret.append(val)
        return ret

    def items (self):
        ret = []
        for i in self.vw:
            key = getattr(i,self.kp)
            val = getattr(i,self.vp)
            if key and self.pickle_key:
                try:
                    key = pickle.loads(key)
                except:
                    print 'Problem unpickling key ',key
                    raise
            if val and self.pickle_val:
                try:
                    val = pickle.loads(val)
                except:
                    print 'Problem unpickling value ',val, ' for key ',key
                    raise 
            ret.append((key,val))
        return ret

# This Normalizer stuff is really metakit only for now...
import metakit
class Normalizer:
    def __init__ (self, rd, normdic):
        self.__rd__ = rd
        self.__normdic__ = normdic

    def str_to_int (self, k, v):
        if not v: return None
        k=str(k)
        v=str(v)
        normtable = self.__normdic__[k]
        row = self.__rd__.fetch_one(normtable,**{k:v})
        if row:
            return row.id
        else:
            n=self.__rd__.increment_field(normtable,'id')
            if n:
                normtable.append({'id':n,k:v})
                r = normtable[-1]
            else:
                normtable.append({k:v})
                r = normtable[-1]
            return r.id
        
    def int_to_str (self, k, v):
        if 0: return ""
        normtable = self.__normdic__[k]
        if type(v)!=int:
            print "int_to_str says: WTF are you handing me ",v,"for?"
        row = self.__rd__.fetch_one(normtable,id=v)
        if row:
            #print 'Magic ',v,'->',getattr(row,k)
            return getattr(row,k)
        elif v==0:
            return None
        else:
            print "That's odd, I couldn't find ",k,v,type(v)
            #metakit.dump(normtable)
            raise KeyError('%s %s does not exist!'%(k,v))
        
class NormalizedView (Normalizer):
    """Some magic to allow normalizing our tables without touching our
    reliance on simple attribute-style access to properties. With this
    beautiful magic, in other words, iview[0].ingkey will give us the
    key even though key is actually normalized through a separate table.
    Similarly, iview.select(ingkey='sugar') will do the proper magic.
    """
    def __init__ (self, view, rd, normdic):
        self.__view__ = view
        Normalizer.__init__(self, rd, normdic)
        self.__normdic__ = normdic

    def __iter__ (self):
        for i in self.__view__:
            yield NormalizedRow(i,self.__rd__,self.__normdic__)

    def __nonzero__ (self): return not not self.__view__

    def __str__ (self): return repr(self)
    
    def __getattr__ (self, attname):
        if attname == '__view__': return self.__view__
        if attname == '__normdic__': return self.__normdic__
        if attname == '__rd__': return self.__rd__
        if attname == '__repr__': return self.__repr__
        if attname == '__join_normed_prop__': return self.__join_normed_prop__
        if attname == '__normalize_dictionary__': return self.__normalize_dictionary__
        if attname == 'sort': return self.sort
        if attname == 'sortrev': return self.sortrev
        if attname == '__iter__': return self.__iter__
        try:
            base_att = getattr(self.__view__,attname)
        except AttributeError:
            print 'Odd ',self.__view__,'has no attribute',attname
            print 'We were called from: '
            import traceback
            traceback.print_exc()
            raise
        if callable(base_att):
            return self.wrap_callable(base_att)
        return base_att
        
    def __setattr__ (self, attname, val):
        if attname in ['__view__',
                       '__normdic__',
                       '__rd__',
                       '__repr__',
                       '__join_normed_prop__',
                       '__normalize_dictionary__',
                       'sort',
                       'sortrev',
                       '__iter__',
                       ]:
            self.__dict__[attname] = val
        else:
            setattr(self.__view__,val)

    def __normalize_dictionary__ (self, d):
        for k,v in d.items():
            if self.__normdic__.has_key(k) and type(v)!=int:
                d[k]=Normalizer.str_to_int(self,k,v)
            elif type(v)==bool: d[k]=int(v)
        return d

    def __getitem__ (self, n): return NormalizedRow(self.__view__[n], self.__rd__, self.__normdic__)
    def __getslice__ (self, a=None, b=None): return NormalizedView(self.__view__[a:b],self.__rd__,self.__normdic__)
    def __len__ (self): return len(self.__view__)

    def wrap_callable (self, f):
        """A meta-function -- we wrap up anything callable in a
        function that replaces arguments doing normalization as necessary.

        We also replace any views or rows that are to be returned with subviews of ourselves.
        """
        def _(*args,**kwargs):
            kwargs=self.__normalize_dictionary__(kwargs)
            for k,v in kwargs.items():
                if type(v)==dict: kwargs[k] = self.__normalize_dictionary__(v)
                if isinstance(v,NormalizedView): kwargs[k]=v.__view__
                if isinstance(v,NormalizedRow): kwargs[k]=v.__row__
            args = [type(a)==dict and self.__normalize_dictionary__(a) or a for a in args]
            args = [(isinstance(a,NormalizedView) and a.__view__) or a for a in args]
            args = [(isinstance(a,NormalizedRow) and a.__row__) or a for a in args]
            ret = f(*args,**kwargs)
            if type(ret)==metakit.RowRefType:
                return NormalizedRow(ret,self.__rd__,self.__normdic__)
            elif type(ret) in [metakit.ViewType, metakit.ViewerType, metakit.ROViewerType]:
                return NormalizedView(ret,self.__rd__,self.__normdic__)
            else:
                return ret
        return _

    def __repr__ (self): return '<Normalized %s>'%self.__view__

    def __join_normed_prop__ (self, prop, subvw=None):
        """Join in a normalized version of our property.

        Return the new property name.
        This is useful for e.g. sorting.

        The reason we can't simply use joins this way for everything
        is that these new joined props are read-only.
        """
        if not subvw: subvw=self.__view__
        normedprop = prop+'lookup'
        if not hasattr(subvw,normedprop):
            normtable = self.__normdic__[prop]
            normtable = normtable.rename(prop,normedprop)
            normtable = normtable.rename('id',prop)
            # do our join -- now we can search by our normedprop
            subvw = subvw.join(normtable,getattr(normtable,
                                                 prop),
                               outer=True)
        return subvw,normedprop
    
    def sort (self, prop):
        # we do some magic sorting...
        #if self.__normdic__.has_key(prop):
        #    prop = self.__join_normed_prop__(prop)
        #sorter = self.wrap_callable(self.__view__.sort)
        #return sorter(prop)
        # Regular sorting is failing for reasons I don't understand
        # So we're just going to use this as a shorthand for sortrev
        return self.sortrev([getattr(self.__view__,prop)],[])

    def sortrev (self, fprops, rprops):
        new_fprops = []
        subvw = self.__view__
        for prop in [p.name for p in fprops]:
            if self.__normdic__.has_key(prop):
                subvw,newprop = self.__join_normed_prop__(prop,subvw)
                new_fprops.append(getattr(subvw,newprop))
            else:
                new_fprops.append(getattr(subvw,prop))
        new_rprops = []
        for prop in [p.name for p in rprops]:
            if self.__normdic__.has_key(prop):
                subvw,newprop = self.__join_normed_prop__(prop,subvw)
                new_rprops.append(getattr(subvw,newprop))
            else:
                new_rprops.append(getattr(subvw,prop))
        sorter = self.wrap_callable(subvw.sortrev)
        return sorter(new_fprops,new_rprops)

class NormalizedRow (Normalizer):
    """Some magic to allow normalizing our tables."""
    def __init__ (self, row, rd, normdic):
        self.__row__ = row
        Normalizer.__init__(self,rd,normdic)

    def __getattr__ (self, attname):
        if attname == '__row__': return self.__row__
        if attname == '__normdic__': return self.__normdic__
        if attname == '__rd__': return self.__rd__
        if attname == '__repr__': return self.__repr__
        base_attr = getattr(self.__row__,attname)
        if self.__normdic__.has_key(attname):
            return Normalizer.int_to_str(self,attname,base_attr)
        elif type(base_attr) in [metakit.ViewType, metakit.ViewerType, metakit.ROViewerType]:
            return NormalizedView(base_attr,self.__rd__,self.__normdic__)
        elif type(base_attr)==metakit.RowRefType:
            return NormalizedRow(base_attr,self.__rd__,self.__normdic__)
        else:
            return base_attr

    def __setattr__ (self, attname, val):
        if attname in ['__normdic__','__row__','__rd__']:
            #print 'setting',attname,'->',val
            self.__dict__[attname]=val
            return
        if self.__normdic__.has_key(attname):
            #print 'norming'
            nval = Normalizer.str_to_int(self,attname,val)
            #print 'normed ',val,'->',nval
            #print 'setting ',self.__row__,attname,'->',nval
            setattr(self.__row__,
                    attname,
                    nval
                    )
            #print 'set!'
        else:
            setattr(self.__row__,attname,val)

    def __repr__ (self): return '<Normalized %s>'%self.__row__
                    
                         
