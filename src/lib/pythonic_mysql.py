import PythonicSQL, threading
import MySQLdb
import _mysql_exceptions

class PythonicMySQL (PythonicSQL.PythonicSQL):
    def __init__ (self, host="localhost", user="", passwd="", db="recipe"):
        #print file
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        PythonicSQL.PythonicSQL.__init__(self,MySQLdb)

    def connect (self):
        c = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd)
        self._cursors[threading.currentThread()] = c.cursor()
        try:
            self.execute(['use %s'%self.db])
        except _mysql_exceptions.OperationalError:
            self.execute(['create database %s'%self.db])
            self.execute(['use %s'%self.db])
        return c

    def new_cursor (self):
        c = self.get_connection().cursor()
        c.execute('use %s'%self.db)
        return c

    def _check_for_table (self, name):
        return name in [x[0] for x in self.execute(['show tables;'])]

    def get_fields_for_table (self,name):
        return [x[0] for x in self.execute(['SHOW COLUMNS IN %s'%name])]

    def hone_type (self,typstring):
        if typstring in ['unicode','binary']: return 'blob'
        else: return typstring
