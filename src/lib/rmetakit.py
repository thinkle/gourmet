import metakit, re, pickle, keymanager, string, shopping, convert, os.path
from defaults import lang as defaults
from gdebug import *
from gettext import gettext as _
import gglobals
import rdatabase

class RecData (rdatabase.RecData):
    """A class to keep recipe data in. This class basically is a wrapper for interactions
    with metakit (stored in self.db). Ideally, interactions with metakit should be abstracted
    through this class so that I could easily change to a different database backend."""
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        debug('RecData.__init__()',3)
        self.changed=False
        self.file = file
        self.backed_up = False
        rdatabase.RecData.__init__(self)

    def initialize_connection (self):
        debug('using file: %s'%self.file,1)
        self.file = os.path.expandvars(os.path.expanduser(self.file))
        mydir = os.path.split(self.file)[0]
        # create the directory if it does not yet exist
        if not os.path.exists(mydir):
            os.mkdir(mydir)
        self.db = metakit.storage(self.file,1)
        self.load()
        self.db.autocommit()

    def setup_tables (self):
        # first, we check for old, incompatible table names
        # and fix them
        self._move_row(table='ingredients',old=('group','text'),new=('inggroup','text'))
        self._move_row(table='ingredients',old=('key','char(200)'),new=('ingkey','char(200)'))
        self._move_row(table='shopcats',old=('key','char(50)'),new=('shopkey','char(50)'))
        self._move_row(table='density',old=('key','char(50)'),new=('dkey','char(50)'))        
        self._move_row(table='convtable',old=('key','char(50)'),new=('ckey','char(50)'))
        self._move_row(table='crossunitdict',old=('key','char(50)'),new=('cukey','char(50)'))
        self._move_row(table='unitdict',old=('key','char(50)'),new=('ukey','char(50)'))                
        rdatabase.RecData.setup_tables(self)

    def _move_row (self, table, old, new):
        """This is designed for backwards compatability (to allow
        for other database backends)."""
        tmpview = self.setup_table(table, [new,old])
        vw = tmpview.filter(lambda x: getattr(x,old[0]))
        to_move_vw = tmpview.remapwith(vw)
        to_move = len(to_move_vw)
        print '%s rows to move'%to_move
        if to_move > 0 and not self.backed_up:
            backupfile = self.file + '.OLD'
            import shutil
            shutil.copy(self.file, backupfile)
            print """Moving old attributes -> group attributes.
            If you save, your database will not work with older
            versions of GOURMET.
            A backup has been saved in %s"""%backupfile
            self.backed_up = True
        for r in to_move_vw:
            setattr(r,new[0],getattr(r,old[0]))
            setattr(r,old[0],"")

    def setup_table (self, name, data, key=None):
        getstring = name + "["
        # We want to make out "key" the first item in the database
        if key:
            key_index = [x[0] for x in data].index(key)
            data = [data[key_index]] + data[0:key_index] + data[key_index+1:]
        for col,typ in data:
            getstring += "%s:%s,"%(col,self.type_to_metakit_type(typ))
        getstring = getstring[0:-1] + "]"
        debug('Metakit: getting database: %s'%getstring,10)
        db = self.db.getas(getstring)
        if key:
            rhsh = self.db.getas("__%s_hash__[_H:I,_R:I]"%name)
            db = db.hash(rhsh,1)
        return db

    def type_to_metakit_type (self, typ):
        if typ.find('char') >= 0:
            return 's'
        if typ.find('text') >= 0:
            return 's'
        if typ == 'unicode': return 's'
        if typ == 'float': return "F"
        if typ == 'int': return "I"
        if typ == 'binary': return 'B'
        else:
            raise "Can't Understand TYPE %s"%typ
    
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

    def modify_rec (self, rec, dic):
        for k,v in dic.items():
            if hasattr(rec,k):
                self.changed=True
                setattr(rec,k,"%s"%v) #everything's a string.
            else:
                debug("Warning: rec has no attribute %s (tried to set to %s)" %(k,v),1)
        self.run_hooks(self.modify_hooks,rec)

    def ings_search (self, ings, keyed=None, rview=None, use_regexp=True, exact=False):
        """Handed a list of regexps, return a list of recipes containing all
        items."""
        for i in ings:
            rview = self.ing_search(i,keyed=keyed,rview=rview,exact=exact,use_regexp=use_regexp)
        return rview

    def ing_search (self, ing, keyed=None, rview=None, use_regexp=True, exact=False):
        """Handed an ingredient (or, rather, a regexp for an
        ingredient), return a list of recipes. By default
        (keyed=None), we search through keys or item descriptions. If
        'keyed', we search only in keys."""
        iview = self.iview
        if not rview:
            rview=self.rview
        vw = self.search(iview, 'ingkey', ing, use_regexp=use_regexp, exact=exact)
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

    def search (self, table, colname, regexp, exact=0, use_regexp=True):
        """Handed a table, a column name, and a regular expression, search
        for an item"""
        if not use_regexp: regexp = re.escape(regexp)
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
        timeaction = TimeAction('rmetakit.add_rec 1',0)
        self.changed=True
        self.remove_unicode(rdict)
        if not rdict.has_key('id'):
            rdict['id']=self.new_id()
        timeaction.end()
        timeaction = TimeAction('rmetakit.add_rec 2',0)
        old_r=self.get_rec(rdict['id'])
        timeaction.end()
        timeaction = TimeAction('rmetakit.add_rec 3',0)
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
            timeaction.end()
            timeaction = TimeAction('rmetakit.add_rec 4 hooks',0)
            self.run_hooks(self.add_hooks,self.rview[-1])
            timeaction.end()            
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

class RecipeManager (RecData,rdatabase.RecipeManager):
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        RecData.__init__(self,file)
        rdatabase.RecipeManager.__init__(self)

class dbDic (rdatabase.dbDic):
    def __init__ (self, keyprop, valprop, view, db, pickle_key=False):
        rdatabase.dbDic.__init__(self,keyprop, valprop, view, db, pickle_key=False)

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
        if self.pickle_key:
            k=pickle.dumps(k)
        return pickle.loads(getattr(self.vw.select(**{self.kp:k})[0],self.vp))

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
