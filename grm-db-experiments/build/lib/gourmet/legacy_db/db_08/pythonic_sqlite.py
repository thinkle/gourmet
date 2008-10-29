import PythonicSQL
import sqlite
from gourmet.gdebug import debug

class PythonicSQLite (PythonicSQL.PythonicSQL):
    def __init__ (self, file):
        #print file
        self.file = file
        PythonicSQL.PythonicSQL.__init__(self,sqlite)

    def hone_type (self, typestring):
        if typestring=='int': return 'integer'
        else: return typestring

    def connect (self):
        # debugging code...
        import sys
        #logbase = os.path.join(tempfile.tempdir,"SQLITE_LOGFILE_GOURMET")
        #logfile = logbase + ".1"
        #if os.path.exists(logfile):
        #    num = logfile.split('.')[-1]
        # logfile = "%s.%s"%(logbase,int(num)+1)
        #logfi = open(logfile,'w')
        return sqlite.Connection(self.file, encoding='utf8',timeout=5000,autocommit=True,)#command_logfile=sys.stderr)

    def _check_for_table (self, name):
        return self.execute(['SELECT name FROM sqlite_master WHERE NAME=%s',name])

    def fetch_table_fields (self,name):
        allrows = self.execute(['SELECT sql FROM sqlite_master WHERE name=%s',name])
        statement = allrows[0][0]
        debug('get_fields_for_table, statement=%s'%statement,0)
        statements = statement[statement.find('(')+1:statement.rfind(')')].split(',')
        retval = [x.split()[0] for x in statements]
        debug("get_fields_for_table returning: %s"%retval,0)
        return retval

if __name__ == '__main__':
    import tempfile
    fi = tempfile.mktemp()
    #fi = '/tmp/tmpKIE0WM'
    psl = PythonicSQLite(fi)
    tt=psl.get_table('names',{'First':'char(50)',
                           'Last':'char(50)',
                           'Birth_Month':'int',
                           'Birth_Day':'int',
                           'Birth_Year':'int',})
    if len(tt) == 0:
        tt.append({'Birth_Day':21,'First':'Thomas','Last':'Hinkle'})               
        tt.extend([{'First':'John'},
                   {'First':'Susan'},
                   {'First':'David'},]
                  )
    import random
    for n in range(100):
        tt.append({'Birth_Day':random.randint(1,28),
                   'Birth_Month':random.randint(1,12),
                   'First':random.choice(['John','Harry','Bob','Lucy','Genevieve','Katharine','Susan']),
                   'Last':random.choice(['Hinkle','Sayre','Wilkins','Wright','Wilson']),
                   })
    for t in tt:
        print 'row:'
        for m in dir(t):
            print getattr(t,m)
    #psl.c.commit()

