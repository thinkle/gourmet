import os.path
from gourmet.gdebug import debug, TimeAction
import re, pickle, string, os.path, string
from gettext import gettext as _
import gourmet.gglobals
from gourmet import Undo, keymanager, convert, shopping
from gourmet.defaults import lang as defaults


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

    def save (self):
        pass

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
                                       ('cooktime',"char(50)"),                                       
                                       ('servings',"char(50)"),
                                       ('image',"binary"),
                                       ('thumb','binary'),
                                       ('deleted','bool')                                       
                                       ])
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
                                       ('position','int'),
                                       ('deleted','bool'),
                                       ],
                                      #key='id'
                                      )
        self.iview_not_deleted = self.iview.select(deleted=False)
        self.iview_deleted = self.iview.select(deleted=True)
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

    def get_dict_for_obj (self, obj, keys):
        orig_dic = {}
        for k in keys:
            v=getattr(obj,k)
            orig_dic[k]=v
        return orig_dic

    def undoable_modify_rec (self, rec, dic, history=[], get_current_rec_method=None,
                             select_change_method=None):
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
            print 'modify_recs: ',args,kwargs
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
        if hasattr(rec,'id'):
            id=rec.id
        else:
            id=rec
        return self.iview.select(id=id,deleted=False)

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
        #debug('alist: %s'%alist,5)
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

    def add_rec (self, rdict):
        self.changed=True
        t = TimeAction('rdatabase.add_rec - checking keys',3)
        if not rdict.has_key('deleted'):
            rdict['deleted']=0
        if not rdict.has_key('id'):
            rdict['id']=self.new_id()
        t.end()
        try:
            debug('Adding recipe %s'%rdict, 4)
            t = TimeAction('rdatabase.add_rec - rview.append(rdict)',3)
            self.rview.append(rdict)
            t.end()
            debug('Running add hooks %s'%self.add_hooks,2)
            if self.add_hooks: self.run_hooks(self.add_hooks,self.rview[-1])
            return self.rview[-1]
        except:
            debug("There was a problem adding recipe%s"%rdict,-1)
            raise

    def delete_rec (self, rec):
        raise NotImplementedError

    def undoable_delete_recs (self, recs, history, make_visible=None):
        def do_delete ():
            for rec in recs: rec.deleted = True
            if make_visible: make_visible(recs)
        def undo_delete ():
            for rec in recs: rec.deleted = False
            if make_visible: make_visible(recs)
        obj = Undo.UndoableObject(do_delete,undo_delete,history)
        obj.perform()

    def new_rec (self):
        raise NotImplementedError

    def new_id (self, base="r"):
        """Return a new unique ID. Possibly, we can have
        a base"""
        if self.top_id.has_key(base):
            start = self.top_id[base]
            n = start + 1
        else:
            n = 0
        while self.rview.find(id=self.format_id(n, base)) > -1 or self.iview.find(id=self.format_id(n, base)) > -1:
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
        debug('adding to iview %s'%ingdict,3)
        timer = TimeAction('rdatabase.add_ing 2',0)
        self.iview.append(ingdict)
        timer.end()
        debug('running ing hooks %s'%self.add_ing_hooks,3)
        timer = TimeAction('rdatabase.add_ing 3',0)
        if self.add_ing_hooks: self.run_hooks(self.add_ing_hooks, self.iview[-1])
        timer.end()
        debug('done with ing hooks',3)
        return self.iview[-1]

    def undoable_modify_ing (self, ing, dic, history, make_visible=None):
        orig_dic = self.get_dict_for_obj(ing,dic.keys())
        print 'orig_dic=',orig_dic
        print 'new_dic=',dic
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
        t=TimeAction('dbdict getting from db',0)
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
                    raise 
            ret.append((key,val))
        return ret
        
#if __name__ == '__main__':
#    rd = recData()
#    count = 0
#    print len(rd.rview), "recipes"
