import os, pickle,re
from gourmet import gglobals
import pythonic_sqlite as psl
import rdatabase
#import rmetakit
from gourmet.gdebug import debug, TimeAction

class RecData (rdatabase.RecData,psl.PythonicSQLite):
    def __init__ (self, filename=os.path.join(gglobals.gourmetdir,'recipes.db'), db="sqlite"):
        self.filename = filename
        self.db = db
        rdatabase.RecData.__init__(self)

    def initialize_connection (self):
        psl.PythonicSQLite.__init__(self,self.filename)

    def setup_tables (self):
        # We don't want to use metakit's version of this!
        rdatabase.RecData.setup_tables(self)

    def setup_table (self, name, data, key=None):
        return self.get_table(name,data,key)

    def delete_rec (self, rec):
        if type(rec)==type(""):
            debug("grabbing rec from id",5)
            rec=self.get_rec(rec)
        self.run_hooks(self.delete_hooks,rec)
        myid = rec.id
        rec.__delete__()
        self.iview.delete({'id':myid})

    def modify_rec (self, rec, dic):
        """Update recipe based on dictionary DIC"""
        self.update('recipe',{'id':rec.id},dic)

    def new_rec (self):
        return self.add_rec({})

    def new_id (self):
        """We reserve a new ID.

        Since we use autoincrement in SQLite, we actually create a new
        database row and return the ID of that object.

        This is of course inefficient, so new_id should only be called
        when we need to reserve a recipe ID before the recipe shows up
        (in other words, when we have a reference to a recipe in an
        import before that recipe has been created).
        """
        r=self.new_rec()
        return r.id
    
    def add_rec (self,rdict):
        t = TimeAction('rsqlite.add_rec',3)
        if rdict.has_key('id'):
            self.update('recipe',{'id':rdict['id']},rdict)
            return self.get_rec(rdict['id'])
        else:
            self.rview.append(rdict)
            return self.rview[-1]
        t.end()

    def save (self):
        #self.get_connection().commit()
        pass # autocommit is on. We do nothing.

    def load (self, filename=None):
        if filename:
            psl.PythonicSQLite.__init__(self,self.filename)

    def get_unique_values (self, colname, table=None):
        if not table: table=self.rview
        return table.get_unique(colname)

    def search (self, table, colname, regexp, exact=False, use_regexp=True):
        """Handed a table, a column name, and a regular expression, search
        for an item"""
        debug('search handed: table:%s, colname:%s, regexp:%s, exact:%s'%(table,colname,regexp,exact),0)
        if type(regexp) != "":
            return table.select(**{colname:regexp})
        if use_regexp:
            # we still convert to sql if we can afford to, given the speed advantage
            if exact: sql = sqlify_regexp(regexp)
            else: sql = regexp_to_sql(regexp)
        else:
            if not exact: sql = regexp + "%"
        if sql:
            return table.select(**{colname:(" LIKE ",sql)})
        else:
            debug('adding filter re.search(%s,getattr(row,%s))'%(regexp,colname),0)
            def fun (row):
                #print 'comparing %s and %s'%(getattr(row,colname),regexp)
                return re.search(regexp,getattr(row,colname),re.IGNORECASE)
            return table.filter(fun)

def regexp_to_sql (regexp):
    debug('regexp_to_sql: base regexp=%s'%regexp,0)
    sq_no_nothing = sqlify_regexp(regexp,ignore_carrot=False,ignore_dollarsign=False)
    if sq_no_nothing: return "%%%s%%"%sq_no_nothing
    sq_nocarrot = sqlify_regexp(regexp,ignore_carrot=False)
    if sq_nocarrot: return "%%%s"%sq_nocarrot
    sq_nodollar = sqlify_regexp(regexp,ignore_dollarsign=False)
    if sq_nodollar: return "%s%%"%sq_nodollar
    else: return sqlify_regexp(regexp)
    

def sqlify_regexp (pattern, ignore_carrot=True, ignore_dollarsign=True):
    """If possible, turn the regexp into a matchable sql pattern.
    If not possible, return None"""
    if ignore_carrot: pattern=re.sub('(?!\\\\)\\\\^','',pattern)
    if ignore_dollarsign: pattern=re.sub('(?!\\\\)\\\\$','',pattern)    
    if not re.search('(?!\\\\)[[^.$*+?{\]|()]',pattern): return pattern.replace('\\','')
    if pattern.find(".*") == len(pattern)-2:
        base = sqlify_regexp(pattern[0:-2])
        if base: return "%s%%"%base
    if pattern.find(".*") == 0:
        base = sqlify_regexp(pattern[2:])
        if base: return "%%%s"%base

class RecipeManager (RecData,rdatabase.RecipeManager):
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.db')):
        RecData.__init__(self)
        rdatabase.RecipeManager.__init__(self)

class dbDic (rdatabase.dbDic):
    def __init__ (self, keyprop, valprop, view, db, pickle_key=False):
        rdatabase.dbDic.__init__(self, keyprop, valprop, view, db, pickle_key=False)

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
