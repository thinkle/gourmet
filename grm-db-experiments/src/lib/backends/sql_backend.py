import rdatabase
import os, os.path, re
import gourmet.gglobals as gglobals
from gettext import gettext as _

class RecData (sql_db.RecData):

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
        return sql

    def execute (self, cursor, sql, params=[]):
        try:
            #print 'Executing:',cursor,sql,params
            cursor.execute(sql,params)
        except UnicodeDecodeError:
            print 'Stupid Unicode Decode Error!'
            import traceback; traceback.print_exc()
            print 'Fearlessly continue without raising an error...'
            print "(now that can't be a good idea, can it)"
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
    def fetch_all (self, table, sort_by=[], **criteria):
        if criteria:
            where,params = self.make_where_statement(criteria)
        else:
            where,params = '',[]
        cursor = self.connection.cursor()
        #print self.cursor,'SELECT * FROM '+table+' '+where,params
        sql = 'SELECT * FROM '+table+' '+where
        if sort_by:
            sql += ' '+self.make_order_by_statement(sort_by)+' '
        self.execute(cursor,sql,params)
        #result = self.cursor.fetchone()
        column_names = self.columns[table]
        return Fetcher(cursor, column_names)
        
    def fetch_one (self, table, **criteria):
        where,params = self.make_where_statement(criteria)
        self.execute(self.cursor,'SELECT * FROM %s '%table + where,params)
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

    def search_recipes (self, searches):
        """Search recipes for columns of values.

        "category" and "ingredient" are handled magically
        """
        crit = ''
        joins = []
        params = []
        if 'ingredient' in [s.get('column','') for s in searches]:
            searches.append({'column':self.iview+'.'+'deleted',
                             'logic':'AND',
                             'operator':'=',
                             'search':False})
        for s in searches:
            col = s['column']
            if col=='ingredient':
                col=self.iview+'.ingkey'
                join_string = 'JOIN '+self.iview+' ON '\
                              + self.iview+'.id='+self.rview+'.id'
                if join_string not in joins: joins.append(join_string)
            elif col=='category':
                col=self.catview+'.category'
                join_string = ('JOIN '+self.catview+' ON ' 
                               + self.catview + '.id='+self.rview+'.id')
                if join_string not in joins: joins.append(join_string)
            elif '.' not in col:
                col = self.rview + '.' + col
            if crit:
                crit += ' ' + s.get('logic','AND') + ' '
            op = s.get('operator','LIKE')
            crit += col + ' ' + op + ' ' + '?'
            params.append(s['search'])
        cursor = self.connection.cursor()
        self.execute(cursor,
                     "SELECT recipe.id FROM recipe " + " ".join(joins) + " WHERE " + crit,
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
        for row in self.cursor.fetchall(): ret.append(row[0])
        return ret

    # Adding recipes...
    def do_add (self, table, d):
        SQL = 'INSERT INTO ' + table + '('+', '.join(d.keys()) + ')'        
        SQL += ' VALUES (' +  ", ".join(["?"]*len(d)) + ')'
        self.execute(self.cursor,SQL,d.values())

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

    def delete_ing (self, ing):
        if hasattr(ing,'rowid'): ing = ing.rowid
        if type(ing)==int:
            self.execute(self.cursor,
                         "DELETE FROM "+self.iview+" WHERE rowid="+str(ing)
                         )
        else:
            print "Damn, can't delete",ing

    def do_modify_ing (self, ing, ingdict):
        if type(ing)!=int: ing=ing.rowid
        self.do_modify(self.iview,ing,ingdict)
        return DelayedRowObject(ing,'rowid',self.iview,self)

    def do_modify_rec (self, rec, recdict):
        if type(rec)!=int: rec=rec.id
        self.do_modify(self.rview,rec,recdict,unique_id_col='id')
        return DelayedRowObject(rec,'id',self.rview,self)

    def do_modify_cat (self, cat, catdict):
        if type(cat)!=int: cat=cat.rowid
        self.do_modify(self.catview,cat,catdict)
        return DelayedRowObject(cat,'rowid',self.catview,self)

    def do_modify (self, table, rowid, d, unique_id_col='rowid'):
        if isinstance(rowid,RowObject):
            #print 'rowid == RowObject'
            new = {}
            for k in rowid.__column_names__:
                v=getattr(rowid,k)
                if v: new[k]=getattr(rowid,k)
            rowid = new
        if type(rowid)==dict:
            where,params = self.make_where_statement(rowid)
            self.execute(
                self.cursor,
                "SELECT rowid FROM " + table + " " + where,
                params
                )
            try:
                rowid = self.cursor.fetchone()[0]
            except (IndexError, TypeError):
                print 'Strange.'
                print 'Tried to select rowid FROM ',table,where,params
                raise "Modifying nonexistent row" + table + "%s"%rowid
            
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
        setattr(self,idprop,id)

    def __getattr__ (self, att):
        if not self.__retrieved__ and not att.find('__')==0 and not att==self.__idprop__:
            return self.__retrieve__(att)
        raise AttributeError
        
    def __retrieve__ (self,att):
        ret = None
        self.__db__.execute(
            self.__db__.cursor,
            ("SELECT * FROM " + self.__table__
             + " WHERE " + self.__idprop__ + "=" + str(getattr(self,self.__idprop__))
             ))
        row = self.__db__.cursor.fetchone()
        for n,cn in enumerate(self.__db__.columns[self.__table__]):
            setattr(self,cn,row[n])
            if cn==att: ret = row[n]
        self.__retrieved__ = True
        return ret

class Fetcher (list):
    def __init__ (self, cursor, column_names):
        self.column_names = column_names
        self.cursor = cursor        
        self.generated = False

    def get_row (self, result):
        if result: return RowObject(self.column_names,result)

    def __iter__ (self):
        if self.generated:
            #print 'Plain old __iter__'
            list.__iter__(self)
        else:
            #print 'Magic __iter__'
            result = self.get_row(self.cursor.fetchone())
            while result:
                self.append(result)
                #print 'Result=',result
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
            return list.__getslice__(self,i,j)
        except IndexError:
            ret = []
            for n in range(i,j):
                if n > len(self): break
                ret.append(self[n])
            return ret

class SearchFetcher (Fetcher):
    def __init__ (self, cursor, db, table, id_prop='id'):
        self.cursor=cursor
        self.db = db
        self.id_prop = id_prop
        self.generated = False
        self.table = table

    def get_row (self, result):
        if not result: return
        else: idval = result[0]
        #idval = getattr(result,self.id_prop)
        return self.db.fetch_one(
            self.table,
            **{self.id_prop:idval}
            )
