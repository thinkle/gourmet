from gettext import gettext as _
import convert, shopping, os.path
import OptionParser
import gglobals
from gtk_extras import dialog_extras as de

# Follow commandline db specification if given
dbargs = {}

if not dbargs.has_key('file'):
    dbargs['file']=os.path.join(gglobals.gourmetdir,'recipes.db')
if OptionParser.options.db_url:
    print 'We have a db_url and it is,',OptionParser.options.db_url
    dbargs['custom_url'] = OptionParser.options.db_url
    

from backends.db import RecData, RecipeManager, dbDic

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
        if len(self.orgdic.items())==0:
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
        if len(self.pantry.items())==0:
            self.pantry.initialize(dict([(i,True) for i in self.default_pantry]))

class DatabaseConverter(convert.Converter):
    def __init__ (self, db):
        self.db = db
        convert.Converter.__init__(self)
    ## still need to finish this class and then
    ## replace calls to convert.Converter with
    ## calls to rmetakit.DatabaseConverter

    def create_conv_table (self):
        self.conv_table = dbDic('ckey','value',self.db.convtable_table, self.db)
        for k,v in defaults.CONVERTER_TABLE.items():
            if not self.conv_table.has_key(k):
                self.conv_table[k]=v

    def create_density_table (self):
        self.density_table = dbDic('dkey','value',
                                   self.db.density_table,self.db)
        for k,v in defaults.DENSITY_TABLE.items():
            if not self.density_table.has_key(k):
                self.density_table[k]=v

    def create_cross_unit_table (self):
        self.cross_unit_table=dbDic('cukey','value',self.db.crossunitdict_table,self.db)
        for k,v in defaults.CROSS_UNIT_TABLE:
            if not self.cross_unit_table.has_key(k):
                self.cross_unit_table[k]=v

    def create_unit_dict (self):
        self.units = defaults.UNITS
        self.unit_dict=dbDic('ukey','value',self.db.unitdict_table,self.db)
        for itm in self.units:
            key = itm[0]
            variations = itm[1]
            self.unit_dict[key] = key
            for v in variations:
                self.unit_dict[v] = key
                
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

