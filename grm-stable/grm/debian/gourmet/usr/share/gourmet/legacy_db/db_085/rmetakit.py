import metakit, re, pickle, string, os.path
import rdatabase
import gourmet.gglobals as gglobals
from gourmet import keymanager,shopping,convert
from gourmet.defaults import lang as defaults
from gourmet.gdebug import *
from gettext import gettext as _

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
        # READ ONLY
        self.db = metakit.storage(str(self.file),0) #filename must be string, not unicode 
        self.contentview=self.db.contents()
        #self.load()
        self.db.autocommit()

    def setup_tables (self):
        # we check for old, incompatible table names
        # and fix them before calling our regular setup stuff
        debug('setup_tables called!',1)
        self._change_row_type(table='ingredients',name='optional',old='char(10)',new='bool',
                              converter=lambda x: x=='yes' and 1 or 0
                              )
        self._move_row(table='ingredients',old=('group','text'),new=('inggroup','text'))
        self._move_row(table='ingredients',old=('key','char(200)'),new=('ingkey','char(200)'))        
        self._move_row(table='shopcats',old=('key','char(50)'),new=('shopkey','char(50)'))
        self._move_row(table='density',old=('key','char(50)'),new=('dkey','char(50)'))        
        self._move_row(table='convtable',old=('key','char(50)'),new=('ckey','char(50)'))
        self._move_row(table='crossunitdict',old=('key','char(50)'),new=('cukey','char(50)'))
        self._move_row(table='unitdict',old=('key','char(50)'),new=('ukey','char(50)'))
        rdatabase.RecData.setup_tables(self)

    def _change_row_type (self, table, name, old, new, converter):
        """Change row named 'name' from type 'old' to type 'new'"""

        # This is quite a complex little problem in pymetakit. I got
        # help from Brian Kelley <fustigator@gmail.com> over the
        # metakit mailing list on this one.  Basically, in order to
        # change the datatype of a column we have to add a dummy
        # column, drop the old column, add the old column back, and
        # copy the information over from our dummy. This is made even
        # stranger by the fact that to drop a column in metakit, you
        # have to call commit().
        
        debug('calling _change_row_type for %s %s %s->%s'%(table,name,old,new))
        # if we don't have this table yet 
        if  not hasattr(self.contentview[0],table)  \
           or not hasattr(getattr(self.contentview[0],table),name):
            return # then there's no need to modify a thing!
        prop = getattr(getattr(self.contentview[0],table),name) # get ourselves the property object
        if prop.type.lower() == self.type_to_metakit_type(old).lower():
            self._backup_database()
            debug('we need to change the type of %s from %s->%s'%(name,old,new),3)
            # we create a view with our old self and a new temporary self
            DUMMYNAME = 'TMP%s'%name
            self._move_row(table,(name,old),(DUMMYNAME,old))            
            # We're going to modify our default setup arguments to drop the proper column and add the new one
            # in its sted before committing. This allows us to "drop" the old version of column 'name'
            dsc=getattr(self,'%s_TABLE_DESC'%table.upper()) #follow rdatabase naming convention i.e. RECIPE_TABLE_DESC
            dsc=list(dsc)[0:] # convert from tuple to list so we can modify
            dsc[1]=dsc[1][0:] #make a copy of our list of columns to modify
            found = False
            print 'using dsc ',dsc
            for n,colinfo in enumerate(dsc[1]):
                print 'looking at column ',colinfo
                if colinfo[0]==name: #colinfo is in form (name,type)
                    found,myindex=True,n
                    break
            if not found: raise "Property %s not in standard description of %s"%(name,table)
            del dsc[1][myindex]
            dsc[1].append((DUMMYNAME,old))
            # this will do a "getas" with our new DUMMYNAME attribute and without our old attribute.
            # committing will mean we drop the row.
            self.setup_table(*dsc)
            debug('dropping column by committing database',3)
            self.db.commit()
            debug('deleting reference to our db',3)
            del self.db
            debug('reinitialize our connection to a new db',3)
            self.initialize_connection() # reinitialize ourselves with our new DUMMYNAME column
            # now we get our new self as a new datatype and copy our new information over...
            newvw = self.setup_table(table,[(name,new),(DUMMYNAME,old)])
            vw = newvw.filter(lambda x: getattr(x,DUMMYNAME))
            to_move_vw = newvw.remapwith(vw)
            debug('converting attributes',4)
            for n,r in enumerate(to_move_vw):
                # convert our attributes
                setattr(r,name,converter(getattr(r,DUMMYNAME)))
                # erase our temporary/holder attribute
                setattr(r,DUMMYNAME,None)
            debug('moved attribute  %s times'%n,3)
            dsc=getattr(self,'%s_TABLE_DESC'%table.upper()) #follow rdatabase naming convention i.e. RECIPE_TABLE_DESC
            self.setup_table(*dsc) #setup our table with the right attrs
            self.db.commit() # and drop our dummy column
        # if our property is neither the old nor the new type, raise an error.
        elif prop.type.lower() != self.type_to_metakit_type(new).lower():
            raise "Property %s is %s, not of old type %s or new type %s!"%(prop.name,
                                                                          prop.type,
                                                                          old, new)
        # note that our DUMMYNAME will be dropped by default once we
        # run the standard setup_tables stuff which will call getas()
        # without the DUMMYNAME

    def _move_row (self, table, old, new):
        """Move data from old (propertyname, type) to new (propertyname, type).

        This is designed for backwards compatability (to allow
        for other database backends)."""
        debug('calling _move_row for %s %s %s'%(table,old,new),7)
        if not hasattr(self.contentview[0],table) or not hasattr(getattr(self.contentview[0],table),old[0]):
            debug('Old property %s doesn\'t exist'%old[0],9)
            return
        tmpview = self.setup_table(table, [new,old])
        vw = tmpview.filter(lambda x: getattr(x,old[0]))
        to_move_vw = tmpview.remapwith(vw)
        to_move = len(to_move_vw)
        if to_move > 0:
            self._backup_database()
            for r in to_move_vw:
                setattr(r,new[0],getattr(r,old[0]))
                setattr(r,old[0],None)

    def _backup_database (self):
        """Create a backup copy of our database tagged with ".OLD" in case we muck things up."""
        if not self.backed_up:
            backupfile = self.file + '.OLD'
            while os.path.exists(backupfile):
                backupfile = backupfile + ".OLD"
            import shutil
            shutil.copy(self.file, backupfile)
            print """
            Your database will not work with older
            versions of GOURMET.
            A backup has been saved in %s"""%backupfile
            import gourmet.dialog_extras, gourmet.version
            gourmet.dialog_extras.show_message(
                label='Database format has changed',
                sublabel='%(progname)s %(version)s has changed the format of its database. Your database will no longer work with older versions of %(progname)s.  A backup has been saved in %(backupfile)s'%{
                'version':gourmet.version.version,
                'progname':gourmet.version.appname,
                'backupfile':backupfile}
                )
            self.backed_up = True

    def setup_table (self, name, data, key=None):
        """Setup a metakit view (table) for generic table description (see superclass rdatabase)."""
        getstring = name + "["
        # We want to make out "key" the first item in the database
        if key:
            key_index = [x[0] for x in data].index(key)
            data = [data[key_index]] + data[0:key_index] + data[key_index+1:]
        for col,typ in data:
            getstring += "%s:%s,"%(col,self.type_to_metakit_type(typ))
        getstring = getstring[0:-1] + "]"
        debug('Metakit: getting view: %s'%getstring,5)
        db = self.db.getas(getstring)
        debug('Got metakit database',5)
        if key:
            rhsh = self.db.getas("__%s_hash__[_H:I,_R:I]"%name)
            db = db.hash(rhsh,1)
        return db

    def type_to_metakit_type (self, typ):
        """Convert a generic database type to a metakit property description."""
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
        """Commit our metakit database to file."""
        debug('saving database to file %s'%self.file,0)
        debug('there are %s recipes in the database'%len(self.rview),0)
        if self.changed:
            self.db.commit()
            self.changed=False

    def load (self, file=None):
        if file:
            self.file = file
        debug('loading database from file %s'%self.file,0)
        fo  = open(self.file,'rb')
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
        self.changed=True

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
        debug('adding recipe: %s'%rdict,0)
        r=rdatabase.RecData.add_rec(self,rdict)
        self.changed=True
        return r
    
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
        self.changed=True
    
    def delete_ing (self, ing):
        self.iview.delete(ing.__index__)
        self.changed=True

    def add_ing (self, ingdic):
        debug('removing unicode',3)
        timer = TimeAction('rmetakit.add_ing 1',0)
        self.remove_unicode(ingdic)
        timer.end()
        debug('adding ingredient: %s'%ingdic,0)
        i=rdatabase.RecData.add_ing(self,ingdic)
        self.changed=True
        return i

class RecipeManager (RecData,rdatabase.RecipeManager):
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        RecData.__init__(self,file)
        rdatabase.RecipeManager.__init__(self)

dbDic = rdatabase.dbDic

if __name__ == '__main__':
    import time
    def timef (f):
        t = time.time()
        f()
        print time.time()-t
    
    db = RecipeManager('/tmp/addeabc/recipes.mk')

