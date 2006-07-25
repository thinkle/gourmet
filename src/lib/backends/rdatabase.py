import os.path
from gourmet.gdebug import debug, TimeAction
import re, pickle, string, os.path, string, time
from gettext import gettext as _
import gourmet.gglobals
from gourmet import Undo, keymanager, convert, shopping
from gourmet.defaults import lang as defaults
import gourmet.nutrition.parser_data
import StringIO
from gourmet import ImageExtras
import unittest

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

    INFO_TABLE_DESC = ('info',
                  [('version_super','int',[]), # three part version numbers 2.1.10, etc. 1.0.0
                   ('version_major','int',[]),
                   ('version_minor','int',[]),
                   ('last_access','int',[])
                   ])

    INGKEY_LOOKUP_TABLE_DESC = ('keylookup',
                                 [('word','text',[]),
                                  ('item','text',[]),
                                  ('ingkey','text',[]),
                                  ('count','int',[])]
                                 )
    
    RECIPE_TABLE_DESC = ('recipe',
                  [('id',"int",['AUTOINCREMENT']),
                   ('title',"text",[]),
                   ('instructions',"text",[]),
                   ('modifications',"text",[]),
                   ('cuisine',"text",[]),
                   ('rating','int',[]),
                   ('description',"text",[]),
                   ('source',"text",[]),
                   ('preptime','int',[]),
                   ('cooktime','int',[]),
                   ('servings','float',[]),
                   ('image',"binary",[]),
                   ('thumb','binary',[]),
                   ('deleted','bool',[]),
                   ],
                         'id' # key
                         ) 
    CATEGORY_TABLE_DESC = ('categories',
                      [('id','int',[]), #recipe ID
                       ('category','text',[])] # Category ID
                      )

    INGREDIENTS_TABLE_DESC = ('ingredients',
                [('id','int',[]),
                 ('refid','int',[]),
                 ('unit','text',[]),
                 ('amount','float',[]),
                 ('rangeamount','float',[]),
                 ('item','text',[]),
                 ('ingkey','text',[]),
                 ('optional','bool',[]),
                 ('shopoptional','int',[]), #Integer so we can distinguish unset from False
                 ('inggroup','text',[]),
                 ('position','int',[]),
                 ('deleted','bool',[]),
                 ],
                )

    SHOPCATS_TABLE_DESC = ('shopcats',
                  [('ingkey','text',[]),
                   ('shopcategory','text',[]),
                   ('position','int',[])],
                  'ingkey' #key
                  )
    SHOPCATSORDER_TABLE_DESC = (
        'shopcatsorder',[('shopcategory','text',[]),
                         ('position','int',[]),
                         ],
        'shopcategory' #key
                   )
    PANTRY_TABLE_DESC = ('pantry',
                  [('ingkey','text',[]),
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
        [(name,
          typ,
          (name=='ndbno'
           and ['AUTOINCREMENT']
           or [])
          ) for lname,name,typ in gourmet.nutrition.parser_data.NUTRITION_FIELDS] + \
        [('foodgroup','text',[])],
        'ndbno'
        )

    NUTRITION_WEIGHT_TABLE_DESC = (
        'usda_weights',
        [(name,typ,[]) for lname,name,typ in gourmet.nutrition.parser_data.WEIGHT_FIELDS]
        )
    
    NUTRITION_ALIASES_TABLE_DESC = (
        'nutritionaliases',
        [('ingkey','text',[]),
         ('ndbno','int',[]),
         ('density_equivalent','char(20)',[]),
         ],
        'ingkey')

    NUTRITION_CONVERSIONS = (
        'nutritionconversions',
        [('ingkey','text',[]),
         ('unit','text',[]), 
         ('factor','float',[]),],
        )
    
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
        row = self.fetch_one(self.infoview)
        if row:
            self.do_modify(
                self.infoview,
                row,
                {'last_access':time.time()}
                )
        else:
            self.do_add(
                self.infoview,
                {'last_access':time.time()}
                )
        pass

    def setup_tables (self):
        """Setup all of our tables by calling setup_table for each one.

        Subclasses should do any necessary adjustments/tweaking before calling
        this function."""
        self.infoview = self._setup_table(*self.INFO_TABLE_DESC) # For storing version info...
        self.rview = self._setup_table(*self.RECIPE_TABLE_DESC)
        self.iview = self._setup_table(*self.INGREDIENTS_TABLE_DESC)
        self.catview = self._setup_table(*self.CATEGORY_TABLE_DESC)
        #self.iview_not_deleted = self.iview.select(deleted=False)
        #self.iview_deleted = self.iview.select(deleted=True)
        self.ikview = self._setup_table(*self.INGKEY_LOOKUP_TABLE_DESC)
        self.sview = self.setup_table(*self.SHOPCATS_TABLE_DESC)
        self.scview = self.setup_table(*self.SHOPCATSORDER_TABLE_DESC)
        self.pview = self.setup_table(*self.PANTRY_TABLE_DESC)
        # converter items
        self.cdview = self._setup_table(*self.DENSITY_TABLE_DESC)
        self.cview = self._setup_table(*self.CONVTABLE_TABLE_DESC)
        self.cuview = self._setup_table(*self.CROSSUNITDICT_TABLE_DESC)
        self.uview = self._setup_table(*self.UNITDICT_TABLE_DESC)
        self.nview = self._setup_table(*self.NUTRITION_TABLE_DESC)
        # Don't normalize this one!
        self.nwview = self.setup_table(*self.NUTRITION_WEIGHT_TABLE_DESC)
        self.naliasesview = self._setup_table(*self.NUTRITION_ALIASES_TABLE_DESC)
        self.nconversions = self._setup_table(*self.NUTRITION_CONVERSIONS)

    def update_version_info (self, version_string):
        """Report our version to the database.

        If necessary, we'll do some version-dependent updates to the GUI
        """
        stored_info = self.fetch_one(self.infoview)
        if not stored_info:
            # Default info -- the last version before we added the
            # version tracker...
            self.do_add(self.infoview,
                        {'version_super':0,
                         'version_major':11,
                         'version_minor':0})
            stored_info = self.fetch_one(self.infoview)            
        current_super,current_major,current_super = [int(s) for s in version_string.split('.')]
        ### Code for updates between versions...
        
        # Version < 0.11.4 -> version >= 0.11.4... fix up screwed up ikview tables...
        # We don't actually do this yet... (FIXME)
        if False and current_super == 0 and current_major <= 11 and current_minor <= 3:
            # Drop ikview table, which wasn't being properly kept up
            # to date...
            self.delete_by_criteria(self.ikview) 
            # And update it in accord with current ingredients (less
            # than an ideal decision, alas)
            for ingredient in self.fetch_all(self.iview):
                self.add_ing_to_keydic(ingredient.item,ingredient.ingkey)

        ### End of code for updates between versions...
        if (current_super!=stored_info.version_super
            or
            current_major!=stored_info.version_major
            or
            current_minor!=stored_info.version_minor
            ):
            self.do_modify(
                self.infoview,
                {'version_super':current_super,
                 'version_major':current_major,
                 'version_minor':current_minor,}
                )

    def _setup_table (self, *args,**kwargs):
        """Do any magic needed for automagic norming of tables
        """
        # See rmetakit.py and rsqlite.py for examples of normalizing magic.
        return self.setup_table(*args,**kwargs)
        
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

    # Metakit-convenience method (this is here and not in rmetakit
    # because we've reimplemented metakit badness in many of our SQL
    # modules
    def sort_by (self, table, sort_by):
        """Take a list of sorting directives in a normal form and do
        metakit's weird-ass thing with them.

        Normal form is

        (column_name,1) - ascending
        (column_name,-1) - descening
        """
        all = []
        rev = []
        for s in sort_by:
            prop = getattr(table,s[0])
            all.append(prop)
            if s[1]<0: rev.append(prop)
        return table.sortrev(all,rev)
            
    # basic DB access functions

    def fetch_all (self, table, sort_by=[], **criteria):
        if criteria:
            ret =  table.select(**criteria)
        if sort_by:
            return self.sort_by(ret,sort_by)
        else:
            return ret

    def fetch_one (self, table, *args, **kwargs):
        """Fetch one item from table and arguments"""
        # this is only a special method because metakit doesn't have
        # this functionality by default so we have to implement it by
        # hand here. Our PythonicSQL derivatives should have table
        # objects with fetch_one methods, which we'll use here.
        return table.fetch_one(*args,**kwargs)

    def fetch_count (self, table, column, sort_by=[],**criteria):
        """Return a counted view of the table, with the count stored in the property 'count'"""
        ret =  table.counts(getattr(table,column),'count')
        if sort_by: return self.sort_by(ret,sort_by)
        else: return ret

    def fetch_len (self, table, **criteria):
        """Return the number of rows in table that match criteria
        """
        return len(self.fetch_all(table,**criteria))

    def search (self, table, colname, text, exact=0, use_regexp=True):
        """Search colname of table for text, optionally using regular
        expressions and/or requiring an exact match."""
        raise NotImplementedError

    def fetch_food_groups_for_search (self, words):
        raise NotImplementedError

    def search_nutrition (self, words, group=None):
        """Search nutritional information for ingredient keys."""
        raise NotImplementedError

    def search_recipes (self, searches, sort_by=[]):
        """Search recipes for columns of values.

        "category" and "ingredient" are handled magically

        sort_by is a list of tuples (column,1) [ASCENDING] or (column,-1) [DESCENDING]
        """
        pass

    def filter (self, table, func):
        """Return a table representing filtered with func.

        func is called with each row of the table.
        """
        raise NotImplementedError

    def get_unique_values (self, colname,table=None,**criteria):
        """Get list of unique values for column in table."""
        if not table: table=self.rview
        if criteria: table = table.select(**criteria)
        if colname=='category' and table==self.rview:
            table=self.catview
        lst = []
        def add_to_dic (row):
            a=getattr(row,colname)
            if not a in lst: lst.append(a)
        table.filter(add_to_dic)
        if defaults.fields.has_key(colname):
            for v in defaults.fields[colname]:
                if not v in lst: lst.append(v)
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

    def update_by_criteria (self, table, update_criteria, new_values_dic):
        raise NotImplementedError

    # Metakit has no AUTOINCREMENT, so it has to do special magic here
    def increment_field (self, table, field):
        """Increment field in table, or return None if the DB will do
        this automatically.
        """
        return None


    def row_equal (self, r1, r2):
        """Test whether two row references are the same.

        Return True if r1 and r2 reference the same row in the database.
        """
        return r1==r2
    
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
            newcats = dic['category'].split(', ')
            curcats = self.get_cats(rec)
            for c in curcats:
                if c not in newcats:
                    self.delete_by_criteria(self.catview,{'id':rec.id,'category':c})
            for c in newcats:
                if c not in curcats:
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

    def modify_ing_and_update_keydic (self, ing, ingdict):
        """Update our key dictionary and modify our dictionary.

        This is a separate method from modify_ing because we only do
        this for hand-entered data, not for mass imports.
        """
        # If our ingredient has changed, update our keydic...
        if ing.item!=ingdict.get('item',ing.item) or ing.ingkey!=ingdict.get('ingkey',ing.ingkey):
            if ing.item and ing.ingkey:
                self.remove_ing_from_keydic(ing.item,ing.ingkey)
                self.add_ing_to_keydic(
                    ingdict.get('item',ing.item),
                    ingdict.get('ingkey',ing.ingkey)
                    )
        return self.modify_ing(ing,ingdict)
        

    def modify_ing (self, ing, ingdict):
        self.validate_ingdic(ingdict)
        return self.do_modify_ing(ing,ingdict)

    # Lower level DB access functions -- hopefully subclasses can
    # stick to implementing these    

    def add_rec (self, dic):
        cats = []
        if dic.has_key('category'):
            cats = dic['category'].split(', ')
            del dic['category']
        if dic.has_key('servings'):
            dic['servings'] = float(dic['servings'])
        if not dic.has_key('deleted'): dic['deleted']=False
        self.validate_recdic(dic)
        try:
            ret = self.do_add_rec(dic)
        except:
            print 'Problem adding ',dic
            raise
        else:
            if type(ret)==int:
                ID = ret
            else:
                ID = ret.id
            for c in cats:
                if c: self.do_add_cat({'id':ID,'category':c})
            return ret

    def add_ing_and_update_keydic (self, dic):
        if dic.has_key('item') and dic.has_key('ingkey') and dic['item'] and dic['ingkey']:
            self.add_ing_to_keydic(dic['item'],dic['ingkey'])
        return self.add_ing(dic)
    
    def add_ing (self, dic):
        self.validate_ingdic(dic)
        try:          
            return self.do_add_ing(dic)
        except:
            print 'Problem adding',dic
            raise

    def do_add (self, table, dic):
        table.append(dic)

    def do_add_ing (self,dic):
        self.do_add(self.iview,dic)
        return self.iview[-1]

    def do_add_cat (self, dic):
        self.do_add(self.catview,dic)
        return self.catview[-1]

    def validate_ingdic (self,dic):
        """Do any necessary validation and modification of ingredient dictionaries."""
        if not dic.has_key('deleted'): dic['deleted']=False

    def do_modify_rec (self, rec, dic):
        """This is what other DBs should subclass."""
        raise NotImplementedError

    def do_modify_ing (self, ing, ingdict):
        """modify ing based on dictionary of properties and new values."""
        for k,v in ingdict.items():
            if hasattr(ing,k):
                self.changed=True
                setattr(ing,k,v)
            else:
                debug("Warning: ing has no attribute %s (attempted to set value to %s" %(k,v),0)
        return ing

    def do_modify (self, table, row, d):
        for k,v in d.items():
            setattr(row,k,v)

    def get_ings (self, rec):
        """Handed rec, return a list of ingredients.

        rec should be an ID or an object with an attribute ID)"""
        if hasattr(rec,'id'):
            id=rec.id
        else:
            id=rec
        return self.fetch_all(self.iview,id=id,deleted=False)

    def get_cats (self, rec):
        svw = self.fetch_all(self.catview,id=rec.id)
        cats =  [c.category or '' for c in svw]
        # hackery...
        while '' in cats:
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
            rec = self.fetch_one(self.rview,**{'title':ing.item})
            if rec:
                self.modify_ing(ing,{'refid':rec.id})
                return rec
            else:
                print 'Very odd: no match for',ing,'refid:',ing.refid

    def get_rec (self, id, rview=None):
        """Handed an ID, return a recipe object."""
        if rview:
            print 'handing get_rec an rview is deprecated'
            print 'Ignoring rview handed to get_rec'
        rview=self.rview
        return self.fetch_one(self.rview, id=id)

    def do_add (self, table, d):
        """Generic method to add items."""
        raise NotImplementedError

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
        rid = self.increment_field('recipe','id')
        return rid 
    # Convenience functions for dealing with ingredients

    def order_ings (self, ings):
        """Handed a view of ingredients, we return an alist:
        [['group'|None ['ingredient1', 'ingredient2', ...]], ... ]
        """
        defaultn = 0
        groups = {}
        group_order = {}
        n = 0; group = 0
        for i in ings:
            # defaults
            if not hasattr(i,'inggroup'):
                group = None
            else:
                group=i.inggroup
            if group == None:
                group = n; n+=1
            if not hasattr(i,'position'):
                print 'Bad: ingredient without position',i
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
        final_alist = []
        last_g = -1
        for g,ii in alist:
            if type(g)==int:
                if last_g == None:
                    final_alist[-1][1].extend(ii)
                else:
                    final_alist.append([None,ii])
                last_g = None
            else:
                final_alist.append([g,ii])
                last_g = g
        return final_alist

    def replace_ings (self, ingdicts):
        """Add a new ingredients and remove old ingredient list."""
        ## we assume (hope!) all ingdicts are for the same ID
        id=ingdicts[0]['id']
        debug("Deleting ingredients for recipe with ID %s"%id,1)
        self.delete_by_criteria(self.iview,{'id':id})
        for ingd in ingdicts:
            self.add_ing(ingd)
    
    def ingview_to_lst (self, view):
        """Handed a view of ingredient data, we output a useful list.
        The data we hand out consists of a list of tuples. Each tuple contains
        amt, unit, key, alternative?"""
        ret = []
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
        #print 'add ',item,key,'to keydic'
        if not item or not key: return
        row = self.fetch_one(self.ikview, item=item, ingkey=key)
        if row:
            self.do_modify(self.ikview,row,{'count':row.count+1})
        else:
            self.do_add(self.ikview,{'item':item,'ingkey':key,'count':1})
        for w in item.rsplit():
            w=str(w.decode('utf8').lower())
            row = self.fetch_one(self.ikview,word=w,ingkey=key)
            if row:
                self.do_modify(self.ikview,row,{'count':row.count+1})
            else:
                self.do_add(self.ikview,{'word':w,'ingkey':key,'count':1})

    def remove_ing_from_keydic (self, item, key):
        #print 'remove ',item,key,'to keydic'        
        row = self.fetch_one(self.ikview,item=item,ingkey=key)
        if row:
            new_count = row.count - 1
            if new_count:
                self.do_modify(self.ikview,row,{'count':new_count})
            else:
                self.delete_by_criteria(self.ikview,{'item':item,'ingkey':key})
        for w in item.rsplit():
            w=str(w.decode('utf8').lower())
            row = self.fetch_one(self.ikview,item=item,ingkey=key)
            if row:
                new_count = row.count - 1
                if new_count:
                    self.do_modify(self.ikview,row,{'count':new_count})
                else:
                    self.delete_by_criteria(self.ikview,{'word':w,'ingkey':key})

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
        key = dic.get('ingkey',None)
        item = key and dic.get('item',ing.item)
        def do_action ():
            debug('undoable_modify_ing modifying %s'%dic,2)
            self.modify_ing(ing,dic)
            if key:
                self.add_ing_to_keydic(item,key)
            if make_visible: make_visible(ing,dic)
        def undo_action ():
            debug('undoable_modify_ing unmodifying %s'%orig_dic,2)
            self.modify_ing(ing,orig_dic)
            if key:
                self.remove_ing_from_keydic(item,key)
            if make_visible: make_visible(ing,orig_dic)
        obj = Undo.UndoableObject(do_action,undo_action,history)
        obj.perform()
        
    def undoable_delete_ings (self, ings, history, make_visible=None):
        """Delete ingredients in list ings and add to our undo history."""
        def do_delete():
            modded_ings = [self.modify_ing(i,{'deleted':True}) for i in ings]
            if make_visible:
                make_visible(modded_ings)
        def undo_delete ():
            modded_ings = [self.modify_ing(i,{'deleted':False}) for i in ings]
            if make_visible: make_visible(modded_ings)
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
            a,u,i=(m.group(convert.ING_MATCHER_AMT_GROUP),
                   m.group(convert.ING_MATCHER_UNIT_GROUP),
                   m.group(convert.ING_MATCHER_ITEM_GROUP))
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
                    prev_uses = self.fetch_all(self.iview,unit=u.strip())
                    if prev_uses:
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
            if vw2 and vw:
                vw = vw.union(vw2)
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
        row = self.db.fetch_one(self.vw,**{self.kp:k})
        if row:
            self.db.do_modify(self.vw, row, {self.vp:store_v})
        else:
            self.db.do_add(self.vw,{self.kp:k,self.vp:store_v})
        self.db.changed=True
        return v

    def __getitem__ (self, k):
        if self.just_got.has_key(k): return self.just_got[k]
        if self.pickle_key:
            k=pickle.dumps(k)
        v = getattr(self.db.fetch_one(self.vw,**{self.kp:k}),self.vp)
        if v and self.pickle_val:
            try:
                return pickle.loads(v)
            except:
                print "Problem unpickling ",v
                raise
        else:
            return v
    
    def __repr__ (self):
        retstr = "<dbDic> {"
        #for i in self.vw:
        #    if self.pickle_key:
        #        retstr += "%s"%pickle.loads(getattr(i,self.kp))
        #    else:
        #        retstr += getattr(i,self.kp)
        #    retstr += ":"
        #    if self.pickle_val:
        #        retstr += "%s"%pickle.loads(getattr(i,self.vp))
        #    else:
        #        retstr += "%s"%getattr(i,self.vp)
        #    retstr += ", "
        retstr += "}"
        return retstr

    def keys (self):
        ret = []
        for i in self.db.fetch_all(self.vw):
            ret.append(getattr(i,self.kp))
        return ret

    def values (self):
        ret = []
        for i in self.db.fetch_all(self.vw):
            val = getattr(i,self.vp)
            if val and self.pickle_val: val = pickle.loads(val)
            ret.append(val)
        return ret

    def items (self):
        ret = []
        for i in self.db.fetch_all(self.vw):
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
                    
def test_rec_basics (db):
    rec = db.add_rec({'title':'Fooboo'})
    assert(rec.title=='Fooboo')
    rec2 = db.new_rec()
    rec2 = db.modify_rec(rec,{'title':'Foo','cuisine':'Bar'})
    assert(rec2.title=='Foo')
    assert(rec2.cuisine=='Bar')
    db.delete_rec(rec)
    db.delete_rec(rec2)    

def test_ing_basics (db):
    rid = db.new_rec().id
    ing = db.add_ing({'amount':1,
                      'unit':'c.',
                      'item':'Carrot juice',
                      'ingkey':'juice, carrot',
                      'id':rid
                      })
    ing2 = db.add_ing({'amount':2,
                       'unit':'c.',
                      'item':'Tomato juice',
                      'ingkey':'juice, tomato',
                      'id':rid
                       })
    assert(len(db.get_ings(rid))==2)
    ing = db.modify_ing(ing,{'amount':2})
    assert(ing.amount==2)
    ing = db.modify_ing(ing,{'unit':'cup'})    
    assert(ing.unit=='cup')
    db.delete_ing(ing)
    db.delete_ing(ing2)

def test_unique (db):
    for i in ['juice, tomato',
              'broccoli',
              'spinach',
              'spinach',
              'spinach',]:
        db.add_ing({'amount':1,'unit':'c.','item':i,'ingkey':i})
    vv=db.get_unique_values('ingkey',db.iview)
    assert(len(vv)==3)
    cvw = db.fetch_count(db.iview,'ingkey',ingkey='spinach',sort_by=[('count',-1)])
    assert(cvw[0].count==3)    
    assert(cvw[0].ingkey=='spinach')

def test_search (db):
    db.add_rec({'title':'Foo','cuisine':'Bar','source':'Z'})
    db.add_rec({'title':'Fooey','cuisine':'Bar','source':'Y'})
    db.add_rec({'title':'Fooey','cuisine':'Foo','source':'X'})
    db.add_rec({'title':'Foo','cuisine':'Foo','source':'A'})
    db.add_rec({'title':'Boe','cuisine':'Fa'})
    result = db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                {'column':'cuisine','search':'Foo','operator':'='}])
    assert(len(result)==2)
    result = db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                {'column':'cuisine','search':'F.*','operator':'REGEXP'}])

    assert(len(result)==3)
    result = db.search_recipes([{'column':'deleted','search':False,'operator':'='},
                                {'column':'cuisine','search':'Foo'},
                                {'column':'title','search':'Foo','operator':'='},])
    assert(len(result)==1)
    result = db.search_recipes([{'column':'title','search':'Fo.*','operator':'REGEXP'}],
                               [('source',1)])
    assert(result[0].title=='Foo' and result[0].source=='A')
    # Advanced searching
    db.add_rec({'title':'Spaghetti','category':'Entree'})
    db.add_rec({'title':'Quiche','category':'Entree, Low-Fat, High-Carb'})
    assert(len(db.search_recipes([
        {'column':'deleted','search':False,'operator':'='},
        {'column':'category','search':'Entree','operator':'='}]))==2)
    # Test fancy multi-category searches...
    assert(len(db.search_recipes([{'column':'category','search':'Entree','operator':'='},
                                  {'column':'category','search':'Low-Fat','operator':'='}])
               )==1)
    # Test ingredient search
    recs = db.fetch_all(db.rview)
    r = recs[0]
    db.add_ing({'id':r.id,'ingkey':'apple'})
    db.add_ing({'id':r.id,'ingkey':'cinnamon'})
    db.add_ing({'id':r.id,'ingkey':'sugar, brown'})
    r2 = recs[1]
    db.add_ing({'id':r2.id,'ingkey':'sugar, brown'})
    db.add_ing({'id':r2.id,'ingkey':'flour, all-purpose'})
    db.add_ing({'id':r2.id,'ingkey':'sugar, white'})
    db.add_ing({'id':r2.id,'ingkey':'vanilla extract'})
    r3 = recs[2]
    db.add_ing({'id':r3.id,'ingkey':'sugar, brown'})
    db.add_ing({'id':r3.id,'ingkey':'sugar, brown','unit':3,'unit':'c.'} )
    assert(len(db.search_recipes([{'column':'ingredient',
                                   'search':'sugar%',
                                   'operator':'LIKE',
                                  }])
               )==3)
    assert(len(db.search_recipes([{'column':'ingredient',
                                  'search':'sugar, brown'},
                                 {'column':'ingredient',
                                  'search':'apple'}])
               )==1)
    
def test_unicode (db):
    rec = db.add_rec({'title':u'Comida de \xc1guila',
                'source':u'C\xc6SAR',})
    assert(rec.title == u'Comida de \xc1guila')
    assert(rec.source == u'C\xc6SAR')

def test_id_reservation (db):
    rid = db.new_id()
    rid2 = db.new_id()
    r1 = db.add_rec({'title':'intermittent'})
    r1i = db.add_rec({'title':'intermittent2'})
    r12 = db.add_rec({'title':'intermittent3'})    
    r2 = db.add_rec({'title':'reserved','id':rid})
    r3 = db.add_rec({'title':'reserved2','id':rid2})
    try: assert(r2.id==rid)
    except:
        print 'reserved ID',rid
        print 'fetched ID',r2.id
        print 'intermittent ID',r1.id
        raise
    for r in [r1,r1i,r12,r2,r3]: db.delete_rec(r)

img='\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00(\x00#\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xf5\x01#r\xc0\x1c\x01\x92q\xd0S\x9a\xea+x\x1a{\xa9\x92(\x82\x16R\xc7n\xefl\x9e+\x07\xc6z\xf0\xd3$\x16p\xa4A\xf2\xb2d\xb1S\x8eq\xfc\'=\xff\x00:\xcf\x9a\xf7Q\xf1O\x85\x9eDB\xa9\x14\xdbJ\xc7\xceO\xe4\x0f\x7f\xd6\xaeUU\xb4*4\x9bj\xfb\x1d5\x9e\xadk}m\xba\x19\xe3\x92U8a\x1b\x02\x05`k\xfe\'m1\x84\x0bl\x1d\x87F.F>\xb8\xebShKi\xa0\xe9-4\xf8I\xe7E\r\xba,\x98\xd8\x03\x81\x8c\xe4\xf5\xcf^A\x14\x96\x97:>\xb5rl\xae\x00\xbd\x91\x8b"\xbbB\xcaz\xfd\xe1\xe9\xeb\xc1\x1c}1I\xc9\xc9+n5\x15\x17\xaa\xba,\xe9\xda\xb5\xd6\xa3a\r\xdb\xa2\xabH2F\x07c\x8f\xe9Etp\xd9\xc1o\x04p\xc5\x10\x11\xc6\xa1T{\n+U-52v\xbe\x86\x0f\x8c\xbc2\xfa\xcc\x90\xdc@3 \xc4dd\x0f\xa7\xf3\xadm\x13H\x87C\xd2\xa2\xb2\x1f31\xdc\xe4\x0e\x0b\x1cg\xf9\x01Z\x8e\xe7#\x18\x1e\xe6\xa2\xbb\xbb\x8a\xd9Y\x9d\x86\xc03\x9a\xc9E\'r\xdc\xdb\x8f)\xc6\xfcF\xd3e\xb9\xb3\x82\xea0\xc7h*v\xfey\xff\x00>\x95\x93\xf0\xfbIxo\x1e\xfex\xdbj\x02\xa8I\xfe#\xd7\xf4\xcf\xe7]\xcc\x97\xd1\xdd\xda\xc8\x8a\x98S\xf2\xe5\xfe\\\xfd;\xf1\x8c\xfe\x1d\xba\xd3\x86AX\xc4,\x15F7\xed\x00\x13\xdf\x8c\xf1\xcei{?{\x98~\xd3\xdc\xe5,1%\x89\x07\x03\xd0QF(\xadL\xc9\xd9\xc6*\xa5\xec"x\n\xed\xdcr\x1b\x1e\xb84QR\x80\xa0\xc8\xb3C\xf6i"|0\xc6\x0eG\x1f^\xb9\xabS\\}\x968`p\xca\xa3\x01X\xe4\x8f\xc4\xff\x00\x8d\x14U\x89\n\xf7r+m\x8ebT\x01\x8c-\x14QH\x0f\xff\xd9'

def test_data (db):
    r = db.add_rec({'image':img})
    assert(r.img == img)

def test_update (db):
    r = db.add_rec({'title':'Foo','cuisine':'Bar','source':'Z'})
    db.update(db.rview,{'title':'Foo'},{'title':'Boo'})
    assert(db.get_rec(r.id).title == 'Boo')
    
def test_db (db):
    tests = [test_rec_basics,
             test_ing_basics,
             test_unique,
             test_search,
             test_unicode,
             test_id_reservation,
             test_update,
             ]
    success = 0
    for t in tests:
        print t.__name__
        try:
            t(db)
            print 'Passed'
            success += 1
        except:
            print 'Failed'
            import traceback; traceback.print_exc()
    print 'Completed ',len(tests),'tests'
    print 'Passed',"%s/%s"%(success,len(tests)),'tests'
    
# Not working -- I don't understand why -- for now I use the above
# simple test function
class DatabaseUnitTest (unittest.TestCase):
    """Unit test for any subclass to pass."""
    # subclass must provide these arguments for us to work!
    db_class = None
    db_args = []
    db_kwargs = {}

    def setUp (self):
        print 'Set up!',self.db_class,'(*',self.db_args,',**',self.db_kwargs,')'
        self.rd = self.db_class(*self.db_args,**self.db_kwargs)
        self.rd.initialize_connection()
        print 'Set up done.'

    def testRecs (self):
        rec = self.rd.new_rec()
        rec = self.rd.modify_rec(rec,
                                 {'title':'Foo',
                                  'cuisine':'Bar',})
        assert(rec.title=='Foo')
        assert(rec.cuisine=='Bar')
        self.rd.delete_rec(rec)

    def testIngs (self):
        rid = self.rd.new_rec().id
        ing = self.rd.add_ing({'amount':1,
                               'unit':'c.',
                               'item':'Carrot juice',
                               'ingkey':'juice, carrot',
                               'id':rid,
                               })
        ing = self.rd.modify_ing(ing,{'amount':2})
        assert(ing.amount==2)
        ing = self.rd.modify_ing(ing,{'unit':'cup'})
        for i in self.rd.get_ings(rid):
            self.rd.modify_ing(i,{'optional':True})
        assert(ing.unit=='cup')
        self.rd.delete_ing(ing)
        
