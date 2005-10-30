import PythonicSQL
#import sqlite
from pysqlite2 import dbapi2 as sqlite
from gourmet.gdebug import debug

class PythonicSQLite (PythonicSQL.PythonicSQL):
    def __init__ (self, file):
        #print file
        self.file = file
        PythonicSQL.PythonicSQL.__init__(self,sqlite)

    def hone_type (self, typestring):
        if typestring=='int': return 'integer'
        else: return typestring

    def _execute (self, c, sql):
        """For some reason, our parameters aren't working properly."""
        statement = sql[0]
        params = (len(sql)>1 and sql[1]) or []
        if not isinstance(params,list) and not isinstance(params,tuple):
            params = [params]
        if len(sql)>2:
            print 'WTF execute got',sql,'as an argument'
            print 'We should be getting (SQL, params)'
            print 'Bad Tom, Bad!'
            raise
        # We do some pretty lame quoting by hand here.
        params = [(hasattr(p,'replace') and '"%s"'%p.replace('"','inch')
                   or
                   p==None and 'NULL'
                   or
                   type(p)!=bool and p
                   or 
                   int(p) 
                   ) for p in params]
        try:
            sql = [statement%tuple(params)]
        except TypeError:
            print """There appears to be a problem
            with executing the statment %(statement)s
            with the params %(params)s
            """%locals()
            raise
        # We have to do the escaping ourselves, which kind of sucks
        return PythonicSQL.PythonicSQL._execute(self,c,sql)

    def connect (self):
        # debugging code...
        import sys
        #logbase = os.path.join(tempfile.tempdir,"SQLITE_LOGFILE_GOURMET")
        #logfile = logbase + ".1"
        #if os.path.exists(logfile):
        #    num = logfile.split('.')[-1]
        # logfile = "%s.%s"%(logbase,int(num)+1)
        #logfi = open(logfile,'w')
        return sqlite.Connection(self.file,timeout=5000,)
                                 #encoding='utf8',
                                 #autocommit=True,)#command_logfile=sys.stderr)

    def _check_for_table (self, name):
        return self.execute(['SELECT name FROM sqlite_master WHERE NAME=%s',name])

    def fetch_table_fields (self,name):
        # Some ugly code to get a list of fields from the SQL CREATE
        # statement stored in sqlite_master
        allrows = self.execute(['SELECT sql FROM sqlite_master WHERE name=%s',name])
        statement = allrows[0][0]
        debug('get_fields_for_table, statement=%s'%statement,0)
        if statement.find('CREATE VIEW')==0:
            colpart = statement[statement.find('SELECT '):statement.find('FROM')][7:]
            statements = [s.strip() for s in colpart.split(',')]
            retval = [state.split(' AS ')[-1] for state in statements]
        else:
            statements = statement[statement.find('(')+1:statement.rfind(')')].split(',')
            retval = [x.split()[0] for x in statements]
        debug("get_fields_for_table returning: %s"%retval,0)
        return retval

if __name__ == '__main__':
    import tempfile
    fi = tempfile.mktemp()
    #fi = '/tmp/tmpKIE0WM'
    psl = PythonicSQLite(fi)
    psl.normalizations = {}
    psl.normalizations['First']=psl.get_table('First',[('id','int',['AUTOINCREMENT']),
                                                       ('First','text',[])],
                                              'id')
    psl.normalizations['Last']=psl.get_table('Last',[('id','int',['AUTOINCREMENT']),
                                                      ('Last','text',[])],
                                              'id')
    table_desc = [('First','int',[]),
                  ('Last','int',[]),
                  ('Birth_Month','int',[]),
                  ('Birth_Day','int',[]),
                  ('Birth_Year','int',[]),
                  ('myid','int',['AUTOINCREMENT']),
                  ]
    table=psl.get_table('names',table_desc,'myid')
    view = psl.get_view('names',table_desc)
    if len(view) == 0:
        view.append({'Birth_Day':21,'First':'Thomas','Last':'Hinkle'})               
        view.extend([{'First':'John'},
                   {'First':'Susan'},
                   {'First':'David'},]
                  )
    import random
    for n in range(100):
        view.append({'Birth_Day':random.randint(1,28),
                   'Birth_Month':random.randint(1,12),
                   'First':random.choice(['John','Harry','Bob','Lucy','Genevieve','Katharine','Susan']),
                   'Last':random.choice(['Hinkle','Sayre','Wilkins','Wright','Wilson']),
                   })
    for t in view:
        print 'row:'
        for m in dir(t):
            print getattr(t,m)
    #psl.c.commit()

    
