from gettext import gettext as _
import convert, shopping, os.path
import OptionParser
import gglobals
import dialog_extras as de

db=gglobals.db
dbargs = gglobals.dbargs

# Follow commandline db specification if given

if db=='mysql' and not dbargs.has_key('pw'):
    dbargs['pw']=de.getEntry(
        label=_('Enter Password'),
        sublabel=_('Please enter your password for user %s of the MySQL database at host %s'%(dbargs['user'],
                                                                                              dbargs['host'])
                   ),
        entryLabel=_('Password: '),
        visibility=False,
        )
    
# otherwise, default to metakit; fallback to sqlite

#db = 'mysql'
#db='sqlite'
if db == 'sqlite' and not dbargs.has_key('file'):
    dbargs['file']=os.path.join(gglobals.gourmetdir,'recipes.db')
elif db == 'metakit' and not dbargs.has_key('file'):
    dbargs['file']=os.path.join(gglobals.gourmetdir,'recipes.mk')

if not db:
    try:
        from backends.rmetakit import *
    except ImportError:
        from backends.rsqlite import *
elif db=='metakit':
    from backends.rmetakit import *
elif db=='sqlite':
    from backends.rsqlite import *
elif db=='mysql':
    from backends.rmysql import *
    
class mkShopper (shopping.shopper):
    """We are a shopper class that conveniently saves our key dictionaries
    in our metakit database"""
    def __init__ (self, lst, db, conv=None):
        self.db = db
        self.cnv = conv
        shopping.shopper.__init__(self,lst)

    def init_converter (self):
        #self.cnv = mkConverter(self.db)
        if not self.cnv:
            self.cnv = convert.converter()
    
    def init_orgdic (self):
        self.orgdic = dbDic('shopkey','category',self.db.sview,db=self.db)
        if len(self.orgdic.items())==0:
            dic = shopping.setup_default_orgdic()
            for k,v in dic.items():
                self.orgdic[k]=v

    def init_ingorder_dic (self):
        self.ingorder_dic = dbDic('shopkey','position',self.db.sview,db=self.db)

    def init_catorder_dic (self):
        self.catorder_dic = dbDic('category','position',self.db.scview,db=self.db)

    def init_pantry (self):
        self.pantry = dbDic('itm','pantry',self.db.pview,db=self.db)
        if len(self.pantry.items())==0:
            for i in self.default_pantry:
                self.pantry[i]=True

    
class mkConverter(convert.converter):
    def __init__ (self, db):
        self.db = db
        convert.converter.__init__(self)
    ## still need to finish this class and then
    ## replace calls to convert.converter with
    ## calls to rmetakit.mkConverter

    def create_conv_table (self):
        self.conv_table = dbDic('ckey','value',self.db.cview, self.db,
                                pickle_key=True)
        for k,v in defaults.CONVERTER_TABLE.items():
            if not self.conv_table.has_key(k):
                self.conv_table[k]=v

    def create_density_table (self):
        self.density_table = dbDic('dkey','value',
                                   self.db.cdview,self.db)
        for k,v in defaults.DENSITY_TABLE.items():
            if not self.density_table.has_key(k):
                self.density_table[k]=v

    def create_cross_unit_table (self):
        self.cross_unit_table=dbDic('cukey','value',self.db.cuview,self.db)
        for k,v in defaults.CROSS_UNIT_TABLE:
            if not self.cross_unit_table.has_key(k):
                self.cross_unit_table[k]=v

    def create_unit_dict (self):
        self.units = defaults.UNITS
        self.unit_dict=dbDic('ukey','value',self.db.uview,self.db)
        for itm in self.units:
            key = itm[0]
            variations = itm[1]
            self.unit_dict[key] = key
            for v in variations:
                self.unit_dict[v] = key
                
