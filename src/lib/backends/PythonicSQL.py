import threading
import __builtin__
from types import DictionaryType
from gourmet.gdebug import debug,TimeAction

threading_debug_level = 1
lock_change_debug_level = 1
sql_debug_level = 0

def needs_buffer (itm):
    try:
        unicode(itm)
        return False
    except:
        return True

class PythonicSQL:

    """PythonicSQL allows us to treat SQL queries in a more object-oriented/pythonic
    fashion. Really, this class allows SQL to look more like metakit and should be able
    to drop in easily into the codebase I have built around the metakit interfaces, preventing
    me from having to write SQL throughout an app. Subclasses will implement specific SQL dialects,
    such as a MySQL interface or a SQLite interface."""

    def __init__ (self,module=None):
        self.changed = False
        self._table_fields = {}        
        self._connection = {}
        self._cursors = {}
        self._module = module
        debug('PythonicSQL Initializing: module=%s'%self._module,1)
        self._threadsafety = self._module.threadsafety
        self._connection[threading.currentThread()] = self.connect()
        self._cursors[threading.currentThread()] = self.get_connection().cursor()

    def get_connection (self):
        """Return our connection object for the current thread. We open
        a new connection for each thread that uses us."""
        if self._threadsafety >= 2:
            # we can share a connection across threads.
            # we'll only have one connection in our dictionary!
            if self._connection: return self._connection.values()[0]
            else: self._connection = {1:self.connect()}
        thread = threading.currentThread()
        if not self._connection.has_key(thread):
            if self._threadsafety == 0:
                # we can't handle threading; panic!
                raise "%s cannot handle multiple threads!"%self._module
            if self._threadsafety == 1:
                # we need a new connection for our thread!
                print 'Opening new connection for thread %s'%thread
                self._connection[thread]=self.connect()
        return self._connection[thread]
    
    def get_cursor (self):
        """Return our persistent cursor for the current thread."""
        if self._threadsafety == 3:
            # we can share cursors across threads.
            # we'll only have one cursor in our dictionary
            if self._cursors: return self._cursors.values()[0]
            else: self._cursors = {1:self.get_connection().cursor()}
        thread=threading.currentThread()
        if not self._cursors.has_key(thread):
            self._cursors[thread]=self.get_connection().cursor()
        return self._cursors[thread]
    
    def connect (self):
        """Connect to our database

        Subclasses have to implement this."""
        raise NotImplementedError 
        
    def new_cursor (self):
        return self.get_connection().cursor()

    def __cleanup_params (self, lst):
        if type(lst) == str: return lst
        retlst = []
        for i in lst:
            if type(i) == bool: retlst.append(int(i))
            elif i==None: retlst.append('NULL')
            elif hasattr(i,'replace') and needs_buffer(i):
                retlst.append(buffer(i))
            else: retlst.append(i)
        return retlst

    def _execute (self, c, sql):
        """Just do the execution and wrap it with a nice error message if it fails."""
        if type(sql)==type(""): sql = [sql]
        debug('executing SQL : %s'%sql,1)
        if len(sql) > 1:
            # if we have arguments, we have to get rid of booleans
            # which seem to be throwing errors
            sql[1] = self.__cleanup_params(sql[1])
        try:            
            c.execute(*sql)
        except:
            print "There was an error executing the following SQL:"
            print sql
            raise
        
    def execute (self, sql):
        #debug('execute: %s'%sql,sql_debug_level)
        # handle strings or tuples of strings,params        
        c = self.get_cursor()
        self._execute(c,sql)
        retval = c.fetchall()
        return retval

    def execute_and_fetch (self, sql, *fetcher_args,**fetcher_kwargs):
        """Execute our SQL and return a Fetcher object to let us access the query."""
        debug('excute_and_fetch: %s'%sql,sql_debug_level)
        # handle strings or tuples of strings,params
        c = self.new_cursor()
        self._execute(c,sql)
        return Fetcher(c,*fetcher_args,**fetcher_kwargs)

    def create (self, name, table, key=None, flags=[]): # USE FLAGS!!!
        """Use this method to create a table in this database object. Expected
        arguments are a table name and a list [(name, type, [flags])] } with the column names
        as strings and type being type objects representing the data type
        used in that column."""
        #if type(table) != DictionaryType:
        #    raise TypeError, 'expected dictionary type argument'
        add_string = "CREATE TABLE %s ("%name
        sql_params = []
        for rowname,typ,flags in table:
            if type(typ) != type(""):
                typ = self.pytype_to_sqltype(typ)
            typ = self.hone_type(typ)
            add_string +=  "%s %s"%(rowname,typ)
            if 'AUTOINCREMENT' in flags and rowname != key:
                if key:
                    key = rowname
            if rowname==key:
                add_string += " PRIMARY KEY"
            add_string += ","
        add_string = add_string[0:-1] + ")"
        self.execute([add_string,sql_params])
        if key:
            self.execute(['CREATE INDEX %s%sIndex'%(name,key) +' ON %s (%s)'%(name,key),])
        self.changed=True
        return TableObject(self, name, key)

    def create_normed_view (self, name, data):
        """Create denormed view working from table named name with
        columns described in data.

        We return a view named name + _view.

        Our view will have all the same column names as our original
        table, but will have proper JOINs to handle normalizing all of
        attributes stored as IDs (and contained in self.normalizations).
        """
        joins = []
        columns = []
        for col,typ,flags in data:
            if self.normalizations.has_key(col):
                normtable = self.normalizations[col].__tablename__
                joins.append('LEFT JOIN %(normtable)s ON %(name)s.%(col)s=%(normtable)s.id'%locals())
                columns.append('%(normtable)s.%(normtable)s AS %(col)s'%locals())
            else:
                columns.append('%(name)s.%(col)s AS %(col)s'%locals())
        view_name = name + '_view'
        join_statement = ' '.join(joins)
        columns = ','.join(columns)
        statement = """CREATE VIEW %(view_name)s AS SELECT %(columns)s
        FROM %(name)s %(join_statement)s"""%locals()
        self.execute((statement,()))
        return self.get_table(view_name,data,None)        

    def _check_for_table (self, name):
        raise NotImplementedError

    def get_table (self, name, data, key=None):
        results = self._check_for_table(name)
        if results:
            return TableObject(self,name,key)
        else:
            return self.create(name,data,key)

    def get_view (self, name, data, key=None):
        if self._check_for_table(name+'_view'):
            return self.get_table(name+'_view',data)
        else:
            return self.create_normed_view(name,data)

    def pytype_to_sqltype (self, typ):
        types=[(str,"text"),
               (int, "int"),
               (float,"float"),
               (unicode,"unicode"),
               (bool, "binary")]
        for t in types:
            if t[0] == typ:
                return t[1]
        # DEFAULT TO LAST TYPE
        return types[-1][1]

    def hone_type (self, typstring):
        """By default, we trust user. Subclasses can implement customization"""
        return typstring

    def insert (self, name, data):
        """Use this method to insert data into a table.

        Data is a dictionary with column names as keys and values as values.

        Table name is a string.
        """
        t = TimeAction('PythonicSQL.insert()',3)
        if type(data) != DictionaryType:
            raise TypeError, 'expected dictionary type argument'
        # Magic to handle read-only views bandying about...
        if len(name)>5 and name[-5:] == '_view':
            self._denormalize_values_(data) #modifies in place
            name = name[0:-5]
        ins_string = "INSERT INTO %s"%name
        sql_params = []
        if data:
            ins_string += "("
            for k in data.keys():
                ins_string += "%s, "%k
            ins_string = ins_string[0:-2] + ")"
            ins_string += " values ("
            for v in data.values():
                ins_string += "%s, "
                sql_params += [v]
            ins_string = ins_string[0:-2] + ")"
        else:
            fields=self.get_fields_for_table(name)
            ins_string = ins_string + " VALUES (" + ", ".join(["?"] * len(fields)) + ")"
        tt=TimeAction('PythonicSQL.insert() - self.execute()',4)
        self.execute([ins_string,sql_params])
        tt.end()
        self.changed = True
        t.end()
        
    def delete (self, name, criteria={}, logic="and"):
        """Delete rows from table NAME where criteria CRITERIA are met."""
        if len(name)>5 and name[-5:] == '_view':
            self._denormalize_values_(criteria)
            name = name[0:-5]
        if criteria:
            del_string = "DELETE FROM %s"%name
            wstr,wpar = self.make_where_statement(criteria,logic)
            del_string += " %s"%wstr
            self.execute([del_string,wpar])
        else:
            debug('WARNING: CLEARING OUT TABLE %s!'%name,0)
            del_string = "DELETE * FROM %s"%name
            self.execute(del_string)

    def _denormalize_values_ (self, fields):
        """Modify values in fields to de-normalize.

        Replace strings with IDs for all columns referenced in
        self.normalizations.
        """
        for col,val in fields.items():
            if self.normalizations.has_key(col):
                already_there = self.normalizations[col].fetch_one(
                    **{col:val}
                    )
                if already_there:
                    fields[col]=already_there.id
                else:
                    self.normalizations[col].append({col:val})
                    row = self.normalizations[col][-1]
                    fields[col]=row.id

    def update (self, name, criteria, updated_fields):
        """Update table NAME where CRITERIA are met.  UPDATED_FIELDS
        is a dictionary of {COLUMNS:NEW_VALUES...}."""
        if len(name)>5 and name[-5:] == '_view':
            # In this case, we're dealing with a view.
            # It's time we do some fancy ass magic...
            self._denormalize_values_(updated_fields)
            name = name[0:-5]
        up_string = "UPDATE %s"%name
        sql_params = []
        up_string += " SET "
        updates = []
        for k,v in updated_fields.items():
            update = "%s="%k
            update += "%s"
            updates.append(update)
            sql_params += [v]
        up_string += ", ".join(updates)
        up_string += " "
        wherestring,whereparams = self.make_where_statement(criteria, "and")
        up_string += wherestring
        sql_params += whereparams
        self.changed=True
        self.execute([up_string,sql_params])

    def retrieve (self, name, fields=None, criteria={}, logic="and", filters=[]):
        """Retrieve FIELDS from table NAME where CRITERIA are met, possibly filtering
        with functions in list FILTERS. Filters will be handed a RowObject and expected
        to return TRUE to keep the row.  If FIELDS is None, we select all fields in the table.
        retrieve returns a Fetcher with RowObjects."""
        sel_string,sql_params=self.make_select_statement(name,fields)
        if criteria:
            wstr,wpar=self.make_where_statement(criteria,logic)
            sel_string += " %s"%wstr
            sql_params += wpar
        if not fields:
            fields = self.get_fields_for_table(name)
        return self.execute_and_fetch([sel_string,sql_params],name,self,fields,filters=filters)

    def retrieve_group (self, name, field, criteria={}, logic='and',
                        filters=[],groupattr='groupvw'):
        """retrieve_group mimics metakit's groupby functionality. We groupby FIELD
        and return a Fetcher whose RowObjects contain the special attribute GROUPATTR,
        which points to a list of all rows with the given FIELD."""
        sel_string,sql_params=self.make_select_statement(name,None)
        if criteria:
            wstr,wpar = self.make_where_statement(criteria,logic)
            sel_string += " %s"%wstr
            sql_params += wpar
        sel_string += " GROUP BY %s"%field
        debug('retrieve_group: %s %s'%(sel_string,sql_params),sql_debug_level)
        c = self.new_cursor()
        c.execute(sel_string,sql_params)
        fields = self.get_fields_for_table(name)
        return FetcherPivot(c,name,self,fields,filters,pivot_on=field,pivot_attr=groupattr,
                            criteria=criteria)

    def retrieve_unique (self, name, field, criteria={}, logic="and",
                         filters=[]):
        #sel_string,sql_params=self.make_select_statement(name,[field])
        sel_string,sql_params = 'SELECT DISTINCT %(field)s FROM %(name)s '%locals(),[]
        if criteria:
            wstr,wpar = self.make_where_statement(criteria,logic)
            sel_string += wstr
            sql_params += wpar
        return [x[0] for x in self.execute([sel_string,sql_params])]
                   

    def retrieve_counted (self, name, field, criteria={}, logic="and", count_property="count",
                          filters=[]):
        sel_string,sql_params = self.make_select_statement(name,[field,'COUNT(%s)'%field])
        if criteria:
            wstr,wpar = self.make_where_statement(criteria,logic)
            sel_string += " %s"%wstr
            sql_params += wpar
        sel_string+= " GROUP BY %s"%field
        return self.execute_and_fetch([sel_string,sql_params],name,self,[field,count_property],filters=filters)

    def make_select_statement (self, name, fields):
        sel_string = "SELECT "
        if fields:
            for f in fields:
                sel_string += "%s, "%f
            sel_string = sel_string[0:-2]
        else:
            sel_string += "*"
        sel_string += " FROM %s"%name
        return sel_string,[]

    def make_where_statement (self, criteria, logic="AND"):
        sel_string = ""
        sql_params = []
        if criteria:
            sel_string += "where"
            for k,v in criteria.items():
                if type(v)==tuple or type(v)==list:
                    operator,crit = v
                else:
                    operator = "=="
                    crit = v
                sel_string = sel_string + " %s %s "%(k,operator) + " %s" + " %s"%logic
                sql_params += [crit]
            sel_string = sel_string[0:-len(logic)]
        debug("Made where statement from %s: %s"%(criteria,sel_string),0)
        return sel_string,sql_params

    def fetch_table_fields (self, name):
        raise NotImplementedError
        
    def get_fields_for_table (self,name):
        if not self._table_fields.has_key(name):
            fields = self.fetch_table_fields(name)
            self._table_fields[name]=fields
            debug('fields for %s: %s'%(name,fields),8)
            return fields
        else:
            return self._table_fields[name]
        
        

    def count (self, table, column, criteria=None):
        if not column: column = '*'
        cnt_string = "SELECT COUNT(%s) FROM %s"%(column,table)
        cnt_param = []
        if criteria:
            wstr,wpar = self.make_where_statement(criteria)
            cnt_string += " %s"%wstr
            cnt_param += wpar
        return int(self.execute([cnt_string,cnt_param])[0][0])


def fetcher (cursor, name, db, fields):
    fetched = cursor.fetchone()
    while fetched:
        yield RowObject(name, db, fetched,fields)
        fetched = cursor.fetchone()

class Fetcher (list):

    """A Fetcher lets us look at a database query as a list of results.
    Each item in the list is a RowObject"""
    
    def __init__ (self,cursor, name, db, fields, filters=[]):
        self.cursor = cursor
        self.name = name
        self.db = db
        self.fields = fields
        self.filters = filters
        self.rows = []
        self.generated = False
        self.length = cursor.rowcount
        list.__init__(self)
        #self.generate_all()
        
    def generate (self):
        if self.generated: return
        self.fetched = self.cursor.fetchone()
        while self.fetched:
            row = self.make_row()
            use_row = True
            if self.filters:
                for f in self.filters:
                    if not f(row):
                        use_row = False
                        break
            if use_row:
                self.rows.append(row)
                yield self.rows[-1]
            self.fetched = self.cursor.fetchone()
        self.cursor.close()
        self.generated = True
        list.__init__(self,self.rows)

    def make_row (self):
        return RowObject(self.name, self.db, self.fetched,self.fields)

    def generate_all (self):
        g = self.generate()
        try:
            g=g.next()
        except:
            g=None
        while g:
            try:
                g=g.next()
            except:
                g=None
        
    def __iter__ (self):
        if not self.generated:
            return self.generate()
        else:
            return iter(self.rows)

    def __len__ (self):
        return self.length

    def __nonzero__ (self):
        if len(self) > 0: return True
        else: return False

    def __repr__ (self):
        return '<Fetcher %s fields=%s>'%(self.name,self.fields)

    def __getitem__ (self,index):
        return [x for x in iter(self)][index]

    def __delitem__ (self,index):
        self[index].__delete__()

class FetcherPivot (Fetcher):
    def __init__ (self,cursor, name, db, fields, filters=[],
                  pivot_attr='groupvw',pivot_on=None, criteria={}):
        self.pivot_attr=pivot_attr
        self.pivot_on=pivot_on
        self.criteria=criteria,
        self.filters=filters,
        Fetcher.__init__(self,cursor,name,db,fields,filters)

    def make_row (self):
        return RowObjectPivot(self.name,self.db,self.fetched,self.fields,
                  pivot_attr=self.pivot_attr,pivot_on=self.pivot_on,
                  criteria=self.criteria,filters=self.filters)

class RowObject :
    """Return an object based on a SQL query. Our object has attributes
    for each field in our result set."""
    def __init__ (self, name, db, results, fields):
        self.__instantiated__=False
        self.__db__ = db
        self.__table__ = name
        self.__fields__ = {}
        for i,f in enumerate(fields):
            setattr(self,f,results[i])
            #self.dic[f]=results[i]
        for f in self.__db__.get_fields_for_table(self.__table__):            
            if not hasattr(self,f):
                setattr(self,f,None)
        self.__instantiated__ = True

    def __nonzero__ (self):
        if self.__fields__: return True
        else: return False

    def __setattr__ (self, name, val):
        self.__dict__[name]=val
        if name.find('__') != 0:
            if self.__instantiated__==True:
                self.__db__.update(self.__table__, self.__fields__, {name:val})
            self.__fields__[name]=val

    def __delete__ (self):
        self.__db__.delete(self.__table__,criteria=self.__fields__)

    def __repr__ (self):
        return '<row object (%s)>'%self.__table__

    def __str__ (self):
        return '<row object> (%s)>'%self.__table__
    
class RowObjectPivot (RowObject):
    def __init__ (self, name, db, results, fields, pivot_on, pivot_attr, criteria={}, filters=[]):
        """We are imitating metakit's groupby functionality here. pivot_on becomes
        a key who we group by and provide a table for.  pivot_attr is the name
        of our own attribute to be set to a view of those items we've grouped on.
        This is very similar to getting a "count", only different."""
        RowObject.__init__(self,name,db,results,fields)
        self.__instantiated__ = False
        self.__pivot_on__ = pivot_on
        self.__pivot_attr__ = pivot_attr
        self.__criteria__ = criteria
        if type(self.__criteria__) != type({}):
            self.__criteria__={}
        self.__filters__ = filters
        crit = self.__criteria__.copy()
        crit[self.__pivot_on__]=getattr(self,self.__pivot_on__)
        setattr(self,
                self.__pivot_attr__,
                TableObject(db,
                            self.__table__,
                            criteria=crit,
                            filters=self.__filters__,
                            )
                )
        self.__instantiated__ = True

class TableObject (list):

    """A TableObject makes SQL look similar to a metakit view.

    It is a list, which allows us to access rows in a table with an
    index or to loop through rows easily. TableObject also provides
    the ability to filter based on criteria, returning new
    TableObjects representing "filtered" tables (essentially, saved queries)."""

    def __init__ (self, db, table, key=None, criteria=None, filters=[]):
        self._last = None
        self.__db__ = db
        self.__tablename__ = table
        self.__key__ = key
        self.__criteria__ = criteria
        self.__filters__ = filters
        for f in self.__db__.get_fields_for_table(self.__tablename__):
            setattr(self,f,f)
        debug('Created TableObject %s, filters=%s'%(self,self.__filters__),0)

    def __getitem__ (self, index):
        debug('__getitem__ called for %s'%self,0)
        if index == -1 and self._last:
            try:
                return self.select(**self._last)[-1]
            except:
                print 'WTF, selecting our last member failed.'
                print 'We were trying to call'
                print '%s.select'%self,'(%s)',self._last,'[-1]'
                print 'We have ',len(self),'items'
                raise
        generator = self.__iter__()
        n = 0
        if index < 0:
            index = len(self) + index
        if index < 0:
            raise IndexError
        debug('index=%s'%index)
        while n <= index:
            try:
                retval = generator.next()
            except StopIteration:
                raise IndexError
            n += 1
        return retval

    def __len__ (self):
        ret=self.__db__.count(self.__tablename__,self.__key__,self.__criteria__)
        debug('%s length=%s'%(self,ret),1)
        return ret

    def append (self, item):
        self._last = item.copy()
        self.__db__.insert(self.__tablename__,item)
        

    def extend (self, lst):
        for i in lst: self.append(i)

    def delete (self, criteria=None):
        """Delete from self based on criteria. If criteria=None, delete self entirely."""
        self.__db__.delete(self.__tablename__,criteria=criteria)

    def counts (self, column, count_column):
        """Modelled after metakit. Return a new view grouped by column, with the number of
        entries for column stored in the count_column"""
        return self.__db__.retrieve_counted(self.__tablename__,column,count_property=count_column,
                                            criteria=self.__criteria__,
                                            filters=self.__filters__)

    def groupby (self, column, vwattr):
        return self.__db__.retrieve_group(self.__tablename__,
                                          column,
                                          criteria=self.__criteria__,
                                          filters=self.__filters__,
                                          groupattr=vwattr)

    def get_unique (self, column, **criteria):
        if not self.__criteria__: self.__criteria__={}
        crit = self.__criteria__.copy()
        for k,v in criteria.items(): crit[k]=v
        return self.__db__.retrieve_unique(self.__tablename__,column,criteria=crit,filters=self.__filters__)

    def fetch_one (self,**dictionary):
        table = self.select(**dictionary)
        if table:
            return table[0]

    def select (self,**dictionary):
        """Return a TableObject with a subview of ourselves based on criteria.

        Critieria are handed to us in a dictionary."""
        debug('select called with %s'%dictionary,0)
        if self.__criteria__: criteria = self.__criteria__.copy()
        else: criteria = {}
        for k,v in dictionary.items():
            criteria[k]=v
        return TableObject(self.__db__,
                           self.__tablename__,
                           key=self.__key__,
                           criteria=criteria,
                           filters=self.__filters__)

    def filter (self, *filters):
        debug('Table Filtering',0)
        myfilters=self.__filters__[0:]
        myfilters.extend(filters)
        return TableObject(self.__db__,
                           self.__tablename__,
                           key=self.__key__,
                           criteria=self.__criteria__,
                           filters=myfilters)
    
    def __getslice__ (self, i, j):
        generator = self.__iter__()
        n = 0
        rets = []
        while n < j:
            try:
                retval = generator.next()
            except StopIteration:
                raise IndexError
            if n >= i:
                rets.append(retval)
            n += 1
        return rets

    def __repr__ (self):
        ret = '<TableObject %s'%self.__tablename__
        if self.__criteria__: ret+="%s"%self.__criteria__
        if self.__filters__: ret+=" filter: %s"%self.__filters__
        ret += ">"
        return ret

    def __iter__ (self):
        return iter(self.__db__.retrieve(self.__tablename__,
                                         criteria=self.__criteria__,
                                         filters=self.__filters__))


