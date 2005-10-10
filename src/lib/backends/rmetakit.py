import metakit, re, pickle, string, os.path
import rdatabase
import gourmet.gglobals as gglobals
from gourmet import keymanager,shopping,convert
from gourmet.defaults import lang as defaults
from gourmet.gdebug import *
from gettext import gettext as _
import gourmet.version
import shutil

class RecData (rdatabase.RecData):

    """A class to keep recipe data in. This class basically is a wrapper for interactions
    with metakit (stored in self.db). Ideally, interactions with metakit should be abstracted
    through this class so that I could easily change to a different database backend."""

    database_change_title = _('Database format has changed')
    database_change_message = _('%(progname)s %(version)s has changed the format of its database. Your database will no longer work with older versions of %(progname)s.  A backup has been saved in %(backupfile)s')%{
        'version':gourmet.version.version,
        'progname':gourmet.version.appname,
        'backupfile':"%(backupfile)s"}
    
    
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        debug('RecData.__init__()',3)
        self.changed=False
        self.file = file
        self.backed_up = False
        self.import_when_done = None
        rdatabase.RecData.__init__(self)

    # Core set-up methods    

    def initialize_connection (self):
        debug('using file: %s'%self.file,1)
        self.file = os.path.expandvars(os.path.expanduser(self.file))
        mydir = os.path.split(self.file)[0]
        # create the directory if it does not yet exist
        if not os.path.exists(mydir):
            os.mkdir(mydir)
        self.db = metakit.storage(str(self.file),1) #filename must be string, not unicode
        self.contentview=self.db.contents()
        #self.load()
        self.db.autocommit()

    def setup_tables (self):
        # we check for old, incompatible table names
        # and fix them before calling our regular setup stuff
        debug('setup_tables called!',1)        
        self.move_old_tables()
        # set up our top id
        # This is unique to metakit and not part of the normal setup_tables routine
        # since other DBs will presumably have auto-increment built into them.
        self.increment_vw  = self.db.getas('incrementer[view:S,field:S,n:I]')
        self.vw_to_name = {}
        self.increment_dict = {}
        #self.top_id_vw.append({'id':1})
        #self.top_id_row = self.top_id_vw[0]
        rdatabase.RecData.setup_tables(self)
        # If we've dumped our data, we want to re-import it!
        if self.import_when_done:            
            old_db,ifi = self.import_when_done
            from gourmet.importers.gxml2_importer import converter 
            converter(
                ifi, self, threaded=False,
                progress=lambda p,m: self.pd.set_progress(p*0.5+0.5,m)
                )
            n = 0
            tot = 3
            for tabl,desc in [('sview',self.SHOPCATS_TABLE_DESC),
                              ('scview',self.SHOPCATSORDER_TABLE_DESC),
                              ('pview',self.PANTRY_TABLE_DESC)]:
                #print old_db,tabl,table_cols=[i[0] for i in desc[1]],prog=lambda p,m: self.pd.set_progress(p/tot+(n*p/tot),m),convert_pickles=True
                self.copy_table(
                    old_db,
                    tabl,
                    table_cols=[i[0] for i in desc[1]],
                    prog=lambda p,m: self.pd.set_progress(p/tot+(n*p/tot),m),
                    convert_pickles=True
                    )
                n+=1
            self.pd.set_progress(1.0,'Database successfully converted!')
            del old_db

    def setup_table (self, name, data, key=None):
        """Setup a metakit view (table) for generic table description (see superclass rdatabase)."""
        debug('setup_table(name=%(name)s,data=%(data)s,key=%(key)s)'%locals(),1)
        getstring = name + "["
        # We want to make our "key" the first item in the database
        if key:
            key_index = [x[0] for x in data].index(key)
            data = [data[key_index]] + data[0:key_index] + data[key_index+1:]
        for col,typ,flags in data:
            if 'AUTOINCREMENT' in flags:
                row = self.fetch_one(self.increment_vw,**{'view':name,
                                                     'field':col}
                                  )
                if not row:
                    self.increment_vw.append(view=name,field=col,n=1)
                    row = self.increment_vw[-1]
                if not self.increment_dict.has_key(name):
                    self.increment_dict[name]={}
                self.increment_dict[name][col]=row
            getstring += "%s:%s,"%(col,self.type_to_metakit_type(typ))
        if name=='recipe':
            getstring = getstring+'categoryname:S,'
        getstring = getstring[0:-1] + "]"
        debug('Metakit: getting view: %s'%getstring,5)
        vw = self.db.getas(getstring)
        debug('Got metakit database',5)
        if key:
            rhsh = self.db.getas("__%s_hash__[_H:I,_R:I]"%name)
            vw = vw.hash(rhsh,1)
        # Make sure our increment fields are right...
        if self.increment_dict.has_key(name):
            self.vw_to_name[vw]=name
            for field,row in self.increment_dict[name].items():
                try:
                    svw=vw.sort(vw.id)
                    if len(svw)>svw[-1].id:
                        print """WTF: increment dicts are foobared. If you see this message, please
                        submit a bug report with the terminal output included.
                        """
                        metakit.dump(svw)
                    self.increment_dict[name][field].n = svw[-1].id
                except IndexError:
                    pass        
        return vw

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

    # Search functions

    def search (self, table, colname, regexp, exact=0, use_regexp=True, recurse=True):
        """Handed a table, a column name, and a regular expression, search
        for an item. Alternatively, the regular expression can just be a value."""
        debug('search %(table)s, %(colname)s, %(regexp)s, %(exact)s, %(use_regexp)s, %(recurse)s'%locals(),5)
        if (recurse
            and
            self.normalizations.has_key(colname)
            and
            isinstance(table,rdatabase.NormalizedView)
            ):
            nsrch = self.search(self.normalizations[colname],colname,regexp,exact,use_regexp,recurse=False)
            if not nsrch: return []
            nsrch = nsrch.rename(colname,'text')
            nsrch = nsrch.rename('id',colname)
            rvw = table.join(nsrch,getattr(table.__view__,colname))
            return rvw
        if type(regexp)==type(""):
            regexp=str(regexp)
        if exact and not use_regexp: return table.select(**{colname:regexp})
        if not use_regexp: regexp = re.escape(regexp)
        if exact:
            indexvw = table.filter(lambda r: re.match(regexp, "%s"%getattr(r,colname)))
        else:
            indexvw = table.filter(lambda r: re.search(regexp,"%s"%getattr(r,colname),re.I))
        if indexvw:
            resultvw = table.remapwith(indexvw)
            resultvw = resultvw.unique()
            return resultvw
        return []

    def ings_search (self, ings, keyed=None, rview=None, use_regexp=True, exact=False):
        """Handed a list of regexps, return a list of recipes containing all
        items."""
        for i in ings:
            rview = self.ing_search(i,keyed=keyed,rview=rview,exact=exact,use_regexp=use_regexp)
        return rview

    def joined_search (self, table1, table2, search_by, search_str,
                       use_regexp=True, exact=False, join_on='id'):
        table2 = table2.join(table1,getattr(table1,join_on))
        vw = self.search(table2, search_by, search_str, use_regexp=use_regexp, exact=exact)
        if not vw: return []
        result_ids = vw.counts(getattr(vw,join_on),
                               'joinedcount')
        return table1.join(result_ids,getattr(result_ids,join_on))

    def filter (self, table, func):
        ivw = table.filter(func)
        return table.remapwith(ivw)
    
    # convenience function
    def delete_by_criteria (self, table, criteria):
        """Delete table by criteria"""
        cur = table.select(**criteria)
        if cur:
            table.remove(table.indices(cur))

    # Our versions of convenience functions for adding/modifying
    # recipe stuff

    def do_add_rec (self, rdict):
        self.remove_unicode(rdict)
        debug('adding recipe: %s'%rdict,5)
        r=rdatabase.RecData.do_add_rec(self,rdict)
        self.changed=True
        return r

    def do_modify_rec (self, rec, dic):
        if not rec or not dic: return
        # This is a bit ugly, but we need to grab the rec object
        # afresh for changes to "stick".
        rid = rec.id
        rec = self.get_rec(rid)
        if not rec:
            print 'Odd: we find no recipe for ID ',rid
            return
        for k,v in dic.items():
            if hasattr(rec,k):
                self.changed=True
                debug('do_modify_rec: setattr %s %s->%s'%(rec,k,v),10)
                setattr(rec,k,v)
            else:
                debug("Warning: rec has no attribute %s (tried to set to %s)" %(k,v),1)
        debug('running hooks',3)
        self.run_hooks(self.modify_hooks,rec)
        self.changed=True
        ## delete this code when we've figured out wtf is going on with this not sticking
        #for attr in dic.keys():
        #    debug('modified recipe %s->%s'%(attr,getattr(rec,attr)),1)
        return rec
    
    def do_add_ing (self, ingdic):
        """Add ingredient to iview based on ingdict and return
        ingredient object. Ingdict contains:
        id: recipe_id
        unit: unit
        item: description
        key: keyed descriptor
        alternative: not yet implemented (alternative)
        #optional: yes|no
        optional: True|False (boolean)
        position: INTEGER [position in list]
        refid: id of reference recipe. If ref is provided, everything
               else is irrelevant except for amount.
        """
        self.remove_unicode(ingdic)
        if ingdic.has_key('amount') and not ingdic['amount']: del ingdic['amount']
        self.iview.append(ingdic)
        if self.add_ing_hooks: self.run_hooks(self.add_ing_hooks, self.iview[-1])
        self.changed=True
        return self.iview[-1]

    def do_add_cat (self, dic):
        self.catview.append(dic)
    
    def delete_ing (self, ing):
        self.iview.delete(ing.__index__)
        self.changed=True

    # Convenience functions

    def fetch_one (self, table, *args, **kwargs):
        indx=table.find(*args,**kwargs)
        if indx >= 0:
            return table[indx]
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

    def increment_field (self, table, field):
        if type(table)!=str:
            table = self.vw_to_name[table]
        self.increment_dict[table][field].n += 1
        return self.increment_dict[table][field].n


    # Backup / Restructuring methods -- these are special methods to
    # help us with our restructuring of the database - updating from
    # old versions.

    def move_old_tables (self):
        self._move_row(table='ingredients',old=('group','text'),new=('inggroup','text'))
        self._move_row(table='ingredients',old=('key','char(200)'),new=('ingkey','char(200)'))        
        self._move_row(table='shopcats',old=('key','char(50)'),new=('shopkey','char(50)'))
        self._move_row(table='density',old=('key','char(50)'),new=('dkey','char(50)'))        
        self._move_row(table='convtable',old=('key','char(50)'),new=('ckey','char(50)'))
        self._move_row(table='crossunitdict',old=('key','char(50)'),new=('cukey','char(50)'))
        self._move_row(table='unitdict',old=('key','char(50)'),new=('ukey','char(50)'))
        # If our recipe or ingredient tables are of the wrong type,
        # we're simply going to dump the recipe portion of our DB into
        # a file and reload it. This is ugly, but changing row types
        # is simply too tricky in metakit and I've had it with
        # segfaults and data corruption! At the very least, this
        # method ensures the user has an XML copy of their data if the
        # DB gets screwed up.
        if (
            (hasattr(self.contentview[0],'ingredients') and
             (self._row_type('ingredients','optional') != 'i' or
              self._row_type('ingredients','id')!='i' or
              self._row_type('ingredients','refid')!='i')
             )
            or
            (hasattr(self.contentview[0],'recipe') and
             (self._row_type('recipe','id')!='i' 
              or self._row_type('recipe','rating')!='i'
              or self._row_type('recipe','cooktime')!='i' # To be implemented in the future
              or self._row_type('recipe','preptime')!='i'              
              or self._row_type('recipe','cuisine')!='i' # of if we're not normalized
              or (hasattr(self.contentview[0],'recipe') and # of ir we still have 1-category-only
                  hasattr(self.contentview[0].recipe,'category')
                  )
              )
             )
            ):
            self.clean_recs_table_and_dump_data()

    def copy_table (self, old_db, table_name, table_cols,
                    prog=None,convert_pickles=False):
        """Copy columns of table from old database to ourselves.

        Old database should be an instance of RecDataOld.  Any format
        changes that need to happen must happen magically, not here."""
        oldvw = getattr(old_db,table_name)
        tot = len(oldvw)
        newvw = getattr(self,table_name)
        if convert_pickles:
            import pickle
            def unpickle (o):
                try: return pickle.loads(o)
                except: return o
        for n,row in enumerate(oldvw):
            if n % 10: prog(float(n)/tot, "Copying other data...%s"%table_name)
            if convert_pickles:
                newvw.append(
                    dict([(col,unpickle(getattr(row,col))) for col in table_cols])
                    )
            else:
                newvw.append(
                    dict([(col,getattr(row,col)) for col in table_cols])
                    )
        
    def clean_recs_table_and_dump_data (self):
        """Clean out our recipe table and dump our data for later recovery.
        We return an old version of the DB and a file with our recipes.
        """
        # Backup our DB
        self._backup_database_file()
        # Get ourselves out of memory
        subrm = RecDataOldDB(self.backupfile)
        from gourmet.exporters import gxml2_exporter
        #print 'Our old DB looked like this: '
        #print subrm.db.description()
        #print 'And had'
        #print len(subrm.rview),'recipes'
        #print 'and '
        #print len(subrm.iview),'ingredients'
        # dump our recipe db to a backup file
        dumpfile = os.path.join(
            os.path.split(self.file)[0],
            'recipe_backup_%s.grmt'%(time.strftime('%m-%d-%y'))
            )
        self._backup_database_and_make_progress_dialog(dumpfile)
        ofi = file(dumpfile,'w')
        gxml2_exporter.rview_to_xml(
            subrm,
            subrm.rview,
            ofi,
            one_file=True,
            progress_func=lambda p,m: self.pd.set_progress(p*0.5,m)
            ).run()
        ofi.close()
        # Now we drop our tables...
        #self.db.getas('ingredients')
        #self.db.getas('recipe')
        # And commit
        #self.db.commit()
        
        # Move our current file out of the way so we can start a new
        # one, deleting reference to the file so Windows won't
        # complain
        del self.db
        shutil.move(self.file,self.file+'.trash')
        # Restart our connection
        self.initialize_connection()
        # and later on, we'd better import file
        self.import_when_done = subrm,dumpfile

    def _change_row_types (self, changes):
        """Change row named 'name' from type 'old' to type 'new'

        changes = [(table, name, old, new, converter),...]

        We have to make all changes at once or bad things will happen.
        """
        # This is quite a complex little problem in pymetakit. I got
        # help from Brian Kelley <fustigator@gmail.com> over the
        # metakit mailing list on this one.  Basically, in order to
        # change the datatype of a column we have to add a dummy
        # column, drop the old column, add the old column back, and
        # copy the information over from our dummy. This is made even
        # stranger by the fact that to drop a column in metakit, you
        # have to call getas() without the column and then call
        # commit() and nuke any reference to the db.
        
        # if we don't have this table yet, then we don't need to do anything        
        DUMMIES = {}
        change_dic = {}
        default_descs = {}
        dummy_descs = {}
        for table,name,old,new,converter in changes:
            if not hasattr(self.contentview[0],table):
                continue
            if not default_descs.has_key(table):
                default_descs[table]=self.db.description(table)
            if not dummy_descs.has_key(table):
                dummy_descs[table]=default_descs[table]
            if self._row_type(table,name) == self.type_to_metakit_type(new).lower():
                continue
            self._backup_database()
            # we create a view with our old self and a new temporary self
            DUMMIES[name] = 'TMP%s'%name
            if not change_dic.has_key(table):
                change_dic[table]={}
            change_dic[table][name]={}
            change_dic[table][name]['old']=old
            change_dic[table][name]['new']=new
            change_dic[table][name]['converter']=converter
            self._move_row(table,(name,old),(DUMMIES[name],old))
            # We're going to modify our default setup arguments to
            # drop the proper column and add the new one in its sted
            # before committing. This allows us to "drop" the old
            # version of column 'name'
            dummy_descs[table] = re.sub("(,|^)%s:"%re.escape(name),
                                        r"\1%s:"%re.escape(DUMMIES[name]),
                                        dummy_descs[table])
        if DUMMIES:
            # Drop our old columns...
            for table,dummy_desc in dummy_descs.items():
                self.db.getas("%s[%s]"%(table,dummy_desc))
            debug('dropping columns by committing database',3)
            self.db.commit()
            debug('deleting reference to our db',3)
            del self.db
            debug('reinitialize our connection to a new db',3)
            #self.initialize_connection() # reinitialize ourselves
            #with our new DUMMYNAME column
            self.db = metakit.storage(self.file,1)
            self.contentview = self.db.contents()
            # now we get our new self as a new datatype and copy our
            # new information over...
            # Loop through the changes we have to make
            for table,cd in change_dic.items():
                for name,change in cd.items():
                    newvw = self.setup_table(table,[(name,change['new']),(DUMMIES[name],change['old'])])
                    vw = newvw.filter(lambda x: getattr(x,DUMMIES[name]))
                    to_move_vw = newvw.remapwith(vw)
                    debug('converting attributes',4)
                    for n,r in enumerate(to_move_vw):
                        # convert our attributes
                        setattr(r,name,change['converter'](getattr(r,DUMMIES[name])))
                        # erase our temporary/holder attribute
                        setattr(r,DUMMIES[name],None)
                    debug('moved attribute  %s times'%n,3)
                default_descs[table] = re.sub(
                    "(,|^)%s:%s"%(name,self.type_to_metakit_type(change['old'])),
                    r"\1%s:%s"%(name,self.type_to_metakit_type(change['new'])),
                    default_descs[table]
                    )
            for table,finished_desc in default_descs.items():
                self.db.getas("%s[%s]"%(table,finished_desc)) #setup our table with the right attrs
            self.db.commit() # and drop our dummy column

    def _move_row (self, table, old, new, converter=None):
        """Move data from old (propertyname, type) to new (propertyname, type).

        This is designed for backwards compatability (to allow
        for other database backends)."""
        debug('_move_row(table=%(table)s old=%(old)s new=%(new)s converter=%(converter)s'%locals(),1)
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
                if converter:
                    setattr(r,new[0],converter(getattr(r,old[0])))
                else:
                    setattr(r,new[0],getattr(r,old[0]))
                setattr(r,old[0],None)

    def _backup_database_file (self):
        """Create a backup copy of our database tagged with ".OLD" in case we muck things up."""
        if not self.backed_up:
            backupfile = self.file + '.OLD'
            n = 1
            while os.path.exists(backupfile):
                backupfile = re.split('[0-9]*[.]OLD',backupfile)[0]
                backupfile = backupfile +  str(n) + '.OLD'
                n += 1            
            shutil.copy(self.file, backupfile)
            self.backupfile = backupfile
            self.backed_up = True

    def _backup_database (self):
        if not self.backed_up:
            self._backup_database_file()
            print """
            Your database will not work with older
            versions of GOURMET.
            A backup has been saved in %s"""%self.backupfile
            import gourmet.dialog_extras, gourmet.version
            gourmet.dialog_extras.show_message(
                label=self.database_change_title,
                sublabel=self.database_change_message%{'backupfile':self.backupfile},
                )

    def _backup_database_and_make_progress_dialog (self, xmlbackup):
        self._backup_database_file()
        from gourmet.dialog_extras import ProgressDialog
        subl = self.database_change_message%{'backupfile':self.backupfile}
        subl += "\n"
        subl += _("In case anything goes wrong, a backup copy of your recipe database is being exported to %s")%xmlbackup
        self.pd = ProgressDialog(
            title=_("Transferring data to new database format"),
            label=self.database_change_title,
            sublabel=subl,
            pause=False,
            stop=False)
        self.pd.show()

    def _row_type (self, table, name):
        """Return the row type for the table named name"""
        if not hasattr(self.contentview[0],table): return 
        prop = getattr(getattr(self.contentview[0],table),name) # get ourselves the property object
        return prop.type.lower()

class RecDataOldDB (RecData):
    """We initialize our database with whatever the old settings were.

    This is done to simplify database transitions, or rather, to move
    the onus of db transitions onto our gxml exporters. Those
    exporters are now responsible for exporting
    """

    NORMALIZED_COLS = []
    
    def initialize_connection (self):
        # identical to parent class, except that we open the DB read-only
        debug('using file: %s'%self.file,1)
        self.file = str(os.path.expandvars(os.path.expanduser(self.file)))
        mydir = os.path.split(self.file)[0]
        # create the directory if it does not yet exist
        if not os.path.exists(mydir):
            os.mkdir(mydir)
        self.db = metakit.storage(self.file,0) #filename must be string, not unicode
        self.contentview=self.db.contents()

    def setup_tables (self):
        self.NORMALIZED_TABLES = []
        rdatabase.RecData.setup_tables(self)
        # We have some columns that need renaming...
        for table,old,new in [('sview','shopkey','ingkey'),
                              ('sview','category','shopcategory'),
                              ('scview','category','shopcategory'),
                              ('pview','itm','ingkey'),]:
            if hasattr(getattr(self,table,),old):
                setattr(self,table,getattr(self,table).rename(old,new))

    def setup_table (self, name, data, key=None):
        try:
            desc = self.db.description(name)
        except KeyError:
            return None
        getstring = name+'['+desc+']'
        db = self.db.getas(getstring)
        if key:
            rhsh = self.db.getas("__%s_hash__[_H:I,_R:I]"%name)
            db = db.hash(rhsh,1)
        return db

class RecipeManager (RecData,rdatabase.RecipeManager):
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.mk')):
        RecData.__init__(self,file)
        self.km = keymanager.KeyManager(rm=self)


dbDic = rdatabase.dbDic

if __name__ == '__main__':
    import time
    def timef (f):
        t = time.time()
        f()
        print time.time()-t
    
    db = RecipeManager('/tmp/addeabc/recipes.mk')
    
    
    
