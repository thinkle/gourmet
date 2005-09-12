import re, string
import sys
from parser_data import SUMMABLE_FIELDS

# Our basic module for interaction with our nutritional information DB

class NutritionData:

    """Handle all interactions with our nutrition database.

    We provide methods to set up equivalences between our
    ingredient-keys and our nutritional data.
    """
    
    def __init__ (self, db, conv):
        self.db = db
        self.conv = conv
        self.conv.density_table
        self.gramwght_regexp = re.compile("([0-9.]+)?( ?([^,]+))?(, (.*))?")

    def set_key (self, key, row):
        """Create an automatic equivalence for ingredient key 'key' and nutritional DB row ROW
        """        
        if not row: row = self._get_key(key)
        #density=self.get_density(key,row)
        if row: self.row.ndbno=row.ndbno
        else:
            self.db.naliasesview.append({'ndbno':row.ndbno,
                                         'ingkey':key})

    def set_key_from_ndbno (self, key, ndbno):
        """Create an automatic equivalence between ingredient key 'key' and ndbno
        ndbno is our nutritional database number."""
        self.db.naliasesview.append({'ndbno':ndbno,
                                 'ingkey':key})

    def set_conversion (self, key, unit, factor):
        """Set conversion for ingredient key.

        factor is the amount we multiply by to get from unit to grams.
        """
        if self.conv.unit_dict.has_key(unit):
            unit = self.conv.unit_dict[unit]
        self.db.nconversions.append(ingkey=key,unit=unit,factor=factor)

    def get_matches (self, key, max=50):
        """Handed a string, get a list of likley USDA database matches.

        We return a list of lists:
        [[description, nutritional-database-number],...]

        If max is not none, we cut our list off at max items (and hope our
        sorting algorithm succeeded in picking out the good matches!).
        """
        words=re.split("\W",key)
        words = filter(lambda w: w and not w in ['in','or','and','with'], words)
        if words:
            # match any of the words in our key
            regexp = "("+string.join(words,"|")+")" # match any of our words
            print 'Filtering nview -- %s items'%len(self.db.nview)
            nvw = self.db.search(self.db.nview,'desc',regexp)
            print 'Narrowed to %s items'%len(nvw)
            # create a list of rows and sort it, putting the most likely match first
            lst = [[r.desc,r.ndbno] for r in nvw]
            def sort_func (row1,row2):
                dsc1=row1[0].lower()
                dsc2=row2[0].lower()
                sc1=0
                sc2=0
                # we presume recipe keys start with important words and proceed to less
                # important ones -- so we give each word a descending value.
                # in i.e. milk, low fat, we get the points: milk (3), low (2), fat (1)
                score = len(words)
                for w in words:
                    w=w.lower()
                    if dsc1.find(w)>=0: sc1+=score
                    if dsc2.find(w)>=0: sc2+=score
                    score = score - 1
                if sc1<sc2:
                    return 1
                elif sc2<sc1:
                    return -1
                # otherwise, we assume a longer string is a worse match
                elif len(dsc1)>len(dsc2): return 1
                elif len(dsc2)>len(dsc1): return -1
                else: return 0
            print 'sorting list'
            lst.sort(sort_func)
            if max and len(lst) > max:
                # we cut down the list if it's too long
                # (so we hope our sorting algorhythm is doing
                # a good job!)
                lst = lst[0:max]
            return lst

    def _get_key (self, key):
        """Handed an ingredient key, get our nutritional Database equivalent
        if one exists."""
        #print 'key=',key
        rows=self.db.naliasesview.select({'ingkey':str(key)})
        if rows:
            return rows[0]
        else: return None

    def get_nutinfo_for_ing (self, ing):
        """A convenience function that grabs the requisite items from
        an ingredient."""
        print 'get info for ',ing.ingkey,ing.item,ing.unit,ing.amount
        if hasattr(ing,'rangeamount') and ing.rangeamount:
            # just average our amounts
            amount = (ing.rangeamount + ing.amount)/2
        else:
            amount = ing.amount
        if not amount: amount=1
        return self.get_nutinfo_for_item(ing.ingkey,amount,ing.unit)

    def get_nutinfo_for_inglist (self, inglist):
        """A convenience function to get NutritionInfoList for a list of
        ingredients.
        """
        return NutritionInfoList([self.get_nutinfo_for_ing(i) for i in inglist])

    def get_nutinfo_for_item (self, key, amt, unit):
        """Handed a key, amount and unit, get out nutritional Database object.
        """
        ni=self.get_nutinfo(key)        
        if ni:
            c=self.get_conversion_for_amt(amt,unit,key)
            if c:
                print 'returning info',ni,c
                return NutritionInfo(ni,mult=c)
        print 'returning vapor'
        return NutritionVapor(self,key,
                              rowref=ni,
                              amount=amt,
                              unit=unit)

    def get_nutinfo (self, key):
        """Get our nutritional information for ingredient key 'key'
        We return an object interfacing with our DB whose attributes
        will be nutritional values.
        """
        aliasrow = self._get_key(key)
        if aliasrow:
            nvrows=self.db.nview.select({'ndbno':aliasrow.ndbno})
            if len(nvrows)==1:
                return NutritionInfo(nvrows[0])
            elif len(nvrows)>1:
                raise "Too many rowd returned for ndbno %s"%aliasrow.ndbno
        # if we don't have a nutritional db row, return a
        # NutritionVapor instance which remembers our query and allows
        # us to redo it.  The idea here is that our callers will get
        # an object that can guarantee them the latest nutritional
        # information for a given item.
        return NutritionVapor(self,key)

    def get_conversion_for_amt (self, amt, unit, key, row=None):
        """Get a conversion for amount amt of unit 'unit' to USDA standard.

        Multiplying our standard numbers (/100g) will get us the appropriate
        calories, etc.

        get_conversion_for_amt(amt,unit,key) * 100 will give us the
        number of grams this AMOUNT converts to.
        """
        # our default is 100g
        cnv=self.conv.converter('g.',unit)
        if not row: row=self.get_nutinfo(key)
        if not cnv:
            cnv = self.conv.converter('g.',unit,
                                      density=self.get_density(key,row)
                                      )
        if not cnv:
            # lookup in our custom nutrition-related conversion table
            if self.conv.unit_dict.has_key(unit):
                unit = self.conv.unit_dict[unit]
            lookup = self.db.nconversions.select(ingkey=key,unit=unit)
            if lookup:
                print amt,unit,'cnv found in nconversions!'
                cnv = lookup[0].factor
        if cnv:
            #print 'returning conversion factory ',(.01*amt)/cnv
            return (0.01*amt)/cnv

    def get_conversions (self, key=None, row=None):
        """Handed an ingredient key or a row of the nutrition database,
        we return two dictionaries, one with Unit Conversions and the other
        with densities. Our return dictionaries look like this:
        ({'chopped':1.03, #density dic
          'melted':1.09},
         {'piece':27,
          'leg':48,} # unit : grams
          )"""
        if not row: row=self.get_nutinfo(key)
        if not row: return {},{}
        print 'working on row',row
        units = {}
        densities = {}
        for gd,gw in self.get_gramweights(row).items():
            a,u,e=gd
            if a:
                convfactor = self.conv.converter(u,'ml')
                if convfactor: #if we are a volume
                    # divide mass by volume converted to mililiters
                    # (since gramwts are in grams!)
                    density = float(gw) / (a * convfactor)
                    densities[e]=density
                    continue
            # if we can't get a density from this amount, we're going to treat it as a unit!
            if e: u = u + ", " + e
            if a: gw = float(gw)/a
            else:
                gw = float(gw)
            if u: units[u]=gw
        return densities,units
            
    def get_densities (self,key=None,row=None):
        """Handed key or nutrow, return dictionary with densities."""
        print 'get_densities handed :',key,',',row
        if not row: row = self._get_key(key)
        if not row: return None
        if self.conv.density_table.has_key(key):
            return {'':self.conv.density_table[key]}
        else:
            #print 'Calculating density'
            densities = {}            
            for gd,gw in self.get_gramweights(row).items():
                a,u,e = gd
                if not a:
                    continue
                convfactor=self.conv.converter(u,'ml')
                if convfactor: # if we are a volume
                    # divide mass by volume converted to milileters
                    # (gramwts are in grams)
                    #print gw,'/','(',a,'*',convfactor,')'
                    density = float(gw) / (a * convfactor)
                    #if e: print '(for ',e,')'
                    densities[e]=density
            return densities

    def get_gramweights (self,row):
        grm1 = self.parse_gramweight_measure(row.gramdsc1)
        grm2 = self.parse_gramweight_measure(row.gramdsc2)
        ret = {}
        if grm1:
            ret[grm1]=row.gramwt1
        if grm2:
            ret[grm2]=row.gramwt2
        return ret
    
    def get_density (self,key=None,row=None):
        densities = self.get_densities(key,row)
        print 'densities are ',densities
        if densities:
            if densities.has_key(None):
                self.conv.density_table[key]=densities[None]
                return densities[None]
            else:
                return self.choose_density(densities)

    def choose_density (self, densdic):
        # this will eventually query the user...
        #print "Choosing an arbitrary density..."
        return densdic.values()[0]

    def parse_gramweight_measure (self, txt):
        m=self.gramwght_regexp.match(txt)
        if m:
            groups=m.groups()
            amt = groups[0]
            if amt: amt = float(amt)
            unit = groups[2]
            extra = groups[4]
            return amt,unit,extra
                    
class NutritionInfo:
    """A multipliable way to reference an object.

    Any attribute of object that can be mutiplied, will be returned
    multiplied by mult.

    We can also support various mathematical operators
    n = NutritionInfo(obj, mult=2)
    n * 2 -> NutritionInfo(obj,mult=4)
    n2 = NutritionInfo(obj2, mult=3)
    n2 + n -> NutritionInfoList([n2,n])

    The result is that addition and multiplication 'makes sense' for
    properties. For example, if we have nutrition info for 1 carrot,
    we can multiply it or add it to the nutrition info for an
    eggplant. The resulting object will reflect the appropriate
    cumulative values.

    Carrot = NutritionInfo(CarrotNutritionRow)
    Eggplant = NutritionInfo(EggplantNutritionRow)

    Carrot.kcal => 41
    Eggplant.kcal => 24
    (Carrot + Eggplant).kcal => 65
    (Carrot * 3 + Eggplant).kcal => 147

    This will be true for all numeric properties.

    Non numeric properties return a somewhat not-useful string:
    
    (Carrot + Eggplant).desc => 'CARROTS,RAW, EGGPLANT,RAW'
    """
    def __init__ (self,rowref, mult=1):
        self.__rowref__ = rowref
        self.__mult__ = mult
        print 'NutritionInfo created->',self.desc,self.kcal

    def __getattr__ (self, attr):
        if attr[0]!='_':
            ret = getattr(self.__rowref__, attr)
            if attr in SUMMABLE_FIELDS:
                return ret * self.__mult__
            else:
                return ret
        else:
            # somehow this magically gets us standard
            # attribute handling...
            raise AttributeError, attr

    def __add__ (self, obj):
        if isinstance(obj,NutritionInfo):
            return NutritionInfoList([self,obj])
        elif isinstance(obj,NutritionInfoList):
            return NutritionInfoList([self]+obj.__nutinfos__)

    def __mul__ (self, n):
        return NutritionInfo(self.__rowref__, self.__mult__ * n)

KEY_VAPOR = 0 # when we don't have a key
UNIT_VAPOR = 1 # when we can't interpret the unit
DENSITY_VAPOR = 2 # when we don't have a density
AMOUNT_VAPOR = 3 # when there is no amount, leaving us quite confused

class NutritionVapor (NutritionInfo):
    """An object to hold our nutritional information before we know it.

    Basically, we have to behave like a NutritionInfo class that doesn't
    actually return any data.

    We also can return information about why we're still vapor
    (whether we need density info, key info or what...).
    """
    def __init__ (self, nd, key,
                  rowref=None,
                  mult=None,
                  amount=None,
                  unit=None,):
        self.__nd__ = nd
        self.__rowref__ = rowref
        self.__key__ = key
        self.__mult__ = mult
        self.__amt__ = amount
        self.__unit__ = unit

    def _reset (self):
        """Try to create matter from vapor and return it.

        If we fail we return more vapor."""
        if not self.__rowref__:
            if self.__mult__:
                ni = self.__nd__.get_nutinfo(self.__key__)
                if not isinstance(ni,NutritionVapor): return ni * self.__mult__
                else: return self
            else:
                return self.__nd__.get_nutinfo_for_item(self.__key__,
                                                        self.__amt__,
                                                        self.__unit__)
        elif self.__amt__:
            c=self.__nd__.get_conversion_for_amt(self.__amt__,self.__unit__,self.__key__)
            if c:
                self.__mult__ = c
                return NutritionInfo(self.__rowref__,
                                     self.mult)
            else:
                return self
        else: return self.__nd__.get_nutinfo_for_item(self.__key__,self.__amt__,self.__unit__)

    def __getattr__ (self,attr):
        """Return 0 for any requests for a non _ prefixed attribute."""
        if attr[0]!='_':
            return 0
        else:
            raise AttributeError,attr

    def __repr__ (self):
        return '<NutritionVapor %s>'%self.__key__
    
    def __nonzero__ (self):
        """Vapor is always False."""
        return False

    def _wheres_the_vapor (self):
        """Return a key as to why we're vapor."""
        if not self.__rowref__: return KEY_VAPOR
        elif not self.__amt__: return AMOUNT_VAPOR
        else: return UNIT_VAPOR
    
class NutritionInfoList (list, NutritionInfo):
    """A summable list of objects.

    When we ask for numeric attributes of our members, we get the sum.
    """
    def __init__ (self,nutinfos, mult=1):
        self.__nutinfos__ = nutinfos
        self.__len__ = self.__nutinfos__.__len__
        self.__getitem__ = self.__nutinfos__.__len__
        self.__mult__ = 1

    def __getattr__ (self, attr):
        if attr[0]!='_':
            alist = [getattr(ni,attr) for ni in self.__nutinfos__]
            if attr in SUMMABLE_FIELDS:
                if self.__mult__: alist = [n * self.__mult__ for n in alist]
                return sum(alist)
            else:
                return ", ".join(map(str,alist))
        else:
            # somehow this magically gets us standard
            # attribute handling...
            raise AttributeError, attr

    def _reset (self):
        """See if we can turn any of our vapor into matter."""
        for i in range(len(self.__nutinfos__)):
            obj = self.__nutinfos__[i]
            if isinstance(obj,NutritionVapor):
                # try resetting
                self.__nutinfos__[i]=obj._reset()

    def _get_vapor (self):
        """Return a list of nutritionVapor if there is any

        In other words, tell us whether we are missing any nutritional
        information."""
        ret = []
        for i in self.__nutinfos__:
            if isinstance(i,NutritionVapor): ret.append(i)
        return ret
        
    def __add__ (self, obj):
        if isinstance(obj,NutritionInfo):
            return NutritionInfoList(self.__nutinfos__ + [obj])
        elif isinstance(obj,NutritionInfoList):
            return NutritionInfoList(self.__nutinfos__ + obj.__nutinfos__)

    def __sub__ (self, obj):
        copy = self.__nutinfos__[0:]
        copy.remove(obj)
        return NutritionInfoList(copy)

    def __getslice__ (self, a, b):
        return NutritionInfoList(self.__nutinfos__[a:b])

    def __repr__ (self):
        return '<NutritionInfoList>'
            
if __name__ == '__main__':
    import sys
    sys.path.append('/usr/share/')
    import gourmet.recipeManager as rm
    #rm.dbargs['file']='/tmp/recipes.mk'
    db=rm.RecipeManager(**rm.dbargs)
    print db,rm.dbargs
    import gourmet.convert
    conv = gourmet.convert.converter()
    import nutritionGrabberGui
    nutritionGrabberGui.check_for_db(db)
    nd=NutritionData(db,conv)

def foo ():
    from gourmet import convert
    class SimpleInterface:
        
        def __init__ (self, nd):
            self.ACTIONS = {'Add ingredient':self.add_ingredient,
                       'Add key info':self.add_key,
                       'Print info':self.print_info,
                       'Exit' : self.exit
                       }
            self.nd = nd
            self.ings = []
            
        def run (self):
            choices = self.ACTIONS.keys()
            for n,a in enumerate(choices):
                print n,'. ',a
            choice = None
            while not choice:
                choice = raw_input('Enter number of choice: ')
                choice = int(choice)
                if choice < len(choices): choice = self.ACTIONS[choices[choice]]
                else: choice = None
            print 'Okay, here we go...'
            try:
                choice()
            except:
                print 'oops!'
                raise
            else:
                self.run()
                

        def add_ingredient (self):
            key=raw_input('Enter ingredient key: ')
            amt = convert.frac_to_float(raw_input('Enter amount: '))
            unit = raw_input('Enter unit: ')
            if not self.ings:
                self.ings = NutritionInfoList([self.nd.get_nutinfo_for_item(key,amt,unit)])
            else:
                self.ings = self.ings + self.nd.get_nutinfo_for_item(key,amt,unit)
            print 'Ingredients: ',self.ings

        def add_key (self):
            key=raw_input('Enter key for which we add info: ')
            matches = self.nd.get_matches(key,10)
            print "Choose an equivalent for ",key
            for n,m in enumerate(matches):
                print n,'. ',m[0]
            choice = None
            while not choice:
                choice = raw_input('Enter number of choice: ')
                choice = int(choice)
                if choice < len(matches): choice = matches[choice][1]
                else: choice = None
            self.nd.set_key_from_ndbno(key,choice)
            self.ings._reset()

        def print_info (self):
            att = raw_input('What information would you like (e.g. kcal): ')
            while not hasattr(self.ings,att):
                print "I'm sorry, there is no information about ",att
                att = raw_input('What information would you like (e.g. kcal): ')
            print att,":",getattr(self.ings,att)
            vv = self.ings._get_vapor()
            if vv:
                print '(but we have some vapor)'
                for v in vv:
                    explanation = v._wheres_the_vapor()
                    print 'Vapor for ',v.__key__
                    if explanation==KEY_VAPOR: print 'No key'
                    if explanation==UNIT_VAPOR: print "Can't handle unit ",v.__unit__
                    if explanation==AMOUNT_VAPOR: print "What am I to do with the amount ",v.__amt__
                

        def exit (self):
            import sys
            sys.exit()
    si = SimpleInterface(nd)
    si.run()
    #import random
    #fake_key = "0"
    #while raw_input('Get another density?'):
    #    row=random.choice(db.nview)
    #    print 'Information: ',row.desc, nd.get_conversions(row=row)
    #    #print 'Gramweights: ',nd.get_gramweights(row)
    #    #print 'Density of ',row.desc,' = ',nd.get_densities(row)
