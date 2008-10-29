import metakit, re, pickle, keymanager, string, shopping, convert, os.path
from defaults import lang as defaults
from gdebug import *
from gettext import gettext as _
import gglobals
global default_values
default_values = defaults.fields

class recData:
    """A class to keep recipe data in. This class basically is a wrapper for interactions
    with metakit (stored in self.db). Ideally, interactions with metakit should be abstracted
    through this class so that I could easily change to a different database backend."""
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        debug('recData.__init__()',3)
        self.changed=False
        self.file=os.path.expandvars(os.path.expanduser(file))
        dir = os.path.split(self.file)[0]
        # create the directory if it does not yet exist
        if not os.path.exists(dir):
            os.mkdir(dir)
        self.db = metakit.storage(self.file,1)
        self.load()
        #self.db.autocommit()        
        self.rview = self.db.getas("recipe[id:s,title:s,instructions:s,modifications:s,cuisine:s,rating:s,description:s,category:s,source:s,preptime:s,servings:s,image:B,thumb:B]")
        rhsh = self.db.getas("__recipe_hash__[_H:I,_R:I]")
        self.rview = self.rview.hash(rhsh,1)
        debug('there are %s recipes in the database'%len(self.rview),0)
        self.iview = self.db.getas("ingredients[id:s,refid:s,unit:s,amount:F,item:s,key:s,optional:s,group:s,position:I]")
        chsh = self.db.getas("__conversions_hash__[_H:I,_R:I]")
        # position is a string because it is used with my mkDic class which
        # pickles everything.
        self.sview = self.db.getas("shopcats[key:s,category:s,position:s]")
        self.scview = self.db.getas("shopcatsorder[category:s,position:s]")
        self.pview = self.db.getas("pantry[itm:s,pantry:s]")
        self.metaview = self.db.getas("categories[id:s,type:s,description:s]")
        # converter items
        self.cdview = self.db.getas("density[key:s,value:s]")
        self.cview = self.db.getas("convtable[key:s,value:s]")
        self.cuview = self.db.getas("crossunitdict[key:s,value:s]")
        self.uview = self.db.getas("unitdict[key:s,value:s]")
        self.converter = None
        # new system for multiple ID namespaces
        # dict contains prefix and top number currently
        # in the system
        self.top_id = {'r': 1}
        # hooks run after adding, modifying or deleting a recipe.
        # Each hook is handed the recipe, except for delete_hooks,
        # which is handed the ID (since the recipe has been deleted)
        self.add_hooks = []
        self.modify_hooks = []
        self.delete_hooks = []
        self.add_ing_hooks = []

    def run_hooks (self, hooks, *args):
        for h in hooks:
            debug('running hook %s with args %s'%(h,args),3)
            h(*args)
    
    def save (self):
        debug('saving database to file %s'%self.file,0)
        debug('there are %s recipes in the database'%len(self.rview),0)
        self.db.commit()
        self.changed=False

    def load (self, file=None):
        if file:
            self.file = file
        debug('loading database from file %s'%self.file,0)        
        fo  = open(self.file,'r')
        self.db.load(fo)
        fo.close()

    def get_default_values (self, colname):
        try:
            return default_values[colname]
        except:
            return []

    def get_unique_values (self, colname, dict=None):
        dct = {}
        if default_values.has_key(colname):
            for v in default_values[colname]:
                dct[v]=1
        if not dict:
            dict=self.rview
        def add_to_dic (row):
            a=getattr(row,colname)
            if type(a)==type(""):
                for i in a.split(","):
                    dct[i.strip()]=1
            else:
                dct[a]=1
        self.rview.filter(add_to_dic)
        return dct.keys()

    def modify_rec (self, rec, dic):
        for k,v in dic.items():
            if hasattr(rec,k):
                self.changed=True
                setattr(rec,k,"%s"%v) #everything's a string.
            else:
                debug("Warning: rec has no attribute %s (tried to set to %s)" %(k,v),1)
        self.run_hooks(self.modify_hooks,rec)

    def ings_search (self, ings, keyed=None, rview=None,*args):
        """Handed a list of regexps, return a list of recipes containing all
        items."""
        for i in ings:
            rview = self.ing_search(i,keyed=keyed,rview=rview)
        return rview

    def ing_search (self, ing, keyed=None, rview=None,*args):
        """Handed an ingredient (or, rather, a regexp for an
        ingredient), return a list of recipes. By default
        (keyed=None), we search through keys or item descriptions. If
        'keyed', we search only in keys."""
        iview = self.iview
        if not rview:
            rview=self.rview
        vw = self.search(iview, 'key', ing)
        if not keyed:
            vw2 = self.search(iview, 'item', ing)
            vw = vw.union(vw2)
        ## this is hackish--using a dictionary to get a list of unique IDs
        ## I should figure out how to do this right so I get a view returned
        ## which can be searched again.
        ## return self.rview.remapwith(vw)
        ## segfaults for unknown reason
        rlist = {}
        for v in vw:
            rlist[v.id]=1
        recs = []
#        for rid in rlist.keys():
#            recs.append(self.get_rec(rid))
        ## now, being backasswards as we are, we use a filter to get ourselves a proper view
        return self.ids_to_rview(rlist.keys(),rview=rview)

    def ids_to_rview (self, ids, rview=None):
        """A backasswards function that shouldn't be necessary: we
        take a list of IDs and return a view containing those recipes."""
        if not rview:
            rview=self.rview
        indexvw = rview.filter(lambda row: ids.__contains__(row.id))
        resultvw = rview.remapwith(indexvw)
        resultvw.unique()
        return resultvw

    def search (self, table, colname, regexp, exact=0):
        """Handed a table, a column name, and a regular expression, search
        for an item"""
        if exact:
            indexvw = table.filter(lambda r: re.match(regexp, getattr(r,colname)))
        else:
            indexvw = table.filter(lambda r: re.search(regexp,getattr(r,colname),re.I))
        resultvw = table.remapwith(indexvw)
        resultvw = resultvw.unique()
        return resultvw

    def get_ings (self, rec):
        """rec can be almost anything and we'll return a view of the
        ingredients in that thing.  We accept: a single string
        containing a rec id, a row reference to a recipe, a list of
        strings or row references OR a view."""
        if type(rec) == type([]) or type(rec)==type(self.rview) or type(rec) == type(self.rview[0:-1]):
            vw = self.get_ings(rec[0])
            for r in rec[1:]:
                vw2 = self.get_ings(r)
                vw = vw.union(vw2)
            return vw
        else:
            if hasattr(rec,"id"):
                rec = rec.id
#            retview = self.search(self.iview, 'id', rec, 1)
#            retview = retview.unique()
            retview = self.iview.select(id=rec)
            return retview

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
                group=i.group
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
            ret.append([i.amount, i.unit, i.key,])
        return ret

    def ing_shopper (self, view):
        s = mkShopper(self.ingview_to_lst(view))
        return s

    def get_rec (self, id, rview=None):
        if not rview:
            rview=self.rview
        s = rview.select(id=id)
        if len(s)>0:
            return rview.select(id=id)[0]
        else:
            return None

    def remove_unicode (self, mydict):
        for k,v in mydict.items():
            if v.__class__ == u'hello'.__class__:
                mydict[k]=v.encode('utf8','replace')
            if k.__class__ == u'hello'.__class__:
                v = mydict[k]
                mydict.__delitem__(k)
                mydict[k.encode('utf8','replace')] = v



    def add_meta (self, metadict):
        self.changed=True
        self.remove_unicode(metadict)
        self.metaview.append(metadict)
        
    def add_rec (self, rdict):
        self.changed=True
        self.remove_unicode(rdict)
        if not rdict.has_key('id'):
            rdict['id']=self.new_id()
        old_r=self.get_rec(rdict['id'])
#        ## if we already have a recipe with this ID, delete it, change the ID
        if old_r:
            #debug("WARNING: DELETING OLD RECIPE %s id %s"%(old_r.title,old_r.id),0)
            #self.delete_rec(old_r)
            debug("ID %s taken. Generating new ID."%rdict['id'])
            rdict['id']=self.new_id()
        try:
            debug('Adding recipe %s'%rdict, 4)
            self.rview.append(rdict)
            debug('Running add hooks %s'%self.add_hooks,2)
            self.run_hooks(self.add_hooks,self.rview[-1])
            return self.rview[-1]
        except:
            debug("There was a problem adding recipe%s"%rdict,-1)
            raise

    def delete_rec (self, rec):
        self.changed=True
        debug("delete_rec called",5)
        if type(rec)==type(""):
            debug("grabbing rec from id",5)
            rec=self.get_rec(rec)
        # we run hooks before deletion in case
        # they need to act on the recipe object
        # (as most imaginable hook would).
        debug("running delete_hooks",5)
        self.run_hooks(self.delete_hooks,rec)
        did = rec.id
        debug("deleting recipe %s %s"%(rec.id,rec.title),2)
        self.rview.delete(rec.__index__)
        debug("successfully deleted recipe!",2)
        ## and now we delete the ingredients
        debug('selecting ingredients')
        for i in self.iview.select(id=did):
            debug("DEBUG: Deleting ingredient %s"%i.item)
            self.iview.delete(i.__index__)
        debug('delete_rec finished.')

    def new_id (self, base="r"):
        """Return a new unique ID. Possibly, we can have
        a base"""
        if self.top_id.has_key(base):
            start = self.top_id[base]
        else:
            start = 0
        # every time we're called, we increment out record.
        # This way, if party A asks for an ID and still hasn't
        # committed a recipe by the time party B asks for an ID,
        # they'll still get unique IDs.
        n = start + 1
        while self.rview.find(id=self.format_id(n, base)) > -1 or self.iview.find(id=self.format_id(n, base)) > -1:
            # if the ID exists, we keep incrementing
            # until we find a unique ID
            n += 1
        self.top_id[base]=n
        return self.format_id(n, base)

    def format_id (self, n, base="r"):
        return base+str(n)

    def new_rec (self):
        blankdict = {'id':self.new_id(),
                     'title':_('New Recipe'),
                     'servings':'4'}
        return self.add_rec(blankdict)
    
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
        self.remove_unicode(ingdict)
        debug('adding to iview',3)
        self.iview.append(ingdict)
        debug('running ing hooks %s'%self.add_ing_hooks,3)
        self.run_hooks(self.add_ing_hooks, self.iview[-1])
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
        self.iview.delete(ing.__index__)
        self.changed=True        

    def save_dic (self, name, dict):
        """Save a dictionary in a metakit table. Names must be unique.
        The metakit table will be cleared before new data is saved."""
        vw = self.db.getas("%s[k:s,v:s]")
        ## clear the table in case there's anything in it!
        for r in vw:
            vw.delete(r.__index__)
        for k,v in dict.items():
            vw.append(k=pickle.dumps(k),v=pickle.dumps(v))
        self.changed=True
            
    def load_dic (self, name):
        vw = self.db.getas("%s[k:s,v:s]")
        d = {}
        for r in vw:
            d[pickle.loads(r.k)]=pickle.loads(r.v)
        return d

    def delete_table (self, table):
        while len(table)>0:
            table.delete(0)

class recipeManager (recData):
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        debug('recipeManager.__init__()',3)
        recData.__init__(self, file)
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
                d['key']=self.km.get_key(i.strip())
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

class mkShopper (shopping.shopper):
    """We are a shopper class that conveniently saves our key dictionaries
    in our metakit database"""
    def __init__ (self, lst, rm, conv=None):
        self.rm = rm
        self.cnv = conv
        shopping.shopper.__init__(self,lst)


    def init_converter (self):
        #self.cnv = mkConverter(self.rm)
        if not self.cnv:
            self.cnv = convert.converter()
    
    def init_orgdic (self):
        self.orgdic = mkDic('key','category',self.rm.sview,rm=self.rm)
        if len(self.orgdic.items())==0:
            dic = shopping.setup_default_orgdic()
            for k,v in dic.items():
                self.orgdic[k]=v

    def init_ingorder_dic (self):
        self.ingorder_dic = mkDic('key','position',self.rm.sview,rm=self.rm)

    def init_catorder_dic (self):
        self.catorder_dic = mkDic('category','position',self.rm.scview,rm=self.rm)

    def init_pantry (self):
        self.pantry = mkDic('itm','pantry',self.rm.pview,rm=self.rm)
        if len(self.pantry.items())==0:
            for i in self.default_pantry:
                self.pantry[i]=True

class mkConverter(convert.converter):
    def __init__ (self, rm):
        self.rm = rm
        convert.converter.__init__(self)
    ## still need to finish this class and then
    ## replace calls to convert.converter with
    ## calls to rmetakit.mkConverter

    def create_conv_table (self):
        self.conv_table = mkDic('key','value',self.rm.cview, self.rm,
                                pickle_key=True)
        for k,v in defaults.CONVERTER_TABLE.items():
            if not self.conv_table.has_key(k):
                self.conv_table[k]=v

    def create_density_table (self):
        self.density_table = mkDic('key','value',
                                   self.rm.cdview,self.rm)
        for k,v in defaults.DENSITY_TABLE.items():
            if not self.density_table.has_key(k):
                self.density_table[k]=v

    def create_cross_unit_table (self):
        self.cross_unit_table=mkDic('key','value',self.rm.cuview,self.rm)
        for k,v in defaults.CROSS_UNIT_TABLE:
            if not self.cross_unit_table.has_key(k):
                self.cross_unit_table[k]=v

    def create_unit_dict (self):
        self.units = defaults.UNITS
        self.unit_dict=mkDic('key','value',self.rm.uview,self.rm)
        for itm in self.units:
            key = itm[0]
            variations = itm[1]
            self.unit_dict[key] = key
            for v in variations:
                self.unit_dict[v] = key
                
class mkDic:
    def __init__ (self, keyprop, valprop, view, rm, pickle_key=False):
        """Create a dictionary interface to a metakit table"""
        self.pickle_key = pickle_key
        self.vw = view
        self.kp = keyprop
        self.vp = valprop
        self.rm = rm

    def has_key (self, k):
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
        self.rm.changed=True
        return v
    
    def __getitem__ (self, k):
        if self.pickle_key:
            k=pickle.dumps(k)
        return pickle.loads(getattr(self.vw.select(**{self.kp:k})[0],self.vp))

    def __repr__ (self):
        str = "<mkDic> {"
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
            ret.append(pickle.loads(getattr(i,self.vp)))
        return ret

    def items (self):
        ret = []
        for i in self.vw:
            ret.append((getattr(i,self.kp),pickle.loads(getattr(i,self.vp))))
        return ret
        
#if __name__ == '__main__':
#    rd = recData()
#    count = 0
#    print len(rd.rview), "recipes"
