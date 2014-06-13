from gettext import gettext as _
from gourmet import ImageExtras, Undo, keymanager, convert
from gourmet.defaults import lang as defaults
from gourmet.gdebug import debug, TimeAction, debug_decorator
from gourmet.plugin import DatabasePlugin
from gourmet.plugin_loader import Pluggable, pluggable_method
import StringIO
import gourmet.gglobals as gglobals
import gourmet.recipeIdentifier as recipeIdentifier
import gourmet.version
import re, string, os.path, time
import shutil
import types

import sqlalchemy
from sqlalchemy import Integer, LargeBinary, String, Float, Boolean, Numeric, Column, ForeignKey, Text
from sqlalchemy.sql import and_, or_, case 
from sqlalchemy import event, func
from gourmet.models.meta import Base, Session, new_db
from gourmet.models import Category, Convtable, CrossUnit, Density, \
    Ingredient, KeyLookup, Pantry, PluginInfo, Recipe, ShopCat, ShopCatOrder, \
    Unitdict, VersionInfo

def map_type_to_sqlalchemy (typ):
    """A convenience method -- take a string type and map it into a
    sqlalchemy type.
    """
    if typ=='int': return Integer()
    if typ.find('char(')==0:
        return String(
            length=int(typ[typ.find('(')+1:typ.find(')')])
            )
    if typ=='text': return Text()
    if typ=='bool': return Boolean()
    if typ=='float': return Float()
    if typ=='binary': return LargeBinary()

def fix_colnames (dict, *tables):
    """Map column names to sqlalchemy columns.
    """
    # This is a convenience method -- throughout Gourmet, the column
    # names are handed around as strings. This converts them into the
    # object sqlalchemy prefers.
    newdict =  {}
    for k,v in dict.items():
        got_prop = False
        for t in tables:
            try:
                newdict[getattr(t.c,k)]=v
            except:
                1
            else:
                got_prop = True
        if not got_prop: raise ValueError("Could not find column %s in tables %s"%(k,tables))
    return newdict

def make_simple_select_arg (criteria,*tables):
    args = []
    for k,v in fix_colnames(criteria,*tables).items():
        if type(v)==str:
            v = unicode(v)
        if type(v)==tuple:
            operator,value = v
            if type(value)==str:
                value = unicode(value)
            if operator=='in':
                args.append(k.in_(value))
            elif hasattr(k,operator):
                args.append(getattr(k,operator)(value))
            elif hasattr(k,operator+'_'): # for keywords like 'in'
                args.append(getattr(k,operator+'_')(value))
            else:
                args.append(k.op(operator)(value))
        else:
            args.append(k==v)
    if len(args)>1:
        return [and_(*args)]
    elif args:
        return [args[0]]
    else:
        return []

def make_order_by (sort_by, table, count_by=None, join_tables=[]):
    ret = []
    for col,direction in sort_by:        
        if col=='count' and not hasattr(table.c,'count'):
            col = sqlalchemy.func.count(getattr(table.c,count_by))
        else:
            if hasattr(table.c,col):
                col = getattr(table.c,col)
            elif join_tables:
                broken = True
                for t in join_tables:
                    if hasattr(t.c,col):
                        broken = False
                        col = getattr(t.c,col)
                        break
                if broken:
                    raise ValueError("No such column for tables %s %s: %s"%(table, join_tables, col))
        if isinstance(col.type, Text):
            # Sort nulls last rather than first using case statement...
            col = case([(col == None, '"%s"'%'z'*20),
                        (col == '', '"%s"'%'z'*20),
                        ],else_=func.lower(col))
        if direction==1: # Ascending
            ret.append(sqlalchemy.asc(col))
        else:
            ret.append(sqlalchemy.desc(col))
    return ret
    
class DBObject:
    pass
# CHANGES SINCE PREVIOUS VERSIONS...
# categories_table: id -> recipe_id, category_entry_id -> id
# ingredients_table: ingredient_id -> id, id -> recipe_id

class RecData (Pluggable): 

    """RecData is our base class for handling database connections.

    Subclasses implement specific backends, such as sqlite, etc."""

    # constants for determining how to get amounts when there are ranges.
    AMT_MODE_LOW = 0
    AMT_MODE_AVERAGE = 1
    AMT_MODE_HIGH = 2

    _singleton = {}

    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'recipes.db'),
                  custom_url=None):
        # hooks run after adding, modifying or deleting a recipe.
        # Each hook is handed the recipe, except for delete_hooks,
        # which is handed the ID (since the recipe has been deleted)
        if RecData._singleton.has_key(file):
            raise RecData._singleton[file]
        else:
            RecData._singleton[file] = self
        # We keep track of IDs we've handed out with new_id() in order
        # to prevent collisions
        self.new_ids = []
        self._created = False
        if custom_url:
            self.url = custom_url
            self.filename = None
        else:
            self.filename = file
            self.url = 'sqlite:///' + self.filename
        self.add_hooks = []
        self.modify_hooks = []
        self.delete_hooks = []
        self.add_ing_hooks = []
        timer = TimeAction('initialize_connection + setup_tables',2)
        self.initialize_connection()
        Pluggable.__init__(self,[DatabasePlugin])            
        self.setup_tables()
        Base.metadata.create_all(self.db)
        self.update_version_info(gourmet.version.version)
        self._created = True
        timer.end()

    # Basic setup functions

    def initialize_connection (self):
        """Initialize our database connection.
        
        This should also set self.new_db accordingly"""
        debug('Initializing DB connection',1)
        def instr(s,subs): return s.lower().find(subs.lower())+1
            
        # End REGEXP workaround 

        # Continue setting up connection...
        if self.filename:
            self.new_db = not os.path.exists(self.filename)
            #print 'Connecting to file ',self.filename,'new=',self.new_db
        else:
            self.new_db = True # ??? How will we do this now?
        #self.db = sqlalchemy.create_engine(self.url,strategy='threadlocal')
        #self.base_connection = self.db

        if self.url.startswith('mysql'):
            self.db = sqlalchemy.create_engine(self.url,
                                               connect_args = {'charset':'utf8'})
        else:
            self.db = sqlalchemy.create_engine(self.url)

        if self.url.startswith('sqlite'):
            # Workaround to create REGEXP function in sqlite
            # New way of adding custom function ensures we create a custom
            # function for every connection created and fixes problems
            # using regexp. Based on code found here:
            # http://stackoverflow.com/questions/8076126/have-an-sqlalchemy-sqlite-create-function-issue-with-datetime-representation
            def regexp(expr, item):
                if item:
                    return re.search(expr,item,re.IGNORECASE) is not None
                else:
                    return False

            @event.listens_for(self.db, 'connect')
            def on_connect (dbapi_con, con_record):
                dbapi_con.create_function('REGEXP',2,regexp)

        self.base_connection = self.db.connect()
        self.base_connection.begin()
        self.metadata = sqlalchemy.MetaData(self.db)
        # Be noisy... (uncomment for debugging/fiddling)
        # self.metadata.bind.echo = True
        Session.configure(bind=self.db)
        debug('Done initializing DB connection',1)

    def save (self):
        """Save our database (if we have a separate 'save' concept)"""
        session = Session()
        stored_info = session.query(VersionInfo).one()
        if stored_info:
            stored_info.last_access = time.time()
            stored_info = session.merge(stored_info)
        else: # This shouldn't really happen
            session.add(VersionInfo(last_access=time.time()))
        session.commit()

    @pluggable_method
    def setup_tables (self):
        """
        Subclasses should do any necessary adjustments/tweaking before calling
        this function."""
        # VersionInfo table - for versioning info
        self.__table_to_object__ = {}
        self.setup_base_tables()
        self.setup_shopper_tables() # could one day be part of a plugin

    def setup_base_tables (self):
        self.setup_info_table()
        self.setup_recipe_table()
        self.setup_category_table()
        self.setup_ingredient_table()        
        
    def setup_info_table (self):
        self.info_table = VersionInfo.__table__
        self.plugin_info_table = PluginInfo.__table__

    def setup_recipe_table (self):
        self.recipe_table = Recipe.__table__

    def setup_category_table (self):
        self.categories_table = Category.__table__

    def setup_ingredient_table (self):
        self.ingredients_table = Ingredient.__table__

    def setup_keylookup_table (self):
        self.keylookup_table = KeyLookup.__table__

    def setup_shopcats_table (self):
        self.shopcats_table = ShopCat.__table__

    def setup_shopcatsorder_table (self):
        self.shopcatsorder_table = ShopCatOrder.__table__

    def setup_pantry_table (self):
        self.pantry_table = Pantry.__table__

    def setup_density_table (self):
        self.density_table = Density.__table__

    def setup_crossunitdict_table (self):
        self.crossunitdict_table = CrossUnit.__table__

    def setup_unitdict_table (self):
        self.unitdict_table = Unitdict.__table__

    def setup_convtable_table (self):
        self.convtable_table = Convtable.__table__

    def setup_shopper_tables (self):
        self.setup_keylookup_table()
        self.setup_shopcats_table()
        self.setup_shopcatsorder_table()
        self.setup_pantry_table()
        self.setup_density_table()
        self.setup_crossunitdict_table()
        self.setup_unitdict_table()
        self.setup_convtable_table()

    def backup_db (self):
        """Make a backup copy of the DB -- this ensures experimental
        code won't permanently screw our users."""
        import time, os.path
        backup_file_name = self.filename + '.backup-' + time.strftime('%d-%m-%y')
        while os.path.exists(backup_file_name):
            backup_file_name += 'I'
        print 'Making a backup copy of DB in ',backup_file_name
        print 'You can use it to restore if something ugly happens.'
        shutil.copy(self.filename,backup_file_name) # Make a backup...
        import gourmet.gtk_extras.dialog_extras as de
        import gtk
        de.show_message(
            title=_("Upgrading database"),
            label=_("Upgrading database"),            
            sublabel=_("Depending on the size of your database, this may be an intensive process and may take  some time. Your data has been automatically backed up in case something goes wrong."),
            expander=(_("Details"),_("A backup has been made in %s in case something goes wrong. If this upgrade fails, you can manually rename your backup file recipes.db to recover it for use with older Gourmet.")%backup_file_name),
            message_type=gtk.MESSAGE_INFO)

    def update_version_info (self, version_string):
        """Report our version to the database.

        If necessary, we'll do some version-dependent updates to the GUI
        """
        version = [int(s) for s in version_string.split('-')[0].split('.')]
        current_info=VersionInfo(*version)
        session = Session()
        try:
            stored_info = session.query(VersionInfo).one()
        except sqlalchemy.orm.exc.NoResultFound:
            if not self.new_db:
                # Default info -- the last version before we added the
                # version tracker...
                session.add(VersionInfo(0, 11, 0))
            else:
                session.add(current_info)

            session.commit()
            stored_info = session.query(VersionInfo).one()
        else:
            if not stored_info.version_major:
                stored_info = session.merge(VersionInfo(0, 11, 0,
                                                         rowid=stored_info.rowid))

        ### Code for updates between versions...
        import pkgutil
        import importlib
        import gourmet.migration.versions
        package = gourmet.migration.versions
        if not new_db and not stored_info == current_info:
            backup = False
            for _, modname, _ in pkgutil.iter_modules(package.__path__):
                target_version = VersionInfo(*[int(s) for s in modname[1:].split('_')],
                                             rowid=stored_info.rowid)
                if stored_info < target_version:
                    if not backup:
                        self.backup_db()
                        backup = True
                    print 'Updating database from %s to %s version layout' % \
                          (stored_info, target_version)
                    upgrade_module = importlib.import_module('gourmet.migration.versions.' + modname)
                    upgrade_module.upgrade(self)
                    stored_info = session.merge(target_version)
                    session.commit()

            for plugin in self.plugins:
                self.update_plugin_version(plugin, current_info)

            current_info.rowid = stored_info.rowid
            stored_info = session.merge(current_info)
            session.commit()

        ### End of code for updates between versions...

    def update_plugin_version (self, plugin, current_version=None):
        session = Session()
        if not current_version:
            current_version = session.query(VersionInfo).one()

        current = PluginInfo(plugin.name, *current_version,
                             plugin_version=plugin.version)
        stored = session.query(PluginInfo).\
                    filter_by(plugin==plugin.name).first()

        if not stored:
            # Default to the version before our plugin system existed
            stored = PluginInfo(plugin.name, None, 0, 13, 9, 0)
        try:
            plugin.update_version(stored, current)
        except:
            print 'Problem updating plugin',plugin,plugin.name
            raise
        # Now we store the information so we know we've done an update
        if stored:
            current.id = stored.id
            stored = session.merge(current)
        else:
            session.add(current)

        session.commit()

    def run_hooks (self, hooks, *args):
        """A basic hook-running function. We use hooks to allow parts of the application
        to tag onto data-modifying events and e.g. update the display"""
        for h in hooks:
            t = TimeAction('running hook %s with args %s'%(h,args),3)
            h(*args)
            t.end()

    # basic DB access functions
    def fetch_all (self, table, sort_by=[], **criteria):
        return self.db.execute(table.select(*make_simple_select_arg(criteria,table),
                            **{'order_by':make_order_by(sort_by,table)}
                            )).fetchall()

    def fetch_one (self, table, **criteria):
        """Fetch one item from table and arguments"""
        return self.db.execute(table.select(*make_simple_select_arg(criteria,table))).fetchone()

    def fetch_count (self, table, column, sort_by=[],**criteria):
        """Return a counted view of the table, with the count stored in the property 'count'"""
        result =  sqlalchemy.select(
            [sqlalchemy.func.count(getattr(table.c,column)).label('count'),
             getattr(table.c,column)],
            *make_simple_select_arg(criteria,table),
            **{'group_by':column,
               'order_by':make_order_by(sort_by,table,count_by=column),
               }
            ).execute().fetchall()
        return result

    def fetch_len (self, table, **criteria):
        """Return the number of rows in table that match criteria
        """
        if criteria:
            return self.db.execute(table.count(*make_simple_select_arg(criteria,table))).fetchone()[0]
        else:
            return self.db.execute(table.count()).fetchone()[0]

    def fetch_join (self, table1, table2, col1, col2,
                    column_names=None, sort_by=[], **criteria):
        if column_names:
            raise Exception("column_names KWARG NO LONGER SUPPORTED BY fetch_join!")
        return  table1.join(table2,getattr(table1.c,col1)==getattr(table2.c,col2)).select(
            *make_simple_select_arg(criteria,table1,table2)
            ).execute().fetchall()

    def fetch_food_groups_for_search (self, words):
        """Return food groups that match a given set of words."""
        where_statement = or_(
            *[self.nutrition_table.c.desc.like('%%%s%%'%w.lower())
              for w in words]
            )
        return [r[0] for r in sqlalchemy.select(
            [self.nutrition_table.c.foodgroup],
            where_statement,
            distinct=True).execute().fetchall()]

    def search_nutrition (self, words, group=None):
        """Search nutritional information for ingredient keys."""
        where_statement = and_(
            *[self.nutrition_table.c.desc.like('%%%s%%'%w)
              for w in words])
        if group:
            where_statement = and_(self.nutrition_table.c.foodgroup==group,
                                   where_statement)
        return self.nutrition_table.select(where_statement).execute().fetchall()

    def __get_joins (self, searches):
        joins = []
        for s in searches:
            if type(s)==tuple:
                joins.append(self.__get_joins(s[0]))
            else:
                if s['column'] == 'category':
                    if self.categories_table not in joins:
                        joins.append(self.categories_table,self.categories_table.c.id,
                                     self.recipe_table.c.id)
                elif s['column'] == 'ingredient':
                    if self.ingredients_table not in joins:
                        joins.append(self.ingredients_table)
        return joins

    def get_criteria (self,crit):
        if type(crit)==tuple:
            criteria,logic = crit
            if logic=='and':
                return and_(*[self.get_criteria(c) for c in criteria])
            elif logic=='or':
                return or_(*[self.get_criteria(c) for c in criteria])
        elif type(crit)!=dict: raise TypeError
        else:
            #join_crit = None # if we need to add an extra arg for a join
            if crit['column']=='category':
                subtable = self.categories_table
                col = subtable.c.category
            elif crit['column'] in ['ingkey','item']:
                subtable = self.ingredients_table
                col = getattr(subtable.c,crit['column'])
            elif crit['column']=='ingredient':
                d1 = crit.copy(); d1.update({'column':'ingkey'})
                d2 = crit.copy(); d2.update({'column':'item'}),
                return self.get_criteria(([d1,d2],
                                          'or'))
            elif crit['column']=='anywhere':
                searches = []
                for column in ['ingkey','item','category','cuisine','title','instructions','modifications',
                               'source','link']:
                    d = crit.copy(); d.update({'column':column})
                    searches.append(d)
                return self.get_criteria((searches,'or'))
            else:
                subtable = None
                col = getattr(self.recipe_table.c,crit['column'])
            # Make sure we're using unicode!
            if (type(crit.get('search',u'')) != unicode
                and type(crit.get('search',u'')) in types.StringTypes):
                crit['search'] = unicode(crit['search'])
            if crit.get('operator','LIKE')=='LIKE':
                retval = (col.like(crit['search']))
            elif crit['operator']=='REGEXP':
                retval = (col.op('REGEXP')(crit['search']))
            else:
                retval = (col==crit['search'])
            if subtable is not None:
                retval = self.recipe_table.c.id.in_(
                    sqlalchemy.select([subtable.c.recipe_id],retval)
                    )
            
            return retval

    def search_recipes (self, searches, sort_by=[]):
        """Search recipes for columns of values.

        "category" and "ingredient" are handled magically

        sort_by is a list of tuples (column,1) [ASCENDING] or (column,-1) [DESCENDING]
        """
        if 'rating' in [t[0] for t in sort_by]:
            i = [t[0] for t in sort_by].index('rating')
            d = (sort_by[i][1]==1 and -1 or 1)
            sort_by[i] = ('rating',d)
        criteria = self.get_criteria((searches,'and'))
        debug('backends.db.search_recipes - search criteria are %s'%searches,2)
        if 'category' in [s[0] for s in sort_by]:
            return self.db.execute(sqlalchemy.select([c for c in self.recipe_table.c],# + [self.categories_table.c.category],
                                     criteria,distinct=True,
                                     from_obj=[sqlalchemy.outerjoin(self.recipe_table,self.categories_table)],
                                     order_by=make_order_by(sort_by,self.recipe_table,
                                                            join_tables=[self.categories_table])
                                     )).fetchall()
        else:
            return self.db.execute(sqlalchemy.select([self.recipe_table],criteria,distinct=True,
                                     order_by=make_order_by(sort_by,self.recipe_table,),
                                     )).fetchall()

    def get_unique_values (self, colname,table=None,**criteria):
        """Get list of unique values for column in table."""
        if table is None: table=self.recipe_table
        if criteria: criteria = make_simple_select_arg(criteria,table)[0]
        else: criteria=None
        if colname=='category' and table==self.recipe_table:
            print 'WARNING: you are using a hack to access category values.'
            table = self.categories_table
            table = table.alias('ingrtable')
        retval = [r[0] for
                  r in self.db.execute(sqlalchemy.select([getattr(table.c,colname)],distinct=True,whereclause=criteria)).fetchall()
                  ]
        return filter(lambda x: x is not None, retval) # Don't return null values

    def get_ingkeys_with_count (self, search={}):
        """Get unique list of ingredient keys and counts for number of times they appear in the database.
        """
        if search:
            col = getattr(self.ingredients_table.c,search['column'])
            operator = search.get('operator','LIKE')
            if operator=='LIKE':
                criteria = col.like(search['search'])
            elif operator=='REGEXP':
                criteria = col.op('REGEXP')(search['search'])
            else:
                criteria = col==crit['search']
            result =  sqlalchemy.select(
                [sqlalchemy.func.count(self.ingredients_table.c.ingkey).label('count'),
                 self.ingredients_table.c.ingkey],
                criteria,
                **{'group_by':'ingkey',
                   'order_by':make_order_by([],self.ingredients_table,count_by='ingkey'),
                   }
                ).execute().fetchall()                
        else:
            result =  sqlalchemy.select(
                [sqlalchemy.func.count(self.ingredients_table.c.ingkey).label('count'),
                 self.ingredients_table.c.ingkey],
                **{'group_by':'ingkey',
                   'order_by':make_order_by([],self.ingredients_table,count_by='ingkey'),
                   }
                ).execute().fetchall()

        return result

    def delete_by_criteria (self, table, criteria):
        """Table is our table.
        Criteria is a dictionary of criteria to delete by.
        """
        criteria = fix_colnames(criteria,table)
        delete_args = []
        for k,v in criteria.items():
            delete_args.append(k==v)
        if len(delete_args) > 1:
            delete_args = [and_(*delete_args)]
        self.db.execute(table.delete(*delete_args))

    def update_by_criteria (self, table, update_criteria, new_values_dic):
        try:
            to_del = []
            for k in new_values_dic:
                if type(k) != str:
                    to_del.append(k)
            for k in to_del:
                v = new_values_dic[k]
                del new_values_dic[k]
                new_values_dic[str(k)] = v
            table.update(*make_simple_select_arg(update_criteria,table)).execute(**new_values_dic)
        except:
            print 'update_by_criteria error...'
            print 'table:',table
            print 'UPDATE_CRITERIA:'
            for k,v in update_criteria.items(): print '','KEY:',k,'VAL:',v
            print 'NEW_VALUES_DIC:'
            for k,v in new_values_dic.items(): print '','KEY:',k,type(k),'VAL:',v
            raise

    def add_column_to_table (self, table, column_spec):
        """table is a table, column_spec is a tuple defining the
        column, following the format for new tables.
        """
        name = table.name; new_col = column_spec[0]; coltyp = column_spec[1]
        coltyp = coltyp.compile(dialect=self.db.dialect)
        sql = 'ALTER TABLE %(name)s ADD %(new_col)s %(coltyp)s;'%locals()
        try:
            self.db.execute(sql)
        except:
            print 'FAILED TO EXECUTE',sql
            print 'Ignoring error in add_column_to_table'
            import traceback; traceback.print_exc()

    def alter_table (self, table_name, setup_function, cols_to_change={}, cols_to_keep=[]):
        """Change table, moving some columns.

        table is the table object. table_name is the table
        name. setup_function is a function that will setup our correct
        table. cols_to_change is a dictionary of columns that are changing
        names (key=orig, val=new). cols_to_keep is a list of columns
        that should be copied over as is.

        This works by renaming our table to a temporary name, then
        recreating our initial table. Finally, we copy over table
        data and then delete our temporary table (i.e. our old table)

        This is much less efficient than an alter table command, but
        will allow us to e.g. change/add primary key columns to sqlite
        tables
        """
        print 'Attempting to alter ',table_name,setup_function,cols_to_change,cols_to_keep
        try:
            self.db.execute('ALTER TABLE %(t)s RENAME TO %(t)s_temp'%{'t':table_name})
        except:
            do_raise = True
            import traceback; traceback.print_exc()
            try:
                self.db.execute('DROP TABLE %(t)s_temp'%{'t':table_name})
            except:
                1
            else:
                do_raise = False
                self.db.execute('ALTER TABLE %(t)s RENAME TO %(t)s_temp'%{'t':table_name})
            if do_raise:
                raise 
        # SQLAlchemy >= 0.7 doesn't allow: del self.metadata.tables[table_name]
        Base.metadata._remove_table(table_name, Base.metadata.schema)
        setup_function()
        getattr(self,'%s_table'%table_name).create()
        TO_COLS = cols_to_keep[:]
        FROM_COLS = cols_to_keep[:]
        for fro,to_ in cols_to_change.items():
            FROM_COLS.append(fro)
            TO_COLS.append(to_)
        stmt = '''INSERT INTO %(t)s (%(to_cols)s)
        SELECT %(from_cols)s FROM %(t)s_temp
        '''%{'t':table_name,
             'from_cols':', '.join(FROM_COLS),
             'to_cols':', '.join(TO_COLS),
             }
        self.db.execute(stmt)        
        self.db.execute('DROP TABLE %s_temp'%table_name)

    def row_equal (self, r1, r2):
        """Test whether two row references are the same.

        Return True if r1 and r2 reference the same row in the database.
        """
        return r1==r2

    def find_duplicates (self, by='recipe',recipes=None, include_deleted=True):
        """Find all duplicate recipes by recipe or ingredient.

        Returns a nested list of IDs, where each nested list is a list
        of duplicates.

        This uses the recipe_hash and ingredient_hash respectively.
        To find only those recipes that have both duplicate recipe and
        ingredient hashes, use find_all_duplicates
        """
        if by=='recipe':
            col = self.recipe_table.c.recipe_hash
        elif by=='ingredient':
            col = self.recipe_table.c.ingredient_hash
        args = []
        if not include_deleted: args.append(self.recipe_table.c.deleted==False)
        kwargs = dict(having=sqlalchemy.func.count(col)>1,
                      group_by=col)
        duped_hashes = sqlalchemy.select([col],
                                         *args,
                                         **kwargs)
        query = sqlalchemy.select([self.recipe_table.c.id,col],
                                  include_deleted and col.in_(duped_hashes) or and_(col.in_(duped_hashes),
                                                                                    self.recipe_table.c.deleted==False),
                                  order_by=col).execute()
        recs_by_hash = {}
        for result in query.fetchall():
            rec_id = result[0]; hsh = result[1]
            if not recs_by_hash.has_key(hsh):
                recs_by_hash[hsh] = []
            recs_by_hash[hsh].append(rec_id)
        results = recs_by_hash.values()
        if recipes:
            rec_ids = [r.id for r in recipes]
            results = filter(lambda reclist: True in [(rid in rec_ids) for rid in reclist], results)
        return results

    def find_complete_duplicates (self, recipes=None, include_deleted=True):
        """Find all duplicate recipes (by recipe_hash and ingredient_hash)."""
        args = []
        if not include_deleted: args.append(self.recipe_table.c.deleted==False)
        
        ing_hashes,rec_hashes = [sqlalchemy.select([col],
                                                   *args,
                                                   **dict(having=sqlalchemy.func.count(col)>1,
                                                   group_by=col)
                                                   ) for col in [self.recipe_table.c.ingredient_hash,
                                                                 self.recipe_table.c.recipe_hash]
                             ]
        if not include_deleted: select_statements = [self.recipe_table.c.deleted==False]
        else: select_statements = []
        select_statements.append(self.recipe_table.c.ingredient_hash.in_(ing_hashes))
        select_statements.append(self.recipe_table.c.recipe_hash.in_(rec_hashes))

        query = sqlalchemy.select([self.recipe_table.c.id,
                                   self.recipe_table.c.recipe_hash,
                                   self.recipe_table.c.ingredient_hash],
                                  and_(*select_statements),
                                  order_by=[self.recipe_table.c.recipe_hash,
                                            self.recipe_table.c.ingredient_hash]).execute()
        recs_by_hash = {}
        for result in query.fetchall():
            rec_id = result[0]; rhsh = result[1]; ihsh = result[2]
            if not recs_by_hash.has_key((rhsh,ihsh)):
                recs_by_hash[(rhsh,ihsh)] = []
            recs_by_hash[(rhsh,ihsh)].append(rec_id)
        results = recs_by_hash.values()
        if recipes:
            rec_ids = [r.id for r in recipes]
            results = filter(lambda reclist: True in [(rid in rec_ids) for rid in reclist], results)
        return results
    
    # convenience DB access functions for working with ingredients,
    # recipes, etc.

    def modify_rec (self, rec, dic):
        """Modify recipe based on attributes/values in dictionary.

        Return modified recipe.
        """
        self.validate_recdic(dic)        
        debug('validating dictionary',3)
        if dic.has_key('category'):
            newcats = dic['category'].split(', ')
            newcats = filter(lambda x: x, newcats) # Make sure our categories are not blank
            curcats = self.get_cats(rec)
            for c in curcats:
                if c not in newcats:
                    self.delete_by_criteria(self.categories_table,{'recipe_id':rec.id,'category':c})
            for c in newcats:
                if c not in curcats:
                    self.do_add_cat({'recipe_id':rec.id,'category':c})
            del dic['category']
        debug('do modify rec',3)
        retval = self.do_modify_rec(rec,dic)
        self.update_hashes(rec)
        return retval
    
    def validate_recdic (self, recdic):
        if not recdic.has_key('last_modified'):
            recdic['last_modified']=time.time()
        if recdic.has_key('image') and not recdic.has_key('thumb'):
            # if we have an image but no thumbnail, we want to create the thumbnail.
            try:
                img = ImageExtras.get_image_from_string(recdic['image'])
                thumb = ImageExtras.resize_image(img,40,40)
                ofi = StringIO.StringIO()
                thumb.save(ofi,'JPEG')
                recdic['thumb']=ofi.getvalue()
                ofi.close()
            except:
                del recdic['image']
                print """Warning: gourmet couldn't recognize the image.

                Proceding anyway, but here's the traceback should you
                wish to investigate.
                """
                import traceback
                traceback.print_stack()
        for k,v in recdic.items():
            try:
                recdic[k]=unicode(v.strip())
            except:
                pass

    def modify_ings (self, ings, ingdict):
        # allow for the possibility of doing a smarter job changing
        # something for a whole bunch of ingredients...
        for i in ings: self.modify_ing(i,ingdict)

    def modify_ing_and_update_keydic (self, ing, ingdict):
        """Update our key dictionary and modify our dictionary.

        This is a separate method from modify_ing because we only do
        this for hand-entered data, not for mass imports.
        """
        # If our ingredient has changed, update our keydic...
        if ing.item!=ingdict.get('item',ing.item) or ing.ingkey!=ingdict.get('ingkey',ing.ingkey):
            if ing.item and ing.ingkey:
                self.remove_ing_from_keydic(ing.item,ing.ingkey)
                self.add_ing_to_keydic(
                    ingdict.get('item',ing.item),
                    ingdict.get('ingkey',ing.ingkey)
                    )
        return self.modify_ing(ing,ingdict)
        
    def update_hashes (self, rec):
        rhash,ihash = recipeIdentifier.hash_recipe(rec,self)
        self.do_modify_rec(rec,{'recipe_hash':rhash,'ingredient_hash':ihash})

    def find_duplicates_of_rec (self, rec, match_ingredient=True, match_recipe=True):
        """Return recipes that appear to be duplicates"""
        if match_ingredient and match_recipe:
            perfect_matches = self.fetch_all(ingredient_hash=rec.ingredient_hash,recipe_hash=rec.recipe_hash)
        elif match_ingredient:
            perfect_matches = self.fetch_all(ingredient_hash=rec.ingredient_hash)
        else:
            perfect_matches = self.fetch_all(recipe_hash=rec.recipe_hash)
        matches = []
        if len(perfect_matches) == 1:
            return []
        else:
            for r in perfect_matches:
                if r.id != rec.id:
                    matches.append(r)
            return matches

    def find_all_duplicates (self):
        """Return a list of sets of duplicate recipes."""
        raise NotImplementedError

    def merge_mergeable_duplicates (self):
        """Merge all duplicates for which a simple merge is possible.
        For those recipes which can't be merged, return:
        [recipe-id-list,to-merge-dic,diff-dic]
        """
        dups = self.find_all_duplicates()
        unmerged = []
        for recs in dups:
            rec_objs = [self.fetch_one(self.recipe_table,id=r) for r in recs]
            merge_dic,diffs = recipeIdentifier.merge_recipes(self,rec_objs)
            if not diffs:
                if merge_dic:
                    self.modify_rec(rec_objs[0],merge_dic)
                for r in rec_objs[1:]: self.delete_rec(r)
            else:
                unmerged.append([recs,merge_dic,diffs])
        return unmerged
    
    def modify_ing (self, ing, ingdict):
        self.validate_ingdic(ingdict)
        return self.do_modify_ing(ing,ingdict)

    def add_rec (self, dic, accept_ids=False):
        """Dictionary is a dictionary of column values for our recipe.
        Return the ID of the newly created recipe.

        If accept_ids is True, we accept recipes with IDs already
        set. These IDs need to have been reserved with the new_id()
        method.
        """
        cats = []
        if dic.has_key('category'):
            cats = dic['category'].split(', ')
            del dic['category']
        if dic.has_key('servings'):
            if dic.has_key('yields'):
                del dic['yields']
            else:
                try:
                    dic['servings'] = float(dic['servings'])
                    dic['yields'] = dic['servings']
                    dic['yield_unit'] = 'servings'
                    del dic['servings']
                except:
                    del dic['servings']
        if not dic.has_key('deleted'): dic['deleted']=False
        self.validate_recdic(dic)
        try:
            ret = self.do_add_rec(dic)
        except:
            print 'Problem adding recipe with dictionary...'
            for k,v in dic.items(): print 'KEY:',k,'of type',type(k),'VALUE:',v,'of type',type(v)
            raise
        else:
            if type(ret)==int:
                ID = ret
                ret = self.get_rec(ID) 
            else:
                ID = ret.id
            for c in cats:
                if c: self.do_add_cat({'recipe_id':ID,'category':c})
            self.update_hashes(ret)
            return ret

    def add_ing_and_update_keydic (self, dic):
        if dic.has_key('item') and dic.has_key('ingkey') and dic['item'] and dic['ingkey']:
            self.add_ing_to_keydic(dic['item'],dic['ingkey'])
        return self.add_ing(dic)
    
    def add_ing (self, dic):
        self.validate_ingdic(dic)
        try:          
            return self.do_add_ing(dic)
        except:
            print 'Problem adding',dic
            raise

    def add_ings (self, dics):
        """Add multiple ingredient dictionaries at a time."""
        for d in dics:
            self.validate_ingdic(d)
            for k in ['refid','unit','amount','rangeamount','item','ingkey','optional','shopoptional','inggroup','position']:
                if not k in d:
                    d[k] = None
        try:
            # Warning: this method relies on all the dictionaries
            # looking identical. validate_ingdic should be taking care
            # of this for us now, but if parameters change in the
            # future, this rather subtle bug could well rear its ugly
            # head again.
            rp = self.ingredients_table.insert().execute(*dics)
        except ValueError:
            for d in dics: self.coerce_types(self.ingredients_table,d)
            self.ingredients_table.insert().execute(*dics)

    # Lower level DB access functions -- hopefully subclasses can
    # stick to implementing these    

    def coerce_types (self, table, dic):
        """Modify dic to make sure types are correct for table.
        """
        type_to_pytype = {Float:float,
                          Integer:int,
                          String:str,
                          Boolean:bool,
                          Numeric:float,
                          }
        for k,v in dic.copy().items():
            column_obj = getattr(table.c,k)
            if column_obj.type.__class__ in type_to_pytype:
                try:
                    v = type_to_pytype[column_obj.type.__class__](v)
                except:
                    v = None
                if dic[k] != v:
                    dic[k] = v

    def commit_fast_adds (self):
        if hasattr(self,'extra_connection'):
            self.extra_connection.commit()

    def do_add_fast (self, table, dic):
        '''Add fast -- return None'''
        if not hasattr(self,'extra_connection'):
            self.extra_connection = self.db.connect().connection
        try:
            tname = table.name
            SQL = 'INSERT INTO ' + tname + '('+', '.join(dic.keys()) + ')'
            SQL += ' VALUES (' +  ", ".join(['?']*len(dic)) + ')'
            self.extra_connection.execute(SQL,dic.values())
        except:
            return self.do_add(table,dic)

    def do_add (self, table, dic):
        insert_statement = table.insert()
        self._force_unicode(dic)
        try:
            result_proxy = self.db.execute(insert_statement,**dic)
        except ValueError:
            print 'Had to coerce types',table,dic
            self.coerce_types(table,dic)
            result_proxy = self.db.execute(insert_statement,**dic)
        return result_proxy

    def do_add_and_return_item (self, table, dic, id_prop='id'):
        result_proxy = self.do_add(table,dic)
        select = table.select(getattr(table.c,id_prop)==result_proxy.inserted_primary_key[0])
        return self.db.execute(select).fetchone()

    def do_add_ing (self,dic):
        return self.do_add_and_return_item(self.ingredients_table,dic,id_prop='id')

    def do_add_cat (self, dic):
        return self.do_add_and_return_item(self.categories_table,dic)

    def do_add_rec (self, rdict):
        """Add a recipe based on a dictionary of properties and values."""
        self.changed=True
        if not rdict.has_key('deleted'):
            rdict['deleted']=0
        if rdict.has_key('id'):
            # If our dictionary has an id, then we assume we are a
            # reserved ID
            if rdict['id'] in self.new_ids:
                rid = rdict['id']; del rdict['id']
                self.new_ids.remove(rid)
                self.update_by_criteria(self.recipe_table,
                                        {'id':rid},
                                        rdict)
                return self.recipe_table.select(self.recipe_table.c.id==rid).execute().fetchone()
            else:
                raise ValueError('New recipe created with preset id %s, but ID is not in our list of new_ids'%rdict['id'])
        insert_statement = self.recipe_table.insert()
        select = self.recipe_table.select(self.recipe_table.c.id==self.db.execute(insert_statement,**rdict).inserted_primary_key[0])
        return self.db.execute(select).fetchone()

    def validate_ingdic (self,dic):
        """Do any necessary validation and modification of ingredient dictionaries."""
        if not dic.has_key('deleted'): dic['deleted']=False
        self._force_unicode(dic)

    def _force_unicode (self, dic):
       for k,v in dic.items():
            if type(v)==str and k not in ['image','thumb']:
                # force unicode...
                dic[k]=unicode(v) 
                
    def do_modify_rec (self, rec, dic):
        """This is what other DBs should subclass."""
        return self.do_modify(self.recipe_table,rec,dic)

    def do_modify_ing (self, ing, ingdict):
        """modify ing based on dictionary of properties and new values."""
        return self.do_modify(self.ingredients_table,ing,ingdict)

    def do_modify (self, table, row, d, id_col='id'):
        if id_col:
            try:
                self._force_unicode(d)
                qr = self.db.execute(table.update(getattr(table.c,id_col)==getattr(row,id_col)),**d)
            except:
                print 'do_modify failed with args'
                print 'table=',table,'row=',row
                print 'd=',d,'id_col=',id_col
                raise
            select = table.select(getattr(table.c,id_col)==getattr(row,id_col))
        else:
            qr = self.db.execute(table.update(),**d)
            select = table.select()
        return self.db.execute(select).fetchone()

    def get_ings (self, rec):
        """Handed rec, return a list of ingredients.

        rec should be an ID or an object with an attribute ID)"""
        if hasattr(rec,'id'):
            id=rec.id
        else:
            id=rec
        session = Session()
        return session.query(Ingredient).filter_by(recipe_id=id,
                                                   deleted=False).all()


    def get_cats (self, rec):
        #svw = rec.categories
        session = Session()
        svw = session.query(Category).filter_by(recipe_id=rec.id).all()
        cats =  [c.category or '' for c in svw]
        # hackery...
        while '' in cats:
            cats.remove('')
        return cats

    def get_referenced_rec (self, ing):
        """Get recipe referenced by ingredient object."""
        if hasattr(ing,'refid') and ing.refid:
            rec = self.get_rec(ing.refid)
            if rec: return rec
        # otherwise, our reference is no use! Something's been
        # foobared. Unfortunately, this does happen, so rather than
        # screwing our user, let's try to look based on title/item
        # name (the name of the ingredient *should* be the title of
        # the recipe, though the user could change this)
        if hasattr(ing,'item'):
            rec = self.fetch_one(self.recipe_table,**{'title':ing.item})
            if rec:
                self.modify_ing(ing,{'refid':rec.id})
                return rec
            else:
                print 'Very odd: no match for',ing,'refid:',ing.refid

    def include_linked_recipes (self, recs):
        '''Handed a list of recipes, append any recipes that are
        linked as ingredients in those recipes to the list.

        Modifies the list in place.
        '''
        for r in recs:
            for i in r.ingredients:
                if i.recipe_ref and i.recipe_ref not in recs:
                    recs.append(i.recipe_ref)
                    #FIXME: see self.get_referenced_rec(i)
                
    def get_rec (self, id, recipe_table=None):
        """Handed an ID, return a recipe object."""
        if recipe_table:
            print 'handing get_rec an recipe_table is deprecated'
            print 'Ignoring recipe_table handed to get_rec'
        recipe_table=self.recipe_table
        return self.fetch_one(self.recipe_table, id=id)

    def delete_rec (self, rec):
        """Delete recipe object rec from our database."""
        if type(rec)!=int: rec=rec.id
        debug('deleting recipe ID %s'%rec,0)
        self.delete_by_criteria(self.recipe_table,{'id':rec})
        self.delete_by_criteria(self.categories_table,{'recipe_id':rec})
        self.delete_by_criteria(self.ingredients_table,{'recipe_id':rec})
        debug('deleted recipe ID %s'%rec,0)

    def new_id (self):
        #raise NotImplementedError("WARNING: NEW_ID IS NO LONGER FUNCTIONAL, FIND A NEW WAY AROUND THE PROBLEM")
        #rec = self.new_rec()
        rec = self.do_add_rec({'deleted':1})
        self.new_ids.append(rec.id)
        return rec.id

    def replace_ings (self, ingdicts):
        """Add a new ingredients and remove old ingredient list."""
        ## we assume (hope!) all ingdicts are for the same ID
        id=ingdicts[0]['id']
        debug("Deleting ingredients for recipe with ID %s"%id,1)
        self.delete_by_criteria(self.ingredients_table,{'id':id})
        for ingd in ingdicts:
            self.add_ing(ingd)
    
    def ingview_to_lst (self, view):
        """Handed a view of ingredient data, we output a useful list.
        The data we hand out consists of a list of tuples. Each tuple contains
        amt, unit, key, alternative?"""
        ret = []
        for i in view:
            ret.append([self.get_amount(i), i.unit, i.ingkey,])
        return ret

    def get_amount_as_float (self, ing, mode=1): #1 == self.AMT_MODE_AVERAGE
        """Return a float representing our amount.

        If we have a range for amount, this function will ignore the range and simply
        return a number.  'mode' specifies how we deal with the mode:
        self.AMT_MODE_AVERAGE means we average the mode (our default behavior)
        self.AMT_MODE_LOW means we use the low number.
        self.AMT_MODE_HIGH means we take the high number.
        """
        amt = self.get_amount(ing)
        if type(amt) in [float, int, type(None)]:
            return amt
        else:
            # otherwise we do our magic
            amt=list(amt)
            amt.sort() # make sure these are in order
            low,high=amt
            if mode==self.AMT_MODE_AVERAGE: return (low+high)/2.0
            elif mode==self.AMT_MODE_LOW: return low
            elif mode==self.AMT_MODE_HIGH: return high # mode==self.AMT_MODE_HIGH
            else:
                raise ValueError("%s is an invalid value for mode"%mode)

    @pluggable_method
    def add_ing_to_keydic (self, item, key):
        session = Session()
        #print 'add ',item,key,'to keydic'
        # Make sure we have unicode...
        if type(item)==str: item = unicode(item)
        if type(key)==str: key = unicode(key)
        if not item or not key: return
        else:
            if item: item = unicode(item)
            if key: key = unicode(key)
        ing = session.query(KeyLookup).\
              filter(KeyLookup.item == item, KeyLookup.ingkey == key).first()
        if ing:
            ing.count += 1
        else:
            session.add(KeyLookup(item=item, ingkey=key, count=1))

        # The below code should move to a plugin for users who care about ingkeys...
        for w in item.split():
            w=str(w.decode('utf8').lower())
            ing = session.query(KeyLookup).\
                        filter(KeyLookup.word == unicode(w),
                               KeyLookup.ingkey == unicode(key)).first()
            if ing:
                ing.count += 1
            else:
                session.add(KeyLookup(word=unicode(w), ingkey=unicode(key), count=1))

        session.commit()

    def remove_ing_from_keydic (self, item, key):
        #print 'remove ',item,key,'to keydic'        
        row = self.fetch_one(self.keylookup_table,item=item,ingkey=key)
        if row:
            new_count = row.count - 1
            if new_count:
                self.do_modify(self.keylookup_table,row,{'count':new_count})
            else:
                self.delete_by_criteria(self.keylookup_table,{'item':item,'ingkey':key})
        for w in item.split():
            w=str(w.decode('utf8').lower())
            row = self.fetch_one(self.keylookup_table,item=item,ingkey=key)
            if row:
                new_count = row.count - 1
                if new_count:
                    self.do_modify(self.keylookup_table,row,{'count':new_count})
                else:
                    self.delete_by_criteria(self.keylookup_table,{'word':w,'ingkey':key})

    def ing_shopper (self, view):
        return DatabaseShopper(self.ingview_to_lst(view))

    # functions to undoably modify tables 

    def get_dict_for_obj (self, obj, keys):
        orig_dic = {}
        for k in keys:
            if k=='category':
                v = ", ".join(self.get_cats(obj))
            else:
                v=getattr(obj,k)
            orig_dic[k]=v
        return orig_dic

    def undoable_delete_recs (self, recs, history, make_visible=None, session=Session()):
        """Delete recipes by setting their 'deleted' flag to True and add to UNDO history."""
        def do_delete ():
            for rec in recs:
                debug('rec %s deleted=True'%rec.id,1)
                rec.deleted=True
            session.commit()
            if make_visible: make_visible(recs)
        def undo_delete ():
            for rec in recs:
                debug('rec %s deleted=False'%rec.id,1)
                rec.deleted=False
            session.commit()
            if make_visible: make_visible(recs)
        obj = Undo.UndoableObject(do_delete,undo_delete,history)
        obj.perform()

    def undoable_modify_ing (self, ing, dic, history, make_visible=None):
        """modify ingredient object ing based on a dictionary of properties and new values.

        history is our undo history to be handed to Undo.UndoableObject
        make_visible is a function that will make our change (or the undo or our change) visible.
        """
        orig_dic = self.get_dict_for_obj(ing,dic.keys())
        key = dic.get('ingkey',None)
        item = key and dic.get('item',ing.item)
        def do_action ():
            debug('undoable_modify_ing modifying %s'%dic,2)
            self.modify_ing(ing,dic)
            if key:
                self.add_ing_to_keydic(item,key)
            if make_visible: make_visible(ing,dic)
        def undo_action ():
            debug('undoable_modify_ing unmodifying %s'%orig_dic,2)
            self.modify_ing(ing,orig_dic)
            if key:
                self.remove_ing_from_keydic(item,key)
            if make_visible: make_visible(ing,orig_dic)
        obj = Undo.UndoableObject(do_action,undo_action,history)
        obj.perform()

    def get_default_values (self, colname):
        try:
            return defaults.fields[colname]
        except:
            return []

    
class RecipeManager (RecData):
    
    def __init__ (self,*args,**kwargs):
        debug('recipeManager.__init__()',3)
        RecData.__init__(self,*args,**kwargs)
        #self.km = keymanager.KeyManager(rm=self)
        self.km = keymanager.get_keymanager(rm=self)
        
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

    def parse_ingredient (self, s, conv=None, get_key=True):
        """Handed a string, we hand back a dictionary representing a parsed ingredient (sans recipe ID)"""
        #if conv:
        #    print 'parse_ingredient: conv argument is now ignored'
        debug('ingredient_parser handed: %s'%s,0)
        # Strip whitespace and bullets...
        d={}
        s = s.decode('utf8').strip(
            u'\u2022\u2023\u2043\u204C\u204D\u2219\u25C9\u25D8\u25E6\u2619\u2765\u2767\u29BE\u29BF\n\t #*+-')
        s = unicode(s)
        option_m = re.match('\s*optional:?\s*',s,re.IGNORECASE)
        if option_m:
            s = s[option_m.end():]
            d['optional']=True
        debug('ingredient_parser handed: "%s"'%s,1)
        m=convert.ING_MATCHER.match(s)
        if m:
            debug('ingredient parser successfully parsed %s'%s,1)
            a,u,i=(m.group(convert.ING_MATCHER_AMT_GROUP),
                   m.group(convert.ING_MATCHER_UNIT_GROUP),
                   m.group(convert.ING_MATCHER_ITEM_GROUP))
            if a:
                asplit = convert.RANGE_MATCHER.split(a)
                if len(asplit)==2:
                    d['amount']=convert.frac_to_float(asplit[0].strip())
                    d['rangeamount']=convert.frac_to_float(asplit[1].strip())
                else:
                    d['amount']=convert.frac_to_float(a.strip())
            if u:
                conv = convert.get_converter()
                if conv and conv.unit_dict.has_key(u.strip()):
                    # Don't convert units to our units!
                    d['unit']=u.strip()
                else:
                    # has this unit been used
                    prev_uses = self.fetch_all(self.ingredients_table,unit=u.strip())
                    if prev_uses:
                        d['unit']=u
                    else:
                        # otherwise, unit is not a unit
                        i = u + ' ' + i
            if i:
                optmatch = re.search('\s+\(?[Oo]ptional\)?',i)
                if optmatch:
                    d['optional']=True
                    i = i[0:optmatch.start()] + i[optmatch.end():]
                d['item']=i.strip()
                if get_key: d['ingkey']=self.km.get_key(i.strip())
            debug('ingredient_parser returning: %s'%d,0)
            return d
        else:
            debug("Unable to parse %s"%s,0)
            d['item'] = s
            return d
        
    ingredient_parser = parse_ingredient

    def ing_search (self, ing, keyed=None, recipe_table=None, use_regexp=True, exact=False):
        """Search for an ingredient."""
        if not recipe_table: recipe_table = self.recipe_table
        vw = self.joined_search(recipe_table,self.ingredients_table,'ingkey',ing,use_regexp=use_regexp,exact=exact)
        if not keyed:
            vw2 = self.joined_search(recipe_table,self.ingredients_table,'item',ing,use_regexp=use_regexp,exact=exact)
            if vw2 and vw:
                vw = vw.union(vw2)
            else: vw = vw2
        return vw

    def joined_search (self, table1, table2, search_by, search_str, use_regexp=True, exact=False, join_on='id'):
        raise NotImplementedError
    
    def ings_search (self, ings, keyed=None, recipe_table=None, use_regexp=True, exact=False):
        """Search for multiple ingredients."""
        raise NotImplementedError

    def clear_remembered_optional_ings (self, recipe=None):
        """Clear our memories of optional ingredient defaults.

        If handed a recipe, we clear only for the recipe we've been
        given.

        Otherwise, we clear *all* recipes.
        """
        if recipe:
            vw = self.get_ings(recipe)
        else:
            vw = self.ingredients_table
        # this is ugly...
        vw1 = vw.select(shopoptional=1)
        vw2 = vw.select(shopoptional=2)
        for v in vw1,vw2:
            for i in v: self.modify_ing(i,{'shopoptional':0})

class DatabaseConverter(convert.Converter):
    def __init__ (self, db):
        self.db = db
        convert.converter.__init__(self)
    ## FIXME: still need to finish this class and then
    ## replace calls to convert.converter with
    ## calls to DatabaseConverter

    def create_conv_table (self):
        self.conv_table = dbDic('ckey','value',self.db.convtable_table, self.db)
        for k,v in defaults.CONVERTER_TABLE.items():
            if not self.conv_table.has_key(k):
                self.conv_table[k]=v

    def create_density_table (self):
        self.density_table = dbDic('dkey','value',
                                   self.db.density_table,self.db)
        for k,v in defaults.DENSITY_TABLE.items():
            if not self.density_table.has_key(k):
                self.density_table[k]=v

    def create_cross_unit_table (self):
        self.cross_unit_table=dbDic('cukey','value',self.db.crossunitdict_table,self.db)
        for k,v in defaults.CROSS_UNIT_TABLE:
            if not self.cross_unit_table.has_key(k):
                self.cross_unit_table[k]=v

    def create_unit_dict (self):
        self.units = defaults.UNITS
        self.unit_dict=dbDic('ukey','value',self.db.unitdict_table,self.db)
        for itm in self.units:
            key = itm[0]
            variations = itm[1]
            self.unit_dict[key] = key
            for v in variations:
                self.unit_dict[v] = key
                
class dbDic:
    def __init__ (self, keyprop, valprop, view, db):
        """Create a dictionary interface to a database table."""
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
        store_v = v
        row = self.db.fetch_one(self.vw,**{self.kp:k})
        if row:
            self.db.do_modify(self.vw, row, {self.vp:store_v},id_col=self.kp)
        else:
            self.db.do_add(self.vw,{self.kp:k,self.vp:store_v})
        self.db.changed=True
        return v

    def __getitem__ (self, k):
        if self.just_got.has_key(k): return self.just_got[k]
        v = getattr(self.db.fetch_one(self.vw,**{self.kp:k}),self.vp)
        return v
    
    def __repr__ (self):
        retstr = "<dbDic> {"
        #for i in self.vw:
        #    retstr += getattr(i,self.kp)
        #    retstr += ":"
        #    retstr += "%s"%getattr(i,self.vp)
        #    retstr += ", "
        retstr += "}"
        return retstr

    def initialize (self, d):
        '''Initialize values based on dictionary d

        We assume the DB is known to be empty.

        '''
        dics = []
        for k in d:
            store_v = d[k]
            if type(store_v) in types.StringTypes:
                store_v = unicode(store_v)
            if type(k) in types.StringTypes:
                k = unicode(k)
            dics.append({self.kp:k,self.vp:store_v})
        self.vw.insert().execute(*dics)

    def keys (self):
        ret = []
        for i in self.db.fetch_all(self.vw):
            ret.append(getattr(i,self.kp))
        return ret

    def values (self):
        ret = []
        for i in self.db.fetch_all(self.vw):
            val = getattr(i,self.vp)
            ret.append(val)
        return ret

    def items (self):
        ret = []
        for i in self.db.fetch_all(self.vw):
            try:
                key = getattr(i,self.kp)
                val = getattr(i,self.vp)
            except:
                print 'TRYING TO GET',self.kp,self.vp,'from',self.vw
                print 'ERROR!!!'
                import traceback; traceback.print_exc()
                print 'IGNORING'
                continue
            ret.append((key,val))
        return ret

# To change
# fetch_one -> use whatever syntax sqlalchemy uses throughout
# fetch_all ->
#recipe_table -> recipe_table
# To eliminate

def test_db ():
    import tempfile
    db = RecData(file=tempfile.mktemp())
    print 'BEGIN TESTING'
    from db_tests import test_db
    test_db(db)
    print 'END TESTING'

def add_sample_recs ():
    for rec,ings in [[dict(title='Spaghetti',cuisine='Italian',category='Easy, Entree'),
                      [dict(amount=1,unit='jar',item='Marinara Sauce',ingkey='sauce, marinara'),
                       dict(amount=0.25,unit='c.',item='Parmesan Cheese',ingkey='cheese, parmesan'),
                       dict(amount=.5,unit='lb.',item='Spaghetti',ingkey='spaghetti, dried')]],
                     [dict(title='Spaghetti w/ Meatballs',cuisine='Italian',category='Easy, Entree'),
                      [dict(amount=1,unit='jar',item='Marinara Sauce',ingkey='sauce, marinara'),
                       dict(amount=0.25,unit='c.',item='Parmesan Cheese',ingkey='cheese, parmesan'),
                       dict(amount=.5,unit='lb.',item='Spaghetti',ingkey='spaghetti, dried'),
                       dict(amount=0.5,unit='lb.',item='Meatballs',ingkey='Meatballs, prepared'),
                       ]],
                     [dict(title='Toasted cheese',cuisine='American',category='Sandwich, Easy',
                           servings=2),
                      [dict(amount=2,unit='slices',item='bread'),
                       dict(amount=2,unit='slices',item='cheddar cheese'),
                       dict(amount=2,unit='slices',item='tomato')]]
                     ]:
        r = db.add_rec(rec)
        for i in ings:
            i['recipe_id']=r.id
            db.add_ing(i)

def get_database (*args,**kwargs):
    try:
        return RecData(*args,**kwargs)
    except RecData, rd:
        return rd

if __name__ == '__main__':
    db = RecData()
