import os.path
from gdebug import debug, TimeAction
import re, pickle, keymanager, string, shopping, convert, os.path
from gettext import gettext as _
import gglobals


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

    def modify_rec (self, rec, dict):
        raise NotImplementedError

    def search (self, table, colname, text, exact=0, use_regexp=True):
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


        #if self.kd.has_key(ing):
        #    #print "DEBUG: key_search returning:",self.kd[ing]
        #    return self.kd[ing]
        #else:
        #    
        #    retlist = []
        #    for i in self.kd.keys():
        #        if string.find(i,ing) > -1 or string.find(ing,i) > -1:
        #            retlist.extend(self.kd[i])
        #    #print "DEBUG: key_search returning:",retlist
        #    return retlist

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
