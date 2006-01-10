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
        # set up our top id
        # This is unique to metakit and not part of the normal setup_tables routine
        # since other DBs will presumably have auto-increment built into them.
        self.increment_vw  = self.db.getas('incrementer[view:S,field:S,n:I]')
        self.increment_vw = self.increment_vw.ordered() #ordered vw
        self.vw_to_name = {}
        # we check for old, incompatible table names
        # and fix them before calling our regular setup stuff
        debug('setup_tables called!',3)        
        self.move_old_tables()
        debug('Setup tables',3)
        rdatabase.RecData.setup_tables(self)
        # If we've dumped our data, we want to re-import it!
        if self.import_when_done:
            debug('Do import of old recipes',3)
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
                self.copy_table(
                    old_db,
                    tabl,
                    table_cols=[i[0] for i in desc[1]],
                    prog=lambda p,m: self.pd.set_progress(p/tot+(n*p/tot),m),
                    convert_pickles=True
                    )
                n+=1
            self.pd.set_progress(1.0,'Database successfully converted!')
            debug('Delete reference to old database',3)
            del old_db
        
    def _setup_table (self, *args, **kwargs):
        return self.setup_table(*args,**kwargs)

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
                debug('Setup autoincrement for %s'%name,3)
                row = self.fetch_one(self.increment_vw,**{'view':name,
                                                          'field':col}
                                     )
                debug('Looked up autoincrement row',3)
                if not row:
                    debug('Add new autoincrement row',3)
                    self.increment_vw.append(view=name,field=col,n=1)
            debug('Building metakit getstring %s'%getstring,3)
            getstring += "%s:%s,"%(col,self.type_to_metakit_type(typ))
        if name=='recipe':
            # Hack to allow sorting to work...
            getstring = getstring+'categoryname:S,'
        getstring = getstring[0:-1] + "]"
        debug('Metakit: getting view: %s'%getstring,5)
        vw = self.db.getas(getstring)
        debug('Got view!',5)
        if key:
            if data[key_index][1]=='int': #if typ of key is int
                debug('Make ordered',3)
                vw = vw.ordered()
                debug('Made ordered',3)
            else:
                #debug('Make hash',3)
                rhsh = self.db.getas("__%s_hash__[_H:I,_R:I]"%name)
                vw = vw.hash(rhsh,1)
                #debug('Made hash!',3)
        # Make sure our increment fields are right...
        self.vw_to_name[vw]=name
        debug('Investigate increment rows',3)
        increment_rows = self.increment_vw.select(view=name)
        if increment_rows:
            #for field,row in self.increment_dict[name].items():
            for dbrow in self.increment_vw.select(view=name):                
                field = dbrow.field
                debug("look at row for field:%s"%field,3)
                svw=vw.sort(getattr(vw,field))
                tot = len(svw)
                if tot>1:
                    if tot>getattr(svw[-1],field):
                        print """WTF: increment dicts are foobared. If you see this message, please
                        submit a bug report with the terminal output included.
                        """
                        metakit.dump(svw)
                    else:
                        # Setting increment row's n to the highest number in our DB
                        dbrow.n = getattr(svw[-1],field)
        debug('setup_table done!',2)
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

    def search_recipes (self, searches):
        """Search recipes for columns of values.

        "category" and "ingredient" are handled magically
        """
        rvw = self.rview
        for s in searches:
            print 'on search',s,'using',rvw
            if (s.get('operator','LIKE')=='LIKE'):
                exact = False
                use_regexp = False
            elif s['operator'] in ['=','==']:
                exact = True
                use_regexp = False
            elif s['operator'] == 'REGEXP':
                exact = True
                use_regexp = True
            col = s['column']
            if col=='ingredient':
                nvw = self.ing_search(s['search'],rview=rvw,use_regexp=use_regexp,exact=exact)
            elif col=='category':
                nvw = self.joined_search(rvw, self.catview, 'category', s['search'],
                                         use_regexp=use_regexp, exact=exact)
            else:
                nvw = self.search(rvw,col,s['search'],exact=exact,use_regexp=use_regexp)
            if s.get('logic','AND')=='OR': print "METAKIT DOESN'T YET HANDLE OR"
            rvw = nvw
            if not rvw: return rvw
        return rvw

    def search (self, table, colname, regexp, exact=0, use_regexp=True, recurse=True):
        """Handed a table, a column name, and a regular expression, search
        for an item. Alternatively, the regular expression can just be a value."""
        debug('search %(table)s, %(colname)s, %(regexp)s, %(exact)s, %(use_regexp)s, %(recurse)s'%locals(),5)
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
        props = result_ids.properties()
        #del props['joinedcount']
        result_ids = result_ids.project(props[join_on])
        return table1.join(result_ids,getattr(result_ids,join_on))

    def filter (self, table, func):
        ivw = table.filter(func)
        if ivw:
            return table.remapwith(ivw)
        else:
            return []
    
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

    def do_add_cat (self, catdict):
        self.remove_unicode(catdict)
        return rdatabase.RecData.do_add_cat(self,catdict)

    def do_modify_rec (self, rec, dic):
        if not rec or not dic: return
        # This is a bit ugly, but we need to grab the rec object
        # afresh for changes to "stick".
        rid = rec.id
        rec = self.get_rec(rid)
        if not rec:
            print 'Odd: we find no recipe for ID ',rid
            print 'We cannot modify it with: ',dic
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

    def validate_ingdic (self,ingdic):
        """Unicode seems to cause us trouble!"""
        self.remove_unicode(ingdic)
    
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
        #print 'removing unicode'
        if ingdic.has_key('amount') and not ingdic['amount']: del ingdic['amount']
        self.iview.append(ingdic)
        if self.add_ing_hooks: self.run_hooks(self.add_ing_hooks, self.iview[-1])
        self.changed=True
        return self.iview[-1]

    def delete_ing (self, ing):
        self.iview.delete(ing.__index__)
        self.changed=True

    # Convenience functions
    def fetch_one (self, table, *args, **kwargs):
        # Method 1: locate
        indx,cnt=table.locate(*args,**kwargs)
        if cnt:
            return table[indx]
        else:
            # method 2: find
            new_indx = table.find(*args,**kwargs)
            if new_indx>-1:
                return table[new_indx]
            # method 3: select
            rows = table.select(*args,**kwargs)
            if rows:
                return rows[0]

    def remove_unicode (self, mydict):
        for k,v in mydict.items():
            if v.__class__ == u'hello'.__class__:
                mydict[k]=v.encode('utf8','replace')
            if k.__class__ == u'hello'.__class__:
                v = mydict[k]
                mydict.__delitem__(k)
                mydict[k.encode('utf8','replace')] = v
        #print 'mydict = ',mydict

    def increment_field (self, table, field):
        if type(table)!=str:
            try:
                table = self.vw_to_name[table]
            except:
                try:
                    table = self.vw_to_name[table.__view__]
                except:
                    print "I don't know about the table ",table,'(',field,')'
                    raise
        row = self.fetch_one(self.increment_vw,
                             **{'view':table,
                                'field':field})
        if not row:
            print 'Here are the guts of increment_vw:'
            metakit.dump(self.increment_vw)
            raise 'Very odd: we find no row for table: %s, field: %s'%(table,field)
        row.n += 1
        return row.n

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
            debug('cleaning rec table and dumping data',1)
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


# This Normalizer stuff is really metakit only for now...

quick_norms = {}
quick_rnorms = {}

class Normalizer:
    def __init__ (self, rd, normdic):
        self.__rd__ = rd
        self.__normdic__ = normdic

    def str_to_int (self, k, v):
        if not v: return None
        k=str(k)
        v=str(v)
        if quick_norms.has_key(k):
            if quick_norms[k].has_key(v):
                return quick_norms[k][v]
        else:
            quick_norms[k]={}
            quick_rnorms[k]={}
        normtable = self.__normdic__[k]
        row = self.__rd__.fetch_one(normtable,**{k:v})
        if row:
            quick_norms[k][v]=row.id; quick_rnorms[k][row.id]=v
            return row.id
        else:
            n=self.__rd__.increment_field(normtable,'id')
            if n:
                normtable.append({'id':n,k:v})
                r = normtable[-1]
            else:
                normtable.append({k:v})
                r = normtable[-1]
            quick_norms[k][v]=r.id; quick_rnorms[k][r.id]=v
            return r.id
        
    def int_to_str (self, k, v):
        if quick_rnorms.has_key(k):
            if quick_rnorms[k].has_key(v):
                return quick_rnorms[k][v]
        else:
            quick_rnorms[k]={}
            quick_norms[k]={}
        normtable = self.__normdic__[k]
        if type(v)!=int:
            print "int_to_str says: WTF are you handing me ",v,"for?"
        row = self.__rd__.fetch_one(normtable,id=v)        
        if row:
            sval = getattr(row,k)
            quick_rnorms[k][v]=sval; quick_norms[k][sval]=v
            return getattr(row,k)
        elif v==0:
            return None
        else:
            print "That's odd, I couldn't find ",k,v,type(v)
            print 'Using normtable',normtable,'for k',k
            print 'Fetched row',row
            #metakit.dump(normtable)
            raise KeyError('%s %s does not exist!'%(k,v))
        
class NormalizedView (Normalizer):
    """Some magic to allow normalizing our tables without touching our
    reliance on simple attribute-style access to properties. With this
    beautiful magic, in other words, iview[0].ingkey will give us the
    key even though key is actually normalized through a separate table.
    Similarly, iview.select(ingkey='sugar') will do the proper magic.
    """
    def __init__ (self, view, rd, normdic):
        self.__view__ = view
        Normalizer.__init__(self, rd, normdic)
        self.__normdic__ = normdic

    def __iter__ (self):
        for i in self.__view__:
            yield NormalizedRow(i,self.__rd__,self.__normdic__)

    def __nonzero__ (self): return not not self.__view__

    def __str__ (self): return repr(self)
    
    def __getattr__ (self, attname):
        if attname == '__view__': return self.__view__
        if attname == '__normdic__': return self.__normdic__
        if attname == '__rd__': return self.__rd__
        if attname == '__repr__': return self.__repr__
        if attname == '__join_normed_prop__': return self.__join_normed_prop__
        if attname == '__normalize_dictionary__': return self.__normalize_dictionary__
        if attname == 'sort': return self.sort
        if attname == 'sortrev': return self.sortrev
        if attname == '__iter__': return self.__iter__
        try:
            base_att = getattr(self.__view__,attname)
        except AttributeError:
            raise AttributeError
        if callable(base_att):
            return self.wrap_callable(base_att)
        return base_att
        
    def __setattr__ (self, attname, val):
        if attname in ['__view__',
                       '__normdic__',
                       '__rd__',
                       '__repr__',
                       '__join_normed_prop__',
                       '__normalize_dictionary__',
                       'sort',
                       'sortrev',
                       '__iter__',
                       ]:
            self.__dict__[attname] = val
        else:
            setattr(self.__view__,val)

    def __normalize_dictionary__ (self, d):
        for k,v in d.items():
            if self.__normdic__.has_key(k) and type(v)!=int:
                d[k]=Normalizer.str_to_int(self,k,v)
            elif type(v)==bool: d[k]=int(v)
        return d

    def __getitem__ (self, n): return NormalizedRow(self.__view__[n], self.__rd__, self.__normdic__)
    def __getslice__ (self, a=None, b=None): return NormalizedView(self.__view__[a:b],self.__rd__,self.__normdic__)
    def __len__ (self): return len(self.__view__)

    def wrap_callable (self, f):
        """A meta-function -- we wrap up anything callable in a
        function that replaces arguments doing normalization as necessary.

        We also replace any views or rows that are to be returned with subviews of ourselves.
        """
        import metakit
        def _(*args,**kwargs):
            kwargs=self.__normalize_dictionary__(kwargs)
            for k,v in kwargs.items():
                if type(v)==dict: kwargs[k] = self.__normalize_dictionary__(v)
                if isinstance(v,NormalizedView): kwargs[k]=v.__view__
                if isinstance(v,NormalizedRow): kwargs[k]=v.__row__
            args = [type(a)==dict and self.__normalize_dictionary__(a) or a for a in args]
            args = [(isinstance(a,NormalizedView) and a.__view__) or a for a in args]
            args = [(isinstance(a,NormalizedRow) and a.__row__) or a for a in args]
            ret = f(*args,**kwargs)
            if type(ret)==metakit.RowRefType:
                return NormalizedRow(ret,self.__rd__,self.__normdic__)
            elif type(ret) in [metakit.ViewType, metakit.ViewerType, metakit.ROViewerType]:
                return NormalizedView(ret,self.__rd__,self.__normdic__)
            else:
                return ret
        return _

    def __repr__ (self): return '<Normalized %s>'%self.__view__

    def __join_normed_prop__ (self, prop, subvw=None):
        """Join in a normalized version of our property.

        Return the new property name.
        This is useful for e.g. sorting.

        The reason we can't simply use joins this way for everything
        is that these new joined props are read-only.
        """
        if not subvw: subvw=self.__view__
        normedprop = prop+'lookup'
        if not hasattr(subvw,normedprop):
            normtable = self.__normdic__[prop]
            normtable = normtable.rename(prop,normedprop)
            normtable = normtable.rename('id',prop)
            # do our join -- now we can search by our normedprop
            subvw = subvw.join(normtable,getattr(normtable,
                                                 prop),
                               outer=True)
        return subvw,normedprop
    
    def sort (self, prop):
        # we do some magic sorting...
        #if self.__normdic__.has_key(prop):
        #    prop = self.__join_normed_prop__(prop)
        #sorter = self.wrap_callable(self.__view__.sort)
        #return sorter(prop)
        # Regular sorting is failing for reasons I don't understand
        # So we're just going to use this as a shorthand for sortrev
        return self.sortrev([getattr(self.__view__,prop)],[])

    def sortrev (self, fprops, rprops):
        new_fprops = []
        subvw = self.__view__
        for prop in [p.name for p in fprops]:
            if self.__normdic__.has_key(prop):
                subvw,newprop = self.__join_normed_prop__(prop,subvw)
                new_fprops.append(getattr(subvw,newprop))
            else:
                new_fprops.append(getattr(subvw,prop))
        new_rprops = []
        for prop in [p.name for p in rprops]:
            if self.__normdic__.has_key(prop):
                subvw,newprop = self.__join_normed_prop__(prop,subvw)
                new_rprops.append(getattr(subvw,newprop))
            else:
                new_rprops.append(getattr(subvw,prop))
        sorter = self.wrap_callable(subvw.sortrev)
        return sorter(new_fprops,new_rprops)

class NormalizedRow (Normalizer):
    """Some magic to allow normalizing our tables."""
    def __init__ (self, row, rd, normdic):
        self.__row__ = row
        Normalizer.__init__(self,rd,normdic)

    def __getattr__ (self, attname):
        import metakit
        if attname == '__row__': return self.__row__
        if attname == '__normdic__': return self.__normdic__
        if attname == '__rd__': return self.__rd__
        if attname == '__repr__': return self.__repr__
        base_attr = getattr(self.__row__,attname)
        if self.__normdic__.has_key(attname):
            return Normalizer.int_to_str(self,attname,base_attr)
        elif type(base_attr) in [metakit.ViewType, metakit.ViewerType, metakit.ROViewerType]:
            return NormalizedView(base_attr,self.__rd__,self.__normdic__)
        elif type(base_attr)==metakit.RowRefType:
            return NormalizedRow(base_attr,self.__rd__,self.__normdic__)
        else:
            return base_attr

    def __setattr__ (self, attname, val):
        if attname in ['__normdic__','__row__','__rd__']:
            self.__dict__[attname]=val
            return
        if self.__normdic__.has_key(attname):
            nval = Normalizer.str_to_int(self,attname,val)
            setattr(self.__row__,
                    attname,
                    nval
                    )
        else:
            setattr(self.__row__,attname,val)

    def __repr__ (self): return '<Normalized %s>'%self.__row__


dbDic = rdatabase.dbDic


if __name__ == '__main__':
    import unittest
    import tempfile
    #while os.path.exists(fi+str(n)+'.mk'):
    #    n+=1
    #MetakitUnitTest.db_kwargs['file']=fi+str(n)+'.mk'
    #try:
    #    if __file__:
    #        unittest.main()
    ##    else:
    #         raise
    #except:
    db = RecipeManager(tempfile.mktemp('.mk'))
    rdatabase.test_db(db)
    
    
    
    
