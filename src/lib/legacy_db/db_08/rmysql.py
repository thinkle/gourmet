import rsqlite, rdatabase, os.path
from gourmet import gglobals
from rsqlite import dbDic
import pythonic_mysql

class RecData (pythonic_mysql.PythonicMySQL,rsqlite.RecData):
    def __init__ (self, host="symmys", user="tom", pw="mssnurt89", db="recipe"):
        print 'rmysql.RecData'
        self.user = user
        self.host = host
        self.passwd = pw
        self.db = db
        rdatabase.RecData.__init__(self)

    def initialize_connection (self):
        pythonic_mysql.PythonicMySQL.__init__(self,self.host,self.user,self.passwd,self.db)

    def save (self):
        pass

class RecipeManager (RecData,rdatabase.RecipeManager):
    def __init__ (self, host="symmys", user="tom", pw="mssnurt89", db="recipe"):
        RecData.__init__(self,host,user,pw,db)
        rdatabase.RecipeManager.__init__(self)

