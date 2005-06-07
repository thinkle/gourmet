import re, string
import sys

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
        density=self.get_density(key,row)
        row = self._get_key(key)
        if row: self.row.nbdno=row.nbdno
        else:
            self.db.naliases.append({'nbdno':row.nbdno,
                                  'ingkey':key})

    def set_key_from_ndbno (self, key, nbdno):
        """Create an automatic equivalence between ingredient key 'key' and ndbno
        ndbno is our nutritional database number."""
        self.db.naliases.append({'nbdno':nbdno,
                                 'ingkey':key})

    def get_matches_for_string (self, key, max=50):
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
        rows=self.db.naliases.select({'ingkey':str(key)})
        if rows:
            return rows[0]
        else: return None

    def get_nut_from_key (self, key):
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
        # if we don't have a nutritional db row, return None
        return None

    def get_conversion_for_amt (self, amt, unit, key, row=None):
        """Get a conversion for amount amt of unit 'unit' to USDA standard.

        Multiplying our standard numbers (/100g) will get us the appropriate
        calories, etc.

        get_conversion_for_amt(amt,unit,key) * 100 will give us the
        number of grams this AMOUNT converts to.
        """
        
        # our default is 100g
        cnv=self.conv.converter('g.',unit)
        if not row: row=self.get_nut_from_key(key)
        if not cnv:
            cnv = self.conv.converter('g.',unit,
                                      density=self.get_density(key,row)
                                      )
        if cnv:
            #print 'returning conversion factory ',(.01*amt)/cnv
            return (0.01*amt)/cnv

    def convert_amount (self, amount, unit, density=None):
        cnv = self.conv.converter('g.',unit)
        if not cnv:
            print 'using density ',density
            cnv = self.conv.converter('g.',unit,density=density)
        if cnv:
            return (0.01*amount)/cnv
        
    def get_conversions (self, key=None, row=None):
        """Handed an ingredient key or a row of the nutrition database,
        we return two dictionaries, one with Unit Conversions and the other
        with densities. Our return dictionaries look like this:
        ({'chopped':1.03, #density dic
          'melted':1.09},
         {'piece':27,
          'leg':48,} # unit : grams
          )"""
        if not row: row=self.get_nut_from_key(key)
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
        if not row: row = self._get_key(key)
        if not row: return None
        if self.conv.density_table.has_key(key):
            return self.conv.density_table[key]
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
    
    (Carrot + Eggplant).desc => "CARROTS,RAW, EGGPLANT,RAW"
    """
    def __init__ (self,rowref, mult=1):
        self.__rowref__ = rowref
        self.__mult__ = mult

    def __getattr__ (self, attr):
        if attr[0]!='_':
            ret = getattr(self.__rowref__, attr)
            if type(ret)==float:
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
        return NutritionInfo(self.__rowref__, n)
        
class NutritionInfoList (list, NutritionInfo):
    """A summable list of objects.

    When we ask for numeric attributes of our members, we get the sum.
    """
    def __init__ (self,nutinfos, mult=1):
        self.__nutinfos__ = nutinfos
        self.__mult__ = 1

    def __getattr__ (self, attr):
        if attr[0]!='_':
            alist = [getattr(ni,attr) for ni in self.__nutinfos__]
            try:
                if alist and type(alist[0])==float:
                    if self.__mult__: alist = [n * self.__mult__ for n in alist]
                    return sum(alist)
            except:
                return ", ".join(map(str,alist))
        else:
            # somehow this magically gets us standard
            # attribute handling...
            raise AttributeError, attr

    def __add__ (self, obj):
        if isinstance(obj,NutritionInfo):
            return NutritionInfoList(self.__nutinfos__ + [obj])
        elif isinstance(obj,NutritionInfoList):
            return NutritionInfoList(self.__nutinfos__ + obj.__nutinfos__)

    def __sub__ (self, obj):
        copy = self.__nutinfos__[0:]
        copy.remove(obj)
        return NutritionInfoList(copy)
            
if __name__ == '__main__':
    import sys
    sys.path.append('/usr/share/')
    import gourmet.recipeManager as rm
    rm.dbargs['file']='/tmp/recipes.mk'
    db=rm.RecipeManager(**rm.dbargs)
    import gourmet.convert
    conv = gourmet.convert.converter()
    import nutritionGrabberGui
    nutritionGrabberGui.check_for_db(db)
    nd=NutritionData(db,conv)
    import random
    fake_key = "0"
    while raw_input('Get another density?'):
        row=random.choice(db.nview)
        print 'Information: ',row.desc, nd.get_conversions(row=row)
        #print 'Gramweights: ',nd.get_gramweights(row)
        #print 'Density of ',row.desc,' = ',nd.get_densities(row)
