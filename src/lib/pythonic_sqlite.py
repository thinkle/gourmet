import PythonicSQL
import sqlite
from gdebug import debug

class PythonicSQLite (PythonicSQL.PythonicSQL):
    def __init__ (self, file):
        #print file
        self.file = file
        PythonicSQL.PythonicSQL.__init__(self,sqlite)

    def connect (self):
        # debugging code...
        import sys
        #logbase = os.path.join(tempfile.tempdir,"SQLITE_LOGFILE_GOURMET")
        #logfile = logbase + ".1"
        #if os.path.exists(logfile):
        #    num = logfile.split('.')[-1]
        # logfile = "%s.%s"%(logbase,int(num)+1)
        #logfi = open(logfile,'w')
        return sqlite.Connection(self.file, encoding='utf8',timeout=5000,autocommit=True,command_logfile=sys.stderr)

    def _check_for_table (self, name):
        return self.execute(['SELECT name FROM sqlite_master WHERE NAME=%s',name])

    def get_fields_for_table (self,name):
        allrows = self.execute(['SELECT sql FROM sqlite_master WHERE name=%s',name])
        statement = allrows[0][0]
        debug('get_fields_for_table, statement=%s'%statement,0)
        statements = statement[statement.find('(')+1:statement.rfind(')')].split(',')
        retval = [x.split()[0] for x in statements]
        debug("get_fields_for_table returning: %s"%retval,0)
        return retval
