import rdatabase
import os, os.path, re
import gourmet.gglobals as gglobals
from gettext import gettext as _

class RecData (rdatabase.RecData):

    # If we search for REGEXP('f.*','foo') instead of 'foo REGEXP f.*'
    USE_PAREN_STYLE_REGEXP = False

    REGEXP_FIXER_REGEXP = re.compile('\s*([A-Za-z0-9_?.]*)\s*REGEXP\s*([A-Za-z0-9_?.]*)\s*')

    def __init__ (self, *args): raise NotImplementedError

    # SQL Convenience stuff
    def create (self, name, table, key=None, flags=[]):
        """Use this method to create a table in this database object. Expected
        arguments are a table name and a list [(name, type, [flags])] } with the column names
        as strings and type being type objects representing the data type
        used in that column."""
        #if type(table) != DictionaryType:
        #    raise TypeError, 'expected dictionary type argument'
        add_string = "CREATE TABLE %s ("%name
        sql_params = []
        for rowname,typ,flags in table:
            if typ=='int': typ='INTEGER'
            elif typ=='binary': typ='BLOB'
            #if type(typ) != type(""):
            #    typ = self.pytype_to_sqltype(typ)
            #typ = self.hone_type(typ)
            add_string +=  "%s %s"%(rowname,typ)
            if 'AUTOINCREMENT' in flags and rowname != key:
                if key:
                    key = rowname
            if rowname==key:
                add_string += " PRIMARY KEY"
                if 'AUTOINCREMENT' in flags:
                    add_string += " AUTOINCREMENT"; print 'AUTOINCREMENT',rowname,typ,flags
            add_string += ","
        add_string = add_string[0:-1] + ")"
        self.execute(self.cursor,add_string,sql_params)
        if key:
            self.execute(self.cursor,'CREATE INDEX %s%sIndex'%(name,key) +' ON %s (%s)'%(name,key))
        self.changed=True

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
                sel_string = sel_string + " %s %s "%(k,operator) + " ?" + " %s"%logic
                sql_params += [crit]
            sel_string = sel_string[0:-len(logic)]
        return sel_string,sql_params

    def make_order_by_statement (self, sorts):
        """Sorts is a list of tuples (column,1) (ASC) or (column,-1) (DESC)"""
        sql = " ORDER BY "
        sql += ", ".join([c+' '+(d<0 and 'DESC' or 'ASC') for c,d in sorts])
        #sql += ", ".join([c+' '+(d<0 and 'DESC' or '') for c,d in sorts])
        return sql

    def execute (self, cursor, sql, params=[]):
        try:
            cursor.execute(sql,params)
        except:
            print "Failed to execute:"
            print "sql   : ",sql
            print "params: ",params
            raise
        
    def initialize_connection (self):
        raise NotImplementedError

    def save (self):
        raise NotImplementedError

    def check_for_table (self, name):
        raise NotImplementedError

    def setup_table (self, name, data, key=None):
        if not self.check_for_table(name):
            self.create(name,data,key)
        self.columns[name]=[r[0] for r in data]
        return name

    def fetch_len (self, table, **criteria):
        if criteria:
            where,params = self.make_where_statement(criteria)
        else:
            where,params = '',[]
        sql = 'SELECT COUNT(*) FROM ' + table + ' ' + where
        self.execute(self.cursor,sql,params)
        return self.cursor.fetchone()[0]

    # Fetching and such...
    def fetch_all (self, table, sort_by=[], distinct=False, limit=None, **criteria):
        """Table is our table object (in our case, just a string)
        sort_by is a list of sort criteria, as tuples ('column',1) or ('column',-1)

        limit is None or a tuple which tells us how many rows we want
        and where we start fetching (start,nrows)
        """
        if criteria:
            where,params = self.make_where_statement(criteria)
        else:
            where,params = '',[]
        cursor = self.connection.cursor()
        column_names = self.columns[table]
        sql = 'SELECT ' + (distinct and 'DISTINCT ' or '') + ', '.join(column_names) + ' FROM '+table+' '+where
        if sort_by:
            sql += ' '+self.make_order_by_statement(sort_by)+' '
        if limit:
            sql += ' '+'LIMIT '+', '.join([str(n) for n in limit])
        self.execute(cursor,sql,params)
        return Fetcher(cursor, column_names)
        
    def fetch_one (self, table, **criteria):
        where,params = self.make_where_statement(criteria)
        self.execute(self.cursor,'SELECT '+', '.join(self.columns[table])+' FROM %s '%table + where,params)
        result = self.cursor.fetchone()
        if not result: return None
        else: return RowObject(self.columns[table],result)

    def fetch_count (self, table, column, sort_by=None,**criteria):
        where,params = self.make_where_statement(criteria)
        cursor = self.connection.cursor()
        sort_by = [((a=='count'
                     and 'COUNT(%s)'%column
                     or a),b) for a,b in sort_by]
        self.execute(cursor,
                ("SELECT %s, COUNT(%s)"%(column,column)
                 +
                 " FROM %s"%table
                 +
                 " " + where
                 + " GROUP BY " + column
                 + (sort_by and self.make_order_by_statement(sort_by)
                    or '')
                 ),
                     params)
        return Fetcher(cursor,[column,'count'])

    def fetch_food_groups_for_search (self,
                                      words):
        params = []
        order_params = []
        where_statements = []
        order_statements = []
        for w in words:
            where_statements.append('desc LIKE ?')
            params.append('%'+w+'%')
            order_statements.append('InStr(desc,?)')
            order_params.append(w)
        statement = 'SELECT DISTINCT foodgroup FROM %s'%self.nview \
                    + (where_statements
                       and (' WHERE '
                            + ' AND '.join(where_statements)
                            )
                       or '') \
                       + ' ORDER BY foodgroup'
        self.execute(self.cursor,
                     statement,
                     params)
        cats = []
        for r in self.cursor.fetchall(): cats.append(r[0])
        return cats

    def search_nutrition (self, words, group=None, limit=None):
        params = []
        order_params = []
        where_statements = []
        order_statements = []
        for w in words:
            where_statements.append('desc LIKE ?')
            params.append('%'+w+'%')
            order_statements.append('InStr(desc,?)')
            order_params.append(w)
        order_statements.append('length(desc)')
        if group:
            where_statements.append('foodgroup = ?')
            params.append(group)
        order_statements.append('desc')
        statement = 'SELECT ' + ', '.join(self.columns[self.nview]) + ' FROM %s'%self.nview \
                    + (where_statements
                       and (' WHERE '
                            + ' AND '.join(where_statements)
                            )
                       or '') \
                       + ' ORDER BY ' + ', '.join(order_statements)
        if limit:
            statement += ' '+'LIMIT '+', '.join([str(n) for n in limit])
        cursor = self.connection.cursor()
        self.execute(cursor,
                     statement,
                     params+order_params),
        return Fetcher(
            cursor,
            self.columns[self.nview]
            )

    def search_recipes (self, searches, sort_by=[], limit=None):
        """Search recipes for columns of values.

        "category" and "ingredient" are handled magically
        """
        crit = ''
        nested_selects = []
        params = []
        for s in searches:
            col = s['column']
            if col=='ingredient':
                sql = '''
                SELECT DISTINCT id FROM %(view)s
                WHERE ingkey %(operator)s ?'''%{
                    'view':self.iview,
                    'operator':s.get('operator','LIKE')
                    }
                prms = [s['search']]
                nested_selects.append((sql,prms))
            elif col=='category':
                sql = '''
                SELECT DISTINCT id FROM %(view)s
                WHERE category %(operator)s ?'''%{
                    'view':self.catview,
                    'operator':s['operator']
                    }
                prms = [s['search']]
                nested_selects.append((sql,prms))
            else:
                if '.' not in col:
                    col = self.rview + '.' + col
                if crit:
                    crit += ' ' + s.get('logic','AND') + ' '
                op = s.get('operator','LIKE')
                crit += col + ' ' + op + ' ' + '?'                
                params.append(s['search'])
        cursor = self.connection.cursor()
        if crit:
            if 'category' in [s[0] for s in sort_by]:
                join='JOIN %(catview)s on %(catview)s.id=%(view)s.id'%{
                    'catview':self.catview,
                    'view':self.rview}
            else:
                join = ''
            base_search = """SELECT DISTINCT %(view)s.id FROM %(view)s %(join)s
            WHERE %(crit)s""" %{'view':self.rview,
                                'join':join,
                                'crit':crit}
        elif nested_selects:
            base_search,params = nested_selects[0]
            nested_selects = nested_selects[1:]
        for sql,prms in nested_selects:
            base_search += ' AND id IN ( ' + sql + ')'
            params += prms
        if sort_by: base_search += '\n'+self.make_order_by_statement(sort_by)
        if limit:
            base_search += ' '+'LIMIT '+', '.join([str(n) for n in limit])
        if self.USE_PAREN_STYLE_REGEXP:
            base_search = self.REGEXP_FIXER_REGEXP.sub(' REGEXP(\\2,\\1) ',
                                                       base_search)
        self.execute(cursor,
                     base_search,
                     params
                     )
        return SearchFetcher(cursor,self,self.rview)

    def get_unique_values (self, colname, table=None, **criteria):
        if not table: table=self.rview
        if criteria:
            where,params = self.make_where_statement(criteria)
        else:
            where,params = '',[]
        self.execute(self.cursor,
                     'SELECT DISTINCT %s FROM %s '%(colname,table)+where,
                     params)
        ret = []
        for row in self.cursor.fetchall():
            if row[0]: ret.append(row[0])
        return ret

    def get_ingkeys_with_count (self, search={}):
        """Get unique list of ingredient keys and counts for number of times they appear in the database.
        """
        c = self.connection.cursor()
        SQL = 'SELECT ingkey,COUNT(*) FROM '+self.iview
        params = []
        if search:
            SQL += ' WHERE ' + search.get('column','ingkey') + ' ' + search.get('operator','LIKE') + ' ?'
            params += [search['search']]
            if self.USE_PAREN_STYLE_REGEXP:
                SQL = self.REGEXP_FIXER_REGEXP.sub(' REGEXP(\\2,\\1) ',SQL)
        SQL += ' GROUP BY ingkey'
        self.execute(c,SQL,params)
        return Fetcher(c,['ingkey','count'])

    # Adding recipes...
    def do_add (self, table, d):
        SQL = 'INSERT INTO ' + table + '('+', '.join(d.keys()) + ')'        
        SQL += ' VALUES (' +  ", ".join(["?"]*len(d)) + ')'
        self.execute(self.cursor,SQL,d.values())

    def do_add_nutrition (self, d):
        self.do_add(self.nview,d)
        self.execute(
            self.cursor,
            'SELECT ndbno FROM '+self.nview+' WHERE rowid=last_insert_rowid()'
            )
        return DelayedRowObject(self.cursor.fetchone()[0],
                                'ndbno',self.nview,self)

    def do_add_rec (self, rdict):
        self.do_add(self.rview,rdict)
        self.execute(self.cursor,
                     "SELECT id FROM "+self.rview+" WHERE rowid=last_insert_rowid()"
                     )
        return DelayedRowObject(self.cursor.fetchone()[0],
                                'id',self.rview,self)

    def new_rec (self):
        return self.add_rec({'title':_('New Recipe')})

    def new_id (self):
        """Reserve a new ID"""
        raise NotImplementedError

    def do_add_cat (self, catdict):
        self.do_add(self.catview,catdict)
        self.execute(self.cursor,'SELECT last_insert_rowid()')
        return DelayedRowObject(self.cursor.fetchone()[0],
                                'rowid',self.catview,self)

    def do_add_ing (self, ingdict):
        self.do_add(self.iview,ingdict)
        self.execute(self.cursor,'SELECT last_insert_rowid()')
        return DelayedRowObject(self.cursor.fetchone()[0],
                                'rowid',self.iview,self)

    def delete_by_criteria (self, table, criteria):
        where,params = self.make_where_statement(criteria)
        self.execute(self.cursor,
                     "DELETE FROM "+table+" "+where,
                     params
                     )

    def update (self, table, criteria, new_values_dic):
        where,params = self.make_where_statement(criteria)
        params = new_values_dic.values() + params
        self.execute(self.cursor,
                     "UPDATE " + table + " SET " +\
                     ", ".join(["%s = ?"%k for k in new_values_dic.keys()]) +\
                     " " + where,
                     params)

    def delete_ing (self, ing):
        if hasattr(ing,'rowid'): ing = ing.rowid
        if type(ing)==int:
            self.execute(self.cursor,
                         "DELETE FROM "+self.iview+" WHERE rowid="+str(ing)
                         )
        else:
            print "Damn, can't delete",ing

    def do_modify_ing (self, ing, ingdict):
        ing = self.do_modify(self.iview,ing,ingdict)
        return DelayedRowObject(ing,'rowid',self.iview,self)

    def do_modify_rec (self, rec, recdict):
        if type(rec)!=int: rec=rec.id
        rec = self.do_modify(self.rview,rec,recdict,unique_id_col='id')
        return DelayedRowObject(rec,'id',self.rview,self)

    def do_modify_cat (self, cat, catdict):
        if type(cat)!=int: cat=cat.rowid
        cat = self.do_modify(self.catview,cat,catdict)
        return DelayedRowObject(cat,'rowid',self.catview,self)

    def do_modify (self, table, rowid, d, unique_id_col='rowid'):
        if isinstance(rowid,RowObject):
            if hasattr(rowid,'rowid'):
                rowid = rowid.rowid
            else:
                new = {}
                for k in rowid.__column_names__:
                    v=getattr(rowid,k)
                    if v:
                        new[k]=getattr(rowid,k)
                rowid = new
        if type(rowid)==dict:
            where,params = self.make_where_statement(rowid)
            self.execute(
                self.cursor,
                "SELECT " + unique_id_col + "  FROM " + table + " " + where,
                params
                )
            try:
                rowid = self.cursor.fetchone()[0]
                if not rowid:
                    raise "Couldn't find row for %s %s,%s"%(table,where,params)
            except (IndexError, TypeError):
                print 'Strange.'
                print 'Tried to select rowid FROM ',table,where,params
                raise "Modifying nonexistent row" + table + "%s"%rowid
        if type(rowid)!=int:
            raise str("%s is not a ROWID. We were handed: "%(rowid,
                                                             table,rowid,d,unique_id_col
                                                             )
                      )
        self.execute(self.cursor,
                     ("UPDATE "+table
                      +
                      " SET "
                      +
                      ", ".join(["%s=?"%k for k in d.keys()])
                      +
                      " WHERE "
                      +
                      "%s = %s"%(unique_id_col,rowid)
                      ),
                     d.values()
                     )
        return rowid

class RowObject:
    def __init__ (self, column_names, columns):
        self.__columns__ = columns
        self.__column_names__ = column_names
        if len(self.__columns__)!=len(self.__column_names__):
            raise "Number of columns and number of column names must be the same!"
        for n,cn in enumerate(self.__column_names__):
            setattr(self,cn,self.__columns__[n])

class DelayedRowObject (RowObject):

    def __init__ (self, id, idprop, table, db):
        self.__idprop__ = idprop
        self.__retrieved__ = False
        self.__db__ = db
        self.__table__ = table
        self.__column_names__ = self.__db__.columns[self.__table__]
        setattr(self,idprop,id)

    def __getattr__ (self, att):
        if not self.__retrieved__ and not att.find('__')==0 and not att==self.__idprop__:
            return self.__retrieve__(att)
        raise AttributeError

    def __retrieve__ (self,att):
        ret = None
        self.__db__.execute(
            self.__db__.cursor,
            ("SELECT " + ", ".join(self.__column_names__) + "  FROM " + self.__table__
             + " WHERE " + self.__idprop__ + "=" + str(getattr(self,self.__idprop__))
             ))
        row = self.__db__.cursor.fetchone()
        for n,cn in enumerate(self.__column_names__):
            setattr(self,cn,row[n])
            if cn==att: ret = row[n]
        self.__retrieved__ = True
        return ret

class Fetcher (list):
    def __init__ (self, cursor, column_names):
        self.column_names = column_names
        self.cursor = cursor        
        self.generated = False
        # Generate ourselves right away...
        for n in self: n

    def get_row (self, result):
        if result: return RowObject(self.column_names,result)

    def __iter__ (self):
        if self.generated:
            for r in list.__iter__(self): yield r
        else:
            for r in list.__iter__(self): yield r
            result = self.get_row(self.cursor.fetchone())
            while result:
                self.append(result)
                yield result
                result = self.get_row(self.cursor.fetchone())
            self.generated = True
            self.cursor.close()

    def __len__ (self):
        if self.generated:
            return list.__len__(self)
        else:
            for r in self: 1
            return list.__len__(self)
        

    def __nonzero__ (self):
        if list.__len__(self)>0: return True
        try:
            self[0]
        except:
            return False
        else:
            return True

    def __repr__ (self): return '<Fetcher>'

    def __getitem__ (self, index):
        if index < 0:
            index = len(self) + index
            if index < 0: raise IndexError
        try:
            return list.__getitem__(self,index)
        except IndexError:
            
            n = list.__len__(self)
            if not self.generated:
                for row in self:
                    if n==index: return row
                    n += 1
            raise IndexError
        
    def __getslice__ (self, i, j):
        try:
            list.__getitem__(self,i) and list.__getitem__(self,j)
        except IndexError:
            ret = []
            for n in range(i,j):
                if n >= len(self): break
                ret.append(self[n])
            return ret
        else:
            return list.__getslice__(self,i,j)

class SearchFetcher (Fetcher):
    def __init__ (self, cursor, db, table, id_prop='id'):
        self.cursor=cursor
        self.db = db
        self.id_prop = id_prop
        self.generated = False
        self.table = table
        # Generate ourselves right away
        for n in self: n

    def get_row (self, result):
        if not result: return
        else: idval = result[0]
        #idval = getattr(result,self.id_prop)
        return DelayedRowObject(
            idval,
            self.id_prop,
            self.table,
            self.db
            )
