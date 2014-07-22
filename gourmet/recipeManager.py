import convert, shopping, os.path
from OptionParser import args
import gglobals
from gtk_extras import dialog_extras as de

from models import Pantry, ShopCat, ShopCatOrder

# Follow commandline db specification if given
dbargs = {}

if not dbargs.has_key('file'):
    dbargs['file']=os.path.join(gglobals.gourmetdir,'recipes.db')
if args.db_url:
    print 'We have a db_url and it is,',args.db_url
    dbargs['custom_url'] = args.db_url
    

from backends.db import RecData, RecipeManager

class DatabaseShopper (shopping.Shopper):
    """We are a Shopper class that conveniently saves our key dictionaries
    in our database"""
    def __init__ (self, lst, session, conv=None):
        self.session = session
        self.cnv = conv
        shopping.Shopper.__init__(self,lst)

    def init_converter (self):
        #self.cnv = DatabaseConverter(self.db)
        if not self.cnv:
            self.cnv = convert.get_converter()
    
    def init_orgdic (self):
        self.orgdic = self.session.query(ShopCat.ingkey, ShopCat.shopcategory).all()
        if len(self.orgdic)==0:
            for key, shop in shopping.setup_default_orgdic().items():
                self.session.add(ShopCat(ingkey=key, shopcategory=shop))
            self.session.commit()
            self.orgdic = self.session.query(ShopCat.ingkey, ShopCat.shopcategory).all()

    def init_ingorder_dic (self):
        self.ingorder_dic = self.session.query(ShopCat.ingkey, ShopCat.position).all()

    def init_catorder_dic (self):
        self.catorder_dic = self.session.query(ShopCatOrder.shopcategory, ShopCatOrder.position).all()

    def init_pantry (self):
        self.pantry = self.session.query(Pantry.ingkey, Pantry.pantry).all()
        if len(self.pantry)==0:
            for i in self.default_pantry:
                self.session.add(Pantry(ingkey=unicode(i), pantry=True))
            self.session.commit()
            self.pantry = self.session.query(Pantry.ingkey, Pantry.pantry).all()

# A simple CLI for mucking about our DB without firing up gourmet proper
class SimpleCLI:
    def __init__  (self, rmclass=None, rmargs=None):
        if not rmclass: self.rmclass=RecipeManager
        else: self.rmclass = rmclass
        if not rmargs: self.args=dbargs
        else: self.args=rmargs
        self.rm = self.rmclass(**self.args)

    def __call__ (self):
        print """Welcome to GRM's handy debugging interface straight to our database.
        You are now in the midst of our caller class. You can access your recipeManager
        class through self.rm.

        One major limitation: You can only execute a single expression
        at a time (i.e. what you you could put in a lambda expression).
        """
        while True:
            inp = raw_input('GRM>')
            if inp == 'quit' or inp == '' or inp == '':
                break
            else:                    
                try:
                    print 'result: %s'%eval(inp)
                except:
                    print 'invalid input.'

def get_recipe_manager (**args):
    if not args: args = dbargs
    try:
        return RecipeManager(**args)
    except RecData,rd:
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

