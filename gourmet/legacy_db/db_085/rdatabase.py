import os.path
from gourmet.gdebug import debug, TimeAction
import re, pickle, string, os.path, string
from gettext import gettext as _
import gourmet.gglobals
from gourmet import Undo, keymanager, convert, shopping
from gourmet.defaults import lang as defaults

# This is our base class for rdatabase.  All functions needed by
# Gourmet to access the database should be defined here and
# implemented by subclasses.  This was designed around metakit, so
# Gourmet requires an object-attribute style syntax for accessing
# database information.  For the time being, this is built in
# throughout Gourmet. Non-metakit backends, such as sql, have to
# implement this syntax themselves (which is fine by me because that
# means I have abstracted ways to handle e.g. SQLite in the future). See
# PythonicSQL.py and other files for the glue between SQL and the object/attribute
# style required by Gourmet.

class RecData:

    """RecData is our base class for handling database connections.

    Subclasses implement specific backends, such as metakit, sqlite, etc."""
    # constants for determining how to get amounts when there are ranges.
    AMT_MODE_LOW = 0
    AMT_MODE_AVERAGE = 1
    AMT_MODE_HIGH = 2
    
    RECIPE_TABLE_DESC = ('recipe',
                  [('id',"char(75)"),
                   ('title',"text"),
                   ('instructions',"text"),
                   ('modifications',"text"),
                   ('cuisine',"text"),
                   ('rating',"text"),
                   ('description',"text"),
                   ('category',"text"),
                   ('source',"text"),
                   ('preptime',"char(50)"),
                   ('cooktime',"char(50)"),                                       
                   ('servings',"char(50)"),
                   ('image',"binary"),
                   ('thumb','binary'),
                   ('deleted','bool'),
                   ],                   #'id' # key
                         ) 
    INGREDIENTS_TABLE_DESC=('ingredients',
                [('id','char(75)'),
                 ('refid','char(75)'),
                 ('unit','text'),
                 ('amount','float'),
                 ('rangeamount','float'),
                 ('item','text'),
                 ('ingkey','char(200)'),
                 ('optional','bool'),
                 ('shopoptional','int'), #Integer so we can distinguish unset from False
                 ('inggroup','char(200)'),
                 ('position','int'),
                 ('deleted','bool'),
                 ],
                )
    SHOPCATS_TABLE_DESC = ('shopcats',
                  [('shopkey','char(50)'),
                   ('category','char(200)'),
                   ('position','int')],
                  'shopkey' #key
                  )
    SHOPCATSORDER_TABLE_DESC = ('shopcatsorder',
                   [('category','char(50)'),
                    ('position','int'),
                    ],
                   'category' #key
                   )
    PANTRY_TABLE_DESC = ('pantry',
                  [('itm','char(200)'),
                   ('pantry','char(10)')],
                  'itm' #key
                  )
    CATEGORIES_TABLE_DESC = ("categories",
                     [('id','char(200)'),
                      ('type','char(100)'),
                      ('description','text')], 'id' #key
                     )
    DENSITY_TABLE_DESC = ("density",
                   [('dkey','char(150)'),
                    ('value','char(150)')],'dkey' #key
                   )
    CROSSUNITDICT_TABLE_DESC = ("crossunitdict",
                   [('cukey','char(150)'),
                    ('value','char(150)')],'cukey' #key
                   )
    UNITDICT_TABLE_DESC = ("unitdict",
                  [('ukey','char(150)'),
                   ('value','char(150)')],'ukey' #key
                  )
    CONVTABLE_TABLE_DESC = ("convtable",
                  [('ckey','char(150)'),
                   ('value','char(150)')],'ckey' #key
                  )
    
    def __init__ (self):
        timer = TimeAction('initialize_connection + setup_tables',0)        
        self.initialize_connection()
        self.setup_tables()        
        timer.end()
        self.top_id = {'r': 1}
        # hooks run after adding, modifying or deleting a recipe.
        # Each hook is handed the recipe, except for delete_hooks,
        # which is handed the ID (since the recipe has been deleted)
        self.add_hooks = []
        self.modify_hooks = []
        self.delete_hooks = []
        self.add_ing_hooks = []

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
        self.recipe_table = self.setup_table(*self.RECIPE_TABLE_DESC)
        self.ingredients_table = self.setup_table(*self.INGREDIENTS_TABLE_DESC)
        self.ingredients_table_not_deleted = self.ingredients_table.select(deleted=False)
        self.ingredients_table_deleted = self.ingredients_table.select(deleted=True)
        self.shopcats_table = self.setup_table(*self.SHOPCATS_TABLE_DESC)
        self.shopcatsorder_table = self.setup_table(*self.SHOPCATSORDER_TABLE_DESC)
        self.pantry_table = self.setup_table(*self.PANTRY_TABLE_DESC) 
        self.metaview = self.setup_table(*self.CATEGORIES_TABLE_DESC)
        # converter items
        self.density_table = self.setup_table(*self.DENSITY_TABLE_DESC)
        self.convtable_table = self.setup_table(*self.CONVTABLE_TABLE_DESC)
        self.crossunitdict_table = self.setup_table(*self.CROSSUNITDICT_TABLE_DESC)
        self.unitdict_table = self.setup_table(*self.UNITDICT_TABLE_DESC)
        
    def setup_table (self, name, data, key):
        """Create and return an object representing a table/view of our database.

        Name is the name of our table.
        Data is a list of tuples of column names and data types.
        Key is the column of the table that should be indexed.
        """
        raise NotImplementedError

    def run_hooks (self, hooks, *args):
        for h in hooks:
            debug('running hook %s with args %s'%(h,args),3)
            h(*args)

    def get_dict_for_obj (self, obj, keys):
        orig_dic = {}
        for k in keys:
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

    def modify_rec (self, rec, dict):
        """Modify recipe 'rec' based on a dictionary of properties and new values."""
        raise NotImplementedError

    def search (self, table, colname, text, exact=0, use_regexp=True):

        """Search colname of table for text, optionally using regular
        expressions and/or requiring an exact match."""

        raise NotImplementedError

    def get_default_values (self, colname):
        try:
            return defaults.fields[colname]
        except:
            return []

    def get_unique_values (self, colname,table=None):
        if not table: table=self.recipe_table
        dct = {}
        if defaults.fields.has_key(colname):
            for v in defaults.fields[colname]:
                dct[v]=1
        def add_to_dic (row):
            a=getattr(row,colname)
            if type(a)==type(""):
                for i in a.split(","):
                    dct[i.strip()]=1
            else:
                dct[a]=1
        table.filter(add_to_dic)
        return dct.keys()

    def get_ings (self, rec):
        """Handed rec, return a list of ingredients.

        rec should be an ID or an object with an attribute ID)"""
        if hasattr(rec,'id'):
            id=rec.id
        else:
            id=rec
        return self.ingredients_table.select(id=id,deleted=False)

    def order_ings (self, ingredients_table):
        """Handed a view of ingredients, we return an alist:
        [['group'|None ['ingredient1', 'ingredient2', ...]], ... ]
        """
        defaultn = 0
        groups = {}
        group_order = {}
        for i in ingredients_table:
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

    def ingview_to_lst (self, view):
        """Handed a view of ingredient data, we output a useful list.
        The data we hand out consists of a list of tuples. Each tuple contains
        amt, unit, key, alternative?"""
        for i in view:
            ret.append([self.get_amount(i), i.unit, i.ingkey,])
        return ret
    
    def ing_shopper (self, view):
        return mkShopper(self.ingview_to_lst(view))

    def get_amount (self, ing, mult=1):
        """Given an ingredient object, return the amount for it.

        Amount may be a tuple if the amount is a range, a float if
        there is a single amount, or None"""
        amt=getattr(ing,'amount')
        ramt = getattr(ing,'rangeamount')
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
                ramount = ramount * conv.Converter(ing.unit, unit)
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
            recs=self.search(self.recipe_table,'title',ing.item,exact=True,use_regexp=False)
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
    
    def get_rec (self, id, recipe_table=None):
        """Handed an ID, return a recipe object."""
        if recipe_table:
            print 'handing get_rec an recipe_table is deprecated'
            print 'Ignoring recipe_table handed to get_rec'
        recipe_table=self.recipe_table
        s = recipe_table.select(id=id)
        if len(s)>0:
            return recipe_table.select(id=id)[0]
        else:
            return None

    def add_rec (self, rdict):
        """Add a recipe based on a dictionary of properties and values."""
        self.changed=True
        t = TimeAction('rdatabase.add_rec - checking keys',3)
        if not rdict.has_key('deleted'):
            rdict['deleted']=0
        if not rdict.has_key('id'):
            rdict['id']=self.new_id()
        t.end()
        try:
            debug('Adding recipe %s'%rdict, 4)
            t = TimeAction('rdatabase.add_rec - recipe_table.append(rdict)',3)
            self.recipe_table.append(rdict)
            t.end()
            debug('Running add hooks %s'%self.add_hooks,2)
            if self.add_hooks: self.run_hooks(self.add_hooks,self.recipe_table[-1])
            return self.recipe_table[-1]
        except:
            debug("There was a problem adding recipe%s"%rdict,-1)
            raise

    def delete_rec (self, rec):
        """Delete recipe object rec from our database."""
        raise NotImplementedError

    def undoable_delete_recs (self, recs, history, make_visible=None):
        """Delete recipes by setting their 'deleted' flag to True and add to UNDO history."""
        def do_delete ():
            for rec in recs: rec.deleted = True
            if make_visible: make_visible(recs)
        def undo_delete ():
            for rec in recs: rec.deleted = False
            if make_visible: make_visible(recs)
        obj = Undo.UndoableObject(do_delete,undo_delete,history)
        obj.perform()

    def new_rec (self):
        """Create and return a new, empty recipe"""
        blankdict = {'id':self.new_id(),
                     'title':_('New Recipe'),
                     #'servings':'4'}
                     }
        return self.add_rec(blankdict)

    def new_id (self, base="r"):
        """Return a new unique ID. Possibly, we can have a base"""
        if self.top_id.has_key(base):
            start = self.top_id[base]
            n = start + 1
        else:
            n = 0
        while self.recipe_table.find(id=self.format_id(n, base)) > -1 or self.ingredients_table.find(id=self.format_id(n, base)) > -1:
            # if the ID exists, we keep incrementing
            # until we find a unique ID
            n += 1 
        # every time we're called, we increment out record.
        # This way, if party A asks for an ID and still hasn't
        # committed a recipe by the time party B asks for an ID,
        # they'll still get unique IDs.
        self.top_id[base]=n
        return self.format_id(n, base)

    def format_id (self, n, base="r"):
        return base+str(n)

    def add_ing (self, ingdict):
        """Add ingredient to ingredients_table based on ingdict and return
        ingredient object. Ingdict contains:
        id: recipe_id
        unit: unit
        item: description
        key: keyed descriptor
        alternative: not yet implemented (alternative)
        #optional: yes|no
        optional: True|False (boolean)
        position: INTEGER [position in list]
        refid: id of reference recipe. If ref is provided, everything
               else is irrelevant except for amount.
        """
        self.changed=True        
        debug('adding to ingredients_table %s'%ingdict,3)
        timer = TimeAction('rdatabase.add_ing 2',5)
        if ingdict.has_key('amount') and not ingdict['amount']: del ingdict['amount']
        self.ingredients_table.append(ingdict)
        timer.end()
        debug('running ing hooks %s'%self.add_ing_hooks,3)
        timer = TimeAction('rdatabase.add_ing 3',5)
        if self.add_ing_hooks: self.run_hooks(self.add_ing_hooks, self.ingredients_table[-1])
        timer.end()
        debug('done with ing hooks',3)
        return self.ingredients_table[-1]

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
        
    def modify_ing (self, ing, ingdict):
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

    def replace_ings (self, ingdicts):
        """Add a new ingredients and remove old ingredient list."""
        ## we assume (hope!) all ingdicts are for the same ID
        id=ingdicts[0]['id']
        debug("Deleting ingredients for recipe with ID %s"%id,1)
        ings = self.get_ings(id)
        for i in ings:
            debug("Deleting ingredient: %s"%i.ingredient,5)
            self.delete_ing(i)
        for ingd in ingdicts:
            self.add_ing(ingd)

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

    def delete_ing (self, ing):
        """Delete ingredient permanently."""
        raise NotImplementedError
    
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
        """Handed a string, we hand back a dictionary (sans recipe ID)"""
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
                    d['unit']=conv.unit_dict[u.strip()]
                else:
                    d['unit']=u.strip()
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

    def ing_search (self, ing, keyed=None, recipe_table=None, use_regexp=True, exact=False):
        """Search for an ingredient."""
        raise NotImplementedError
    
    def ings_search (self, ings, keyed=None, recipe_table=None, use_regexp=True, exact=False):
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
            vw = self.ingredients_table
        # this is ugly...
        vw1 = vw.select(shopoptional=1)
        vw2 = vw.select(shopoptional=2)
        for v in vw1,vw2:
            for i in v: self.modify_ing(i,{'shopoptional':0})

class mkConverter(convert.Converter):
    def __init__ (self, db):
        self.db = db
        convert.Converter.__init__(self)
    ## still need to finish this class and then
    ## replace calls to convert.converter with
    ## calls to rmetakit.mkConverter

    def create_conv_table (self):
        self.conv_table = dbDic('ckey','value',self.db.convtable_table, self.db,
                                pickle_key=True)
        for k,v in defaults.CONVERTER_TABLE.items():
            if not self.conv_table.has_key(k):
                self.conv_table[k]=v

    def create_density_table (self):
        self.density_table = dbDic('dkey','value',
                                   self.db.density_table,self.db)
        for k,v in defaults.DENSITY_TABLE.items():
            if not self.density_table.has_key(k):
                self.density_table[k]=v

    def create_cross_unit_table (self):
        self.cross_unit_table=dbDic('cukey','value',self.db.crossunitdict_table,self.db)
        for k,v in defaults.CROSS_UNIT_TABLE:
            if not self.cross_unit_table.has_key(k):
                self.cross_unit_table[k]=v

    def create_unit_dict (self):
        self.units = defaults.UNITS
        self.unit_dict=dbDic('ukey','value',self.db.unitdict_table,self.db)
        for itm in self.units:
            key = itm[0]
            variations = itm[1]
            self.unit_dict[key] = key
            for v in variations:
                self.unit_dict[v] = key
                
class dbDic:
    def __init__ (self, keyprop, valprop, view, db, pickle_key=False):
        """Create a dictionary interface to a database table."""
        self.pickle_key = pickle_key
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
        row = self.vw.select(**{self.kp:k})
        if len(row)>0:
            setattr(row[0],self.vp,pickle.dumps(v))
        else:
            self.vw.append({self.kp:k,self.vp:pickle.dumps(v)})
        self.db.changed=True
        return v
    
    def __getitem__ (self, k):
        if self.just_got.has_key(k): return self.just_got[k]
        if self.pickle_key:
            k=pickle.dumps(k)
        t=TimeAction('dbdict getting from db',5)
        v = getattr(self.vw.select(**{self.kp:k})[0],self.vp)        
        t.end()
        if v:
            try:
                return pickle.loads(v)
            except:
                print "Problem unpickling ",v                
                raise
        else:
            return None
    
    def __repr__ (self):
        str = "<dbDic> {"
        for i in self.vw:
            if self.pickle_key:
                str += "%s"%pickle.loads(getattr(i,self.kp))
            else:
                str += getattr(i,self.kp)
            str += ":"
            str += "%s"%pickle.loads(getattr(i,self.vp))
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
            if val: val = pickle.loads(val)
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
            if val:
                try:
                    val = pickle.loads(val)
                except:
                    print 'Problem unpickling value ',val, ' for key ',key
                    print """Fearlessly, stupidly pushing forward!
                    (This may help us with corrupt data, but this
                    shouldn't be a normal part of our business).
                    """
            ret.append((key,val))
        return ret
