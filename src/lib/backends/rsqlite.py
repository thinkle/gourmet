import os, pickle,re
from gourmet import gglobals
import pythonic_sqlite as psl
import rdatabase
import traceback
#import rmetakit
from gourmet.gdebug import debug, TimeAction

class RecData (rdatabase.RecData,psl.PythonicSQLite):
    def __init__ (self, filename=os.path.join(gglobals.gourmetdir,'recipes.db'), db="sqlite"):
        self.filename = filename
        self.db = db
        rdatabase.RecData.__init__(self)

    def initialize_connection (self):
        psl.PythonicSQLite.__init__(self,self.filename)

    #def setup_tables (self):
    #    # We don't want to use metakit's version of this!
    #    rdatabase.RecData.setup_tables(self)

    def setup_table (self, name, data, key=None):
        #print 'CREATING: ',name,data        
        return self.get_table(name,data,key) #PythonicSQL's method

    def _setup_table (self, name, data, key=None):
        # Do our normalizing...
        # We'll set up our regular table
        ret = self.setup_table(name,data,key=key)
        # Then we'll set up a view with proper joins
        # to access it via "normalized" columns.
        #return
        columns = [d[0] for d in data]
        if True in [self.normalizations.has_key(d[0]) for d in data]:
            return self.get_view(name,data)
        else:
            return ret

    def do_delete_rec (self, rec):
        if type(rec)==type(""):
            debug("grabbing rec from id",5)
            rec=self.get_rec(rec)
        self.run_hooks(self.delete_hooks,rec)
        myid = rec.id
        rec.__delete__()
        self.iview.delete({'id':myid})

    def new_rec (self):
        return self.add_rec({'title':_('New Recipe')})
    
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
    
    def do_add_rec (self,rdict):
        if rdict.has_key('id'):
            self.update('recipe',{'id':rdict['id']},rdict)
            return self.get_rec(rdict['id'])
        else:
            self.rview.append(rdict)
            return self.rview[-1]

    def do_modify_rec (self, rec, dic):
        if not rec or not dic: return
        self.update(self.rview.__tablename__,
                    {'id':rec.id},
                    dic)
        return self.get_rec(rec.id)

    def do_modify_ing (self, ing, ingdict):
        self.update(self.iview.__tablename__,
                    ing.__fields__,
                    ingdict)

    def save (self):
        self.get_connection().commit()

    def load (self, filename=None):
        if filename:
            psl.PythonicSQLite.__init__(self,self.filename)

    def get_unique_values (self, colname, table=None):
        if table==None: table=self.rview
        if colname=='category' and table.__tablename__==self.rview.__tablename__:
            print "WARNING: you're calling get_unique_values on rview instead of on catview!"
            print "Correcting your mistake, but you should fix this -- here's the traceback:"
            traceback.print_stack()
            table=self.catview
        return table.get_unique(colname)

    def search (self, table, colname, regexp, exact=False, use_regexp=True):
        """Handed a table, a column name, and a regular expression, search
        for an item"""
        debug('search handed: table:%s, colname:%s, regexp:%s, exact:%s'%(table,colname,regexp,exact),0)
        #print 'Doing search...'
        if type(regexp) != str:
            print 'This is funny...',table,colname,regexp
            tbl = table.select(**{colname:regexp})
            print 'we got ',tbl
            return tbl
        if use_regexp:
            # we still convert to sql if we can afford to, given the speed advantage
            if exact: sql = sqlify_regexp(regexp)
            else: sql = regexp_to_sql(regexp)
        else:
            if not exact: sql = regexp + "%"
        if sql:
            tbl=table.select(**{colname:(" LIKE ",sql)})
            print 'returning tbl',tbl
            return tbl
        else:
            debug('adding filter re.search(%s,getattr(row,%s))'%(regexp,colname),0)
            def fun (row):
                #print 'comparing %s and %s'%(getattr(row,colname),regexp)
                return re.search(regexp,getattr(row,colname),re.IGNORECASE)
            tbl = table.filter(fun)
            print '(filter) returning tbl',tbl
            return tbl

    def delete_by_criteria (self, table, criteria):
        table.delete(criteria)

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
    pass


# The table can basically be the same -- it just needs to refer to a
# view of the proper join. What needs to be subclassed is the
# RowObject, whose setitem method will need to be tweaked to do the
# right thing.
# This should be moved to PythonicSQL really...

#class SqlNormalizedTableObject (TableObject):
#    """Provide smooth access to normalized columns.
#
#    In other words, if we store e.g. cuisines as a numeric ID, this
#    class allows us to pretend we are just setting a string when we
#    set a cuisine, and it will automagically convert to an ID.
#    """
#    #def __init__ (self,view,rd,normdic):
#
#    # Methods that call DB functions that return something we'll need
#    # to care about are
    
        

#class SQLiteUnitTest (rdatabase.DatabaseUnitTest):
#D    db_class = RecData
#  #  db_kwargs = {'filename':'/tmp/foo.db'}

if __name__ == '__main__':
    db = RecipeManager(file='/tmp/foo.db')
    rdatabase.test_db(db)
#    import unittest
#    unittest.main()

