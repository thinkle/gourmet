import os.path
from gdebug import debug, TimeAction
import re, pickle, keymanager, string, shopping, convert, os.path
from gettext import gettext as _
import gglobals, Undo
from defaults import lang as defaults


class RecData:
    def __init__ (self):
        timer = TimeAction('initialize_connection + setup_tables',0)
        self.initialize_connection()
        debug('setting up tables',1)
        self.setup_tables()
        debug('done setting up tables',1)
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
        raise NotImplementedError

    def setup_tables (self):
        debug('rview',2)
        debug('rview',2)
        self.rview = self.setup_table('recipe',
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
                                       ('servings',"char(50)"),
                                       ('image',"binary"),
                                       ('thumb','binary')])
        debug('iview',2)
        self.iview = self.setup_table('ingredients',
                                      [('id','char(75)'),
                                       ('refid','char(75)'),
                                       ('unit','text'),
                                       ('amount','float'),
                                       ('item','text'),
                                       ('ingkey','char(200)'),
                                       ('optional','char(10)'),
                                       ('inggroup','char(200)'),
                                       ('position','int')],
                                      key='id'
                                      )
        debug('sview',2)
        self.sview = self.setup_table('shopcats',
                                      [('shopkey','char(50)'),
                                       ('category','char(200)'),
                                       ('position','int')],
                                      key='shopkey')
        debug('scview',2)
        self.scview = self.setup_table('shopcatsorder',
                                       [('category','char(50)'),
                                        ('position','int'),
                                        ],
                                       key='category')
        debug('pview',2)
        self.pview = self.setup_table('pantry',
                                      [('itm','char(200)'),
                                       ('pantry','char(10)')],
                                      key='itm')
        debug('metaview',2)
        self.metaview = self.setup_table("categories",
                                         [('id','char(200)'),
                                          ('type','char(100)'),
                                          ('description','text')], key='id')
        # converter items
        debug('cdview',2)
        self.cdview = self.setup_table("density",
                                       [('dkey','char(150)'),
                                        ('value','char(150)')],key='dkey')
        debug('cview',2)
        self.cview = self.setup_table("convtable",
                                      [('ckey','char(150)'),
                                       ('value','char(150)')],key='ckey')
        debug('cuview',2)
        self.cuview = self.setup_table("crossunitdict",
                                       [('cukey','char(150)'),
                                        ('value','char(150)')],key='cukey')
        debug('uview',2)
        self.uview = self.setup_table("unitdict",
                                      [('ukey','char(150)'),
                                       ('value','char(150)')],key='ukey')
    def setup_table (self, name, data, key):
        """Name is the name of our table. Data is a list of tuples of column names and data types."""
        raise NotImplementedError

    def run_hooks (self, hooks, *args):
        for h in hooks:
            debug('running hook %s with args %s'%(h,args),3)
            h(*args)

    def undoable_modify_rec (self, rec, dic, history=[], get_current_rec_method=None):
        orig_dic = {}
        for k in dic.keys():
            orig_dic[k]=getattr(rec,k)
        redo,reundo=None,None
        if get_current_rec_method:
            redo=lambda *args: [get_current_rec_method(),dic]
            reundo = lambda *args: [get_current_rec_method(),orig_dic]
        obj = Undo.UndoableObject(self.modify_rec,self.modify_rec,history,
                                  action_args=[rec,dic],undo_action_args=[rec,orig_dic],
                                  get_reapply_action_args=redo,
                                  get_reundo_action_args=reundo)
        obj.perform()

    def modify_rec (self, rec, dict):
        raise NotImplementedError

    def search (self, table, colname, text, exact=0, use_regexp=True):
        raise NotImplementedError

    def get_default_values (self, colname):
        try:
            return defaults.fields[colname]
        except:
            return []

    def get_unique_values (self, colname,table=None):
        if not table: table=self.rview
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
        raise NotImplementedError

    def order_ings (self, iview):
        """Handed a view of ingredients, we return an alist:
        [['group'|None ['ingredient1', 'ingredient2', ...]], ... ]
        """
        defaultn = 0
        groups = {}
        group_order = {}
        for i in iview:
            # defaults
            if not hasattr(i,'group'):
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
        debug('alist: %s'%alist,5)
        return alist

    def ingview_to_lst (self, view):
        """Handed a view of ingredient data, we output a useful list.
        The data we hand out consists of a list of tuples. Each tuple contains
        amt, unit, key, alternative?"""
        for i in view:
            ret.append([i.amount, i.unit, i.ingkey,])
        return ret
    
    def ing_shopper (self, view):
        return mkShopper(self.ingview_to_lst(view))
        
    def get_rec (self, id, rview=None):
        if not rview:
            rview=self.rview
        s = rview.select(id=id)
        if len(s)>0:
            return rview.select(id=id)[0]
        else:
            return None

    def delete_rec (self, rec):
        raise NotImplementedError

    def new_rec (self):
        raise NotImplementedError

    def add_ing (self, ingdict):
        """Add ingredient to iview based on ingdict and return
        ingredient object. Ingdict contains:
        id: recipe_id
        unit: unit
        item: description
        key: keyed descriptor
        alternative: not yet implemented (alternative)
        optional: yes|no
        position: INTEGER [position in list]
        refid: id of reference recipe. If ref is provided, everything
               else is irrelevant except for amount.
        """
        debug('add_ing ingdict=%s'%ingdict,5)
        self.changed=True
        debug('removing unicode',3)
        timer = TimeAction('rmetakit.add_ing 1',0)
        self.remove_unicode(ingdict)
        timer.end()
        debug('adding to iview %s'%ingdict,3)
        timer = TimeAction('rmetakit.add_ing 2',0)
        self.iview.append(ingdict)
        timer.end()
        debug('running ing hooks %s'%self.add_ing_hooks,3)
        timer = TimeAction('rmetakit.add_ing 3',0)
        self.run_hooks(self.add_ing_hooks, self.iview[-1])
        timer.end()
        debug('done with ing hooks',3)
        return self.iview[-1]

    def modify_ing (self, ing, ingdict):
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

    def delete_ing (self, ing):
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
            
    def ingredient_parser (self, string, conv=None):
        """Handed a string, we hand back a dictionary (sans recipe ID)"""
        m=re.match("\s*([0-9/ -]+\s+)?(\S\S*\s+)?(\S+.*\S+)$",string.strip("\n\t #*+-"))
        if m:
            d={}
            a,u,i=m.groups()
            if a:
                d['amount']=convert.frac_to_float(a.strip())
            if u:
                if conv and conv.unit_dict.has_key(u.strip()):
                    d['unit']=conv.unit_dict[u.strip()]
                else:
                    d['unit']=u.strip()
            if i:
                if re.match('[Oo]ptional',i):
                    d['optional']='yes'
                m=re.match('(^.*)\(?\s+\(?[Oo]ptional\)?\s*$',i)
                if m:
                    i=i[0:m.start()]         
                d['item']=i.strip()
                d['ingkey']=self.km.get_key(i.strip())
            return d
        else:
            debug("Unable to parse %s"%string,0)
            return None

    def ing_search (self, ing, keyed=None, rview=None, use_regexp=True, exact=False):
        raise NotImplementedError

    def ings_search (self, ings, keyed=None, rview=None, use_regexp=True, exact=False):
        raise NotImplementedError

    


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
    def __init__ (self, keyprop, valprop, view, db, pickle_key=False):
        """Create a dictionary interface to a metakit table"""
        self.pickle_key = pickle_key
        self.vw = view
        self.kp = keyprop
        self.vp = valprop
        self.db = db

    def has_key (self, k):
        try:
            self.__getitem__(k)
            return True
        except:
            return False
        
    def __setitem__ (self, k, v):
        raise NotImplementedError
    
    def __getitem__ (self, k):
        raise NotImplementedError

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
        raise NotImplementedError

    def values (self):
        raise NotImplementedError

    def items (self):
        raise NotImplementedError        
        
#if __name__ == '__main__':
#    rd = recData()
#    count = 0
#    print len(rd.rview), "recipes"
