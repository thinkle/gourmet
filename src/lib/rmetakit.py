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
        #self.load()
        self.db.autocommit()
        self.db.commit()

    def setup_tables (self):
        # we check for old, incompatible table names
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
        if to_move > 0 and not self.backed_up:
            backupfile = self.file + '.OLD'
            import shutil
            shutil.copy(self.file, backupfile)
            print """Moving old attributes -> group attributes.
            Your database will not work with older
            versions of GOURMET.
            A backup has been saved in %s"""%backupfile
            import dialog_extras, version
            dialog_extras.show_message(
                label='Database format has changed',
                sublabel='%(progname)s %(version)s has changed the format of its database. Your database will no longer work with older versions of %(progname)s.  A backup has been saved in %(backupfile)s'%{'version':version.version,
                                                                                                                                                                                                               'progname':version.appname,
                                                                                                                                                                                                               'backupfile':backupfile}
                )
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
        if typ.find('bool') >= 0:
            return 'I'
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
        self.db.autocommit()
        fo.close()

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
        for an item. Alternatively, the regular expression can just be a value."""
        if type(regexp)==type(""):
            regexp=str(regexp)
        if not use_regexp: regexp = re.escape(regexp)
        if exact:
            indexvw = table.filter(lambda r: re.match(regexp, "%s"%getattr(r,colname)))
        else:
            indexvw = table.filter(lambda r: re.search(regexp,"%s"%getattr(r,colname),re.I))
        resultvw = table.remapwith(indexvw)
        resultvw = resultvw.unique()
        return resultvw

    def get_ings_old (self, rec):
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
            retview = self.iview.select(id=rec,deleted=False)
            return retview

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
        self.remove_unicode(rdict)
        rdatabase.RecData.add_rec(self,rdict)
    
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
    
    def new_rec (self):
        blankdict = {'id':self.new_id(),
                     'title':_('New Recipe'),
                     'servings':'4'}
        return self.add_rec(blankdict)

    def delete_ing (self, ing):
        self.iview.delete(ing.__index__)
        self.changed=True        

    def add_ing (self, ingdic):
        debug('removing unicode',3)
        timer = TimeAction('rmetakit.add_ing 1',0)
        self.remove_unicode(ingdic)
        timer.end()
        rdatabase.RecData.add_ing(self,ingdic)

class RecipeManager (RecData,rdatabase.RecipeManager):
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        RecData.__init__(self,file)
        rdatabase.RecipeManager.__init__(self)

dbDic = rdatabase.dbDic
