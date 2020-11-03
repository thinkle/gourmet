import re
import string
import sys

from .parser_data import SUMMABLE_FIELDS

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
        self.wght_breaker = re.compile(r'([^ ,]+)([, ]+\(?(.*)\)?)?$')

    def set_key (self, key, row):
        """Create an automatic equivalence for ingredient key 'key' and nutritional DB row ROW
        """
        if not row: row = self._get_key(key)
        #density=self.get_density(key,row)
        if row: self.row.ndbno=row.ndbno
        else:
            self.db.do_add(self.db.nutritionaliases_table,
                           {'ndbno':row.ndbno,
                            'ingkey':key})

    def set_density_for_key (self, key, density_equivalent):
        self.db.update_by_criteria(
            self.db.nutritionaliases_table,
            {'ingkey':key},
            {'density_equivalent':density_equivalent}
            )

    def set_key_from_ndbno (self, key, ndbno):
        """Create an automatic equivalence between ingredient key 'key' and ndbno
        ndbno is our nutritional database number."""
        if not isinstance(ndbno, int):
            ndbno = int(ndbno)
        prev_association = self.db.fetch_one(self.db.nutritionaliases_table,ingkey=key)
        if prev_association:
            self.db.do_modify(self.db.nutritionaliases_table,
                              prev_association,
                              {'ndbno':ndbno},
                              "ingkey")
        else:
            self.db.do_add(self.db.nutritionaliases_table,{'ndbno':ndbno,
                                                 'ingkey':key}
                           )

    def set_conversion (self, key, unit, factor):
        """Set conversion for ingredient key.

        factor is the amount we multiply by to get from unit to grams.
        """
        if unit in self.conv.unit_dict:
            unit = self.conv.unit_dict[unit]
        prev_entry = self.db.fetch_one(self.db.nutritionconversions_table,
                                       **{'ingkey':key,'unit':unit})
        if prev_entry:
            self.db.do_modify(self.db.nutritionconversions_table,
                               prev_entry,
                               {'factor':factor})
        else:
            self.db.do_add(self.db.nutritionconversions_table,{'ingkey':key,'unit':unit,'factor':factor})

    def get_matches (self, key, max=50):
        """Handed a string, get a list of likely USDA database matches.

        We return a list of lists:
        [[description, nutritional-database-number],...]

        If max is not none, we cut our list off at max items (and hope our
        sorting algorithm succeeded in picking out the good matches!).
        """
        words=re.split(r"\W",key)
        words = [w for w in words if w and not w in ['in','or','and','with']]
        #words += ['raw']
        result =  self.db.search_nutrition(words)
        while not result and len(words)>1:
            words = words[:-1]
            result = self.db.search_nutrition(words)
        if result:
            return [(r.desc,r.ndbno) for r in result]
        else:
            return []

    def _get_key (self, key):
        """Handed an ingredient key, get our nutritional Database equivalent
        if one exists."""
        row=self.db.fetch_one(self.db.nutritionaliases_table,**{'ingkey':str(key)})
        return row

    def get_nutinfo_for_ing (self, ing, rd, multiplier=None):
        """A convenience function that grabs the requisite items from
        an ingredient."""
        if hasattr(ing,'refid') and ing.refid:
            subrec = rd.get_referenced_rec(ing)
            return self.get_nutinfo_for_inglist(rd.get_ings(subrec),rd,ingObject=ing,multiplier=ing.amount)
        if hasattr(ing,'rangeamount') and ing.rangeamount:
            # just average our amounts
            try:
                amount = (ing.rangeamount + ing.amount)/2
            except TypeError:
                print('Failed trying to add',ing.rangeamount,ing.amount)
                raise
        else:
            amount = ing.amount
        if not amount: amount=1
        if multiplier: amount = amount * multiplier
        return  self.get_nutinfo_for_item(ing.ingkey,amount,ing.unit,ingObject=ing)

    def get_nutinfo_for_inglist (self, inglist, rd, ingObject=None, multiplier=None):
        """A convenience function to get NutritionInfoList for a list of
        ingredients.
        """
        return NutritionInfoList([self.get_nutinfo_for_ing(i,rd, multiplier) for i in inglist],
                                 ingObject=ingObject)

    def get_nutinfo_for_item (self, key, amt, unit, ingObject=None):
        """Handed a key, amount and unit, get out nutritional Database object.
        """
        ni=self.get_nutinfo(key)
        if not amt:
            amt = 1
        if ni: # We *can* have conversions w/ no units!
            c=self.get_conversion_for_amt(amt,unit,key=key,row=ni.__rowref__)
            if c:
                return NutritionInfo(ni,mult=c,ingObject=ingObject)
        return NutritionVapor(self,key,
                              rowref=ni,
                              amount=amt,
                              unit=unit,
                              ingObject=ingObject)

    def get_nutinfo_from_desc (self, desc):
        nvrow = self.db.fetch_one(self.db.nutrition_table,**{'desc':desc})
        if nvrow:
            return NutritionInfo(nvrow)
        else:
            matches = self.get_matches(desc)
            if len(matches) == 1:
                ndbno = matches[0][1]
                nvrow = self.db.fetch_one(self.db.nutrition_table,ndbno=ndbno)
                return NutritionInfo(nvrow)
        return None

    def get_nutinfo (self, key):
        """Get our nutritional information for ingredient key 'key'
        We return an object interfacing with our DB whose attributes
        will be nutritional values.
        """
        aliasrow = self._get_key(key)
        if aliasrow:
            nvrow=self.db.fetch_one(self.db.nutrition_table,**{'ndbno':aliasrow.ndbno})
            if nvrow: return NutritionInfo(nvrow)
        else:
            # See if the key happens to match an existing description...
            ni = self.get_nutinfo_from_desc(key)
            # if we don't have a nutritional db row, return a
            # NutritionVapor instance which remembers our query and allows
            # us to redo it.  The idea here is that our callers will get
            # an object that can guarantee them the latest nutritional
            # information for a given item.
            if ni:
                return ni
            return NutritionVapor(self,key)

    def get_ndbno (self, key):
        aliasrow = self._get_key(key)
        if aliasrow: return aliasrow.ndbno
        else: return None

    def convert_to_grams (self, amt, unit, key, row=None):
        conv = self.get_conversion_for_amt(amt,unit,key,row)
        if conv: return conv*100
        else:
            return None

    def get_conversion_for_amt (self, amt, unit, key, row=None, fudge=True):
        """Get a conversion for amount amt of unit 'unit' to USDA standard.

        Multiplying our standard numbers (/100g) will get us the appropriate
        calories, etc.

        get_conversion_for_amt(amt,unit,key) * 100 will give us the
        number of grams this AMOUNT converts to.
        """
        if not unit: unit = ''
        densities,gramweights = self.get_conversions(key,row)
        if unit in gramweights:
            mass = gramweights[unit] * amt
            return mass * 0.01
        # Otherwise, we are trying to find our density...
        cnv = None
        if (',' in unit) or ('(' in unit): # Check for density in unit description...
            print('Checking for density in unit...','densities=',densities)
            if ',' in unit:
                unit,description = unit.split(',')
            if '(' in unit:
                unit,description = unit.split('(')
                description = description.strip(')')
            description = description.strip()
            unit = unit.strip()
            print('description=',description)
            if description in densities:
                print('We got a density!','unit=',unit)
                density = densities[description]
                print(density,type(density),'(unit=',unit,')')
                cnv = self.conv.converter('g.',unit,density=density)
                print('We got a conversion!',cnv)
        # our default is 100g
        if not cnv:
            # Check for convertible mass...
            cnv=self.conv.converter('g',unit)
        if not cnv:
            # Check for density through key information...
            if not row: row=self.get_nutinfo(key)
            cnv = self.conv.converter('g',unit,
                                      density=self.get_density(key,row,fudge=fudge)
                                      )
        if not cnv:
            # lookup in our custom nutrition-related conversion table
            if unit in self.conv.unit_dict:
                unit = self.conv.unit_dict[unit]
            elif not unit:
                unit = ''
            lookup = self.db.fetch_one(self.db.nutritionconversions_table,ingkey=key,unit=unit)
            if lookup:
                cnv = lookup.factor
            else:
                # otherwise, cycle through any units we have and see
                # if we can get a conversion via those units...
                for conv in self.db.fetch_all(self.db.nutritionconversions_table,ingkey=key):
                    factor = self.conv.converter(unit,conv.unit)
                    if factor:
                        cnv = conv.factor*factor
        if cnv:
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
        units = {}
        densities = {}
        for gd,gw in list(self.get_gramweights(row).items()):
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
        if not row: return {}
        if key in self.conv.density_table:
            return {'':self.conv.density_table[key]}
        else:
            densities = {}
            for gd,gw in list(self.get_gramweights(row).items()):
                a,u,e = gd
                if not a:
                    continue
                convfactor=self.conv.converter(u,'ml')
                if convfactor: # if we are a volume
                    # divide mass by volume converted to milileters
                    # (gramwts are in grams)
                    density = float(gw) / (a * convfactor)
                    densities[e]=density
            return densities

    def get_gramweights (self,row):
        """Return a dictionary with gram weights.
        """
        ret = {}
        nutweights = self.db.fetch_all(self.db.usda_weights_table,**{'ndbno':row.ndbno})
        for nw in nutweights:
            mtch = self.wght_breaker.match(nw.unit)
            if not mtch:
                unit = nw.unit
                extra = None
            else:
                unit = mtch.groups()[0]
                extra = mtch.groups()[2]
            ret[(nw.amount,unit,extra)]=nw.gramwt
        return ret

    def get_density (self,key=None,row=None, fudge=True):
        densities = self.get_densities(key,row)
        if '' in densities: densities[None]=densities['']
        if key: keyrow=self._get_key(key)
        if densities:
            if key and keyrow and keyrow.density_equivalent and keyrow.density_equivalent in densities:
                return densities[keyrow.density_equivalent]
            elif None in densities:
                self.conv.density_table[key]=densities[None]
                return densities[None]
            elif len(densities)==1:
                return list(densities.values())[0]
            elif fudge:
                return sum(densities.values())/len(densities)
            else:
                return None

    def parse_gramweight_measure (self, txt):
        m=self.gramwght_regexp.match(txt)
        if m:
            groups=m.groups()
            amt = groups[0]
            if amt: amt = float(amt)
            unit = groups[2]
            extra = groups[4]
            return amt,unit,extra

    def add_custom_nutrition_info (self, nutrition_dictionary):
        """Add custom nutritional information."""
        #new_ndbno = self.db.increment_field(self.db.nutrition_table,'ndbno')
        #if new_ndbno: nutrition_dictionary['ndbno']=new_ndbno
        return self.db.do_add_nutrition(nutrition_dictionary).ndbno


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
    def __init__ (self,rowref, mult=1, fudged=False, ingObject=None):
        self.__rowref__ = rowref
        self.__mult__ = mult
        self.__fudged__ = fudged
        self.__ingobject__ = ingObject

    def __getattr__ (self, attr):
        if attr[0]!='_':
            ret = getattr(self.__rowref__, attr)
            try:
                if attr in SUMMABLE_FIELDS:
                    return (ret or 0) * self.__mult__
                else:
                    return ret
            except:
                raise
        else:
            # somehow this magically gets us standard
            # attribute handling...
            raise AttributeError(attr)

    def __add__ (self, obj):
        if isinstance(obj,NutritionInfo):
            return NutritionInfoList([self,obj])
        elif isinstance(obj,NutritionInfoList):
            return NutritionInfoList([self]+obj.__nutinfos__)

    def __mul__ (self, n):
        return NutritionInfo(self.__rowref__, mult=self.__mult__ * n,
                             fudged=self.__fudged__,ingObject=self.__ingobject__)

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
                  unit=None,
                  ingObject=None):
        self.__nd__ = nd
        self.__rowref__ = rowref
        self.__key__ = key
        self.__mult__ = mult
        self.__amt__ = amount
        self.__unit__ = unit
        self.__ingobject__ = ingObject

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
                                                        self.__unit__,
                                                        ingObject=self.__ingobject__
                                                        )
        elif self.__amt__:
            c=self.__nd__.get_conversion_for_amt(self.__amt__,self.__unit__,self.__key__,fudge=False)
            if c:
                self.__mult__ = c
                return NutritionInfo(self.__rowref__,
                                     self.__mult__)
            else:
                c=self.__nd__.get_conversion_for_amt(self.__amt__,self.__unit__,self.__key__,fudge=True)
                if c:
                    self.__mult__ = c
                    return NutritionInfo(self.__rowref__,
                                         self.__mult__,
                                         ingObject=self.__ingobject__
                                         )
                else:
                    return self
        else: return self.__nd__.get_nutinfo_for_item(self.__key__,self.__amt__,self.__unit__,ingObject=self.__ingobject__)

    def __getattr__ (self,attr):
        """Return 0 for any requests for a non _ prefixed attribute."""
        if attr[0]!='_':
            return 0
        else:
            raise AttributeError(attr)

    def __repr__ (self):
        return '<NutritionVapor %s>'%self.__key__

    def __bool__ (self):
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
    def __init__ (self,nutinfos, mult=1,ingObject=None):
        self.__nutinfos__ = nutinfos
        #self.__len__ = self.__nutinfos__.__len__
        #self.__getitem__ = self.__nutinfos__.__getitem__
        self.__mult__ = 1
        self.__ingobject__ = ingObject

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
            raise AttributeError(attr)

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
            if isinstance(i,NutritionInfoList):
                ret.extend(i._get_vapor())
        return ret

    def _get_fudge (self):
        """Return a list of fudged items
        """
        ret = []
        for i in self.__nutinfos__:
            if hasattr(i,'__fudged__') and i.__fudged__:
                ret.append(i)
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

    def __len__ (self): return len(self.__nutinfos__)
    def __getitem__ (self,x): return self.__nutinfos__[x]

    def __repr__ (self):
        return '<NutritionInfoList>'

    def __iter__ (self):
        for i in self.__nutinfos__: yield i

    def recursive_length (self):
        """Return number of contained nutrition info objects, recursing any embedded lists.
        """
        n = 0
        for x in range(len(self)):
            obj = self[x]
            if isinstance(obj,NutritionInfoList):
                n += obj.recursive_length()
            else:
                n += 1
        return n

if __name__ == '__main__':
    import gourmet.recipeManager as rm
    db=rm.RecipeManager(**rm.dbargs)
    import gourmet.convert
    conv = gourmet.convert.converter()
    from . import nutritionGrabberGui
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
            choices = list(self.ACTIONS.keys())
            for n,a in enumerate(choices):
                print(n,a)
            choice = None
            while not choice:
                choice = input('Enter number of choice: ')
                choice = int(choice)
                if choice < len(choices): choice = self.ACTIONS[choices[choice]]
                else: choice = None
            try:
                choice()
            except:
                raise
            else:
                self.run()


        def add_ingredient (self):
            key=input('Enter ingredient key: ')
            amt = convert.frac_to_float(input('Enter amount: '))
            unit = input('Enter unit: ')
            if not self.ings:
                self.ings = NutritionInfoList([self.nd.get_nutinfo_for_item(key,amt,unit)])
            else:
                self.ings = self.ings + self.nd.get_nutinfo_for_item(key,amt,unit)

        def add_key (self):
            key=input('Enter key for which we add info: ')
            matches = self.nd.get_matches(key,10)
            for n,m in enumerate(matches):
                print(n,'. ',m[0])
            choice = None
            while not choice:
                choice = input('Enter number of choice: ')
                choice = int(choice)
                if choice < len(matches): choice = matches[choice][1]
                else: choice = None
            self.nd.set_key_from_ndbno(key,choice)
            self.ings._reset()

        def print_info (self):
            att = input('What information would you like (e.g. kcal): ')
            while not hasattr(self.ings,att):
                print("I'm sorry, there is no information about ",att)
                att = input('What information would you like (e.g. kcal): ')
            print(att,":",getattr(self.ings,att))
            vv = self.ings._get_vapor()
            if vv:
                for v in vv:
                    explanation = v._wheres_the_vapor()
                    if explanation==KEY_VAPOR: print('No key')
                    if explanation==UNIT_VAPOR: print("Can't handle unit ",v.__unit__)
                    if explanation==AMOUNT_VAPOR: print("What am I to do with the amount ",v.__amt__)


        def exit (self):
            import sys
            sys.exit()
    si = SimpleInterface(nd)
    si.run()
    #import random
    #fake_key = "0"
    #while raw_input('Get another density?'):
    #    row=random.choice(db.nutrition_table)
    #    print 'Information: ',row.desc, nd.get_conversions(row=row)
    #    #print 'Gramweights: ',nd.get_gramweights(row)
    #    #print 'Density of ',row.desc,' = ',nd.get_densities(row)
