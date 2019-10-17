from gettext import gettext as _
import os.path
from gourmet import convert
from gourmet import shopping
from .OptionParser import args
from . import gglobals
from .gtk_extras import dialog_extras as de

# Follow commandline db specification if given
dbargs = {}

if 'file' not in dbargs:
    dbargs['file']=os.path.join(gglobals.gourmetdir,'recipes.db')
if args.db_url:
    print('We have a db_url and it is,',args.db_url)
    dbargs['custom_url'] = args.db_url


from .backends.db import RecData, RecipeManager, dbDic

class DatabaseShopper (shopping.Shopper):
    """We are a Shopper class that conveniently saves our key dictionaries
    in our database"""
    def __init__ (self, lst, db, conv=None):
        self.db = db
        self.cnv = conv
        shopping.Shopper.__init__(self,lst)

    def init_converter (self):
        #self.cnv = DatabaseConverter(self.db)
        if not self.cnv:
            self.cnv = convert.get_converter()

    def init_orgdic (self):
        self.orgdic = dbDic('ingkey','shopcategory',self.db.shopcats_table,db=self.db)
        if len(list(self.orgdic.items()))==0:
            dic = shopping.setup_default_orgdic()
            self.orgdic.initialize(dic)

    def init_ingorder_dic (self):
        self.ingorder_dic = dbDic('ingkey','position',self.db.shopcats_table,db=self.db)

    def init_catorder_dic (self):
        self.catorder_dic = dbDic('shopcategory',
                                  'position',
                                  self.db.shopcatsorder_table,
                                  db=self.db)

    def init_pantry (self):
        self.pantry = dbDic('ingkey','pantry',self.db.pantry_table,db=self.db)
        if len(list(self.pantry.items()))==0:
            self.pantry.initialize(dict([(i,True) for i in self.default_pantry]))

# A simple CLI for mucking about our DB without firing up gourmet proper
class SimpleCLI:
    def __init__  (self, rmclass=None, rmargs=None):
        if not rmclass: self.rmclass=RecipeManager
        else: self.rmclass = rmclass
        if not rmargs: self.args=dbargs
        else: self.args=rmargs
        self.rm = self.rmclass(**self.args)

    def __call__ (self):
        print("""Welcome to GRM's handy debugging interface straight to our database.
        You are now in the midst of our caller class. You can access your recipeManager
        class through self.rm.

        One major limitation: You can only execute a single expression
        at a time (i.e. what you you could put in a lambda expression).
        """)
        while True:
            inp = input('GRM>')
            if inp == 'quit' or inp == '' or inp == '':
                break
            else:
                try:
                    print('result: %s'%eval(inp))
                except:
                    print('invalid input.')

def get_recipe_manager (**args):
    if not args: args = dbargs
    try:
        return RecipeManager(**args)
    except RecData as rd:
        return rd

def default_rec_manager ():
    return get_recipe_manager(**dbargs)
    #try:
    #    return RecipeManager(**dbargs)
    #except RecData,rd:
    #    return rd


if __name__ == '__main__':
    #rm = RecipeManager(**dbargs)
    rm = RecipeManager(file='/tmp/0112/recipes.db')
    #s=SimpleCLI()
    #s()
