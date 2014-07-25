import re, string
import sys

from sqlalchemy.orm.exc import NoResultFound

from models import Nutrition, NutritionAlias, NutritionConversion, UsdaWeight

# Our basic module for interaction with our nutritional information DB

class NutritionData:

    """Handle all interactions with our nutrition database.

    We provide methods to set up equivalences between our
    ingredient-keys and our nutritional data.
    """
    
    def __init__ (self, session, conv):
        self.session = session
        self.conv = conv
        self.conv.density_table
        self.gramwght_regexp = re.compile("([0-9.]+)?( ?([^,]+))?(, (.*))?")
        self.wght_breaker = re.compile('([^ ,]+)([, ]+\(?(.*)\)?)?$')

    def set_key (self, key, row):
        """Create an automatic equivalence for ingredient key 'key' and nutritional DB row ROW
        """        
        if not row: row = self._get_key(key)
        #density=self.get_density(key,row)
        if row: self.row.ndbno=row.ndbno
        else:
            self.session.add(NutritionAlias(ndbno=row.ndbno, ingkey=key))
            self.session.commit()

    def set_density_for_key (self, key, density_equivalent):
        self.session.query(NutritionAlias).filter_by(ingkey=key).one().\
            density_equivalent=density_equivalent
        self.session.commit()

    def set_key_from_ndbno (self, key, ndbno):
        """Create an automatic equivalence between ingredient key 'key' and ndbno
        ndbno is our nutritional database number."""
        if type(ndbno)!=int:
            ndbno = int(ndbno)

        try:
            prev_association = self.session.query(NutritionAlias).filter_by(ingkey=key).one()
        except NoResultFound:
            self.session.add(NutritionAlias(ndbno=ndbno, ingkey=key))
        else:
            prev_association.ndbno = ndbno
        finally:
            self.session.commit()

    def set_conversion (self, key, unit, factor):
        """Set conversion for ingredient key.

        factor is the amount we multiply by to get from unit to grams.
        """
        if self.conv.unit_dict.has_key(unit):
            unit = self.conv.unit_dict[unit]

        try:
            prev_entry = self.session.query(NutritionConversion).filter_by(ingkey=key, unit=unit).one()
        except NoResultFound:
            self.session.add(NutritionConversion(ingkey=key, unit=unit, factor=factor))
        else:
            prev_entry.factor = factor
        finally:
            self.session.commit()

    def get_matches (self, key, max=50):
        """Handed a string, get a list of likely USDA database matches.

        We return a list of lists:
        [[description, nutritional-database-number],...]

        If max is not none, we cut our list off at max items (and hope our
        sorting algorithm succeeded in picking out the good matches!).
        """
        words=re.split("\W",key)
        words = filter(lambda w: w and not w in ['in','or','and','with'], words)
        #words += ['raw']
        result = self.session.query(Nutrition).filter(*[Nutrition.desc.like('%%%s%%'%w) for w in words]).all()
        while not result and len(words)>1:
            words = words[:-1]
            result = self.session.query(Nutrition).filter(*[Nutrition.desc.like('%%%s%%'%w) for w in words]).all()
        if result:
            return [(r.desc,r.ndbno) for r in result]
        else:
            return []
            
    def _get_key (self, key):
        """Handed an ingredient key, get our nutritional Database equivalent
        if one exists."""
        try:
            return self.session.query(NutritionAlias).filter_by(ingkey=str(key)).one()
        except NoResultFound:
            return None

    def get_nutinfo_for_ing (self, ing, multiplier=None):
        """A convenience function that grabs the requisite items from
        an ingredient."""
        if ing.recipe_ref:
            return self.get_nutinfo_for_inglist(ing.recipe_ref.ingredients,ingObject=ing,multiplier=ing.amount)
        if ing.rangeamount:
            # just average our amounts
            try:
                amount = (ing.rangeamount + ing.amount)/2
            except TypeError:
                print 'Failed trying to add',ing.rangeamount,ing.amount
                raise
        else:
            amount = ing.amount
        if not amount: amount=1
        if multiplier: amount = amount * multiplier
        return self.get_nutinfo_for_item(ing.ingkey,amount,ing.unit,ingObject=ing)

    def get_nutinfo_for_inglist (self, inglist, ingObject=None, multiplier=None):
        """A convenience function to get Nutrition for a list of ingredients.
        """
        result = Nutrition()
        for i in inglist:
            result += self.get_nutinfo_for_ing(i, multiplier)
        return result

    def get_nutinfo_for_item (self, key, amt, unit, ingObject=None):
        """Handed a key, amount and unit, get out nutritional Database object.
        """
        ni=self.get_nutinfo(key)
        if not amt:
            amt = 1
        if ni: # We *can* have conversions w/ no units!
            c=self.get_conversion_for_amt(amt,unit,key=key,row=ni)
            if c:
                return c*ni
        # FIXME: The following used to return NutritionVapor
        return Nutrition()

    def get_nutinfo_from_desc (self, desc):
        try:
            return self.session.query(Nutrition).filter_by(desc=desc).one()
        except NoResultFound:
            matches = self.get_matches(desc)
            if len(matches) == 1:
                ndbno = matches[0][1]
                return self.session.query(Nutrition).filter_by(ndbno=ndbno).one()
        return None
    
    def get_nutinfo (self, key):
        """Get our nutritional information for ingredient key 'key'
        We return an object interfacing with our DB whose attributes
        will be nutritional values.
        """
        # FIXME: Use a relation instead.
        try:
            aliasrow = self.session.query(NutritionAlias).filter_by(ingkey=str(key)).one()
        except NoResultFound:
            # See if the key happens to match an existing description...
            ni = self.get_nutinfo_from_desc(key)
            if ni:
                return ni
            # if we don't have a nutritional db row, return a
            # NutritionVapor instance which remembers our query and allows
            # us to redo it.  The idea here is that our callers will get
            # an object that can guarantee them the latest nutritional
            # information for a given item.
            # return NutritionVapor(self,key)
            # FIXME: We should find a cleaner solution to the previous behavior
            # Maybe by throwing exceptions? For now, we'll just return a null
            # Nutrition object.
            return Nutrition()
        else:
            try:
                return self.session.query(Nutrition).filter_by(ndbno=aliasrow.ndbno).one()
            except NoResultFound:
                return None

    def get_ndbno (self, key):
        try:
            aliasrow = self.session.query(NutritionAlias).filter_by(ingkey=str(key)).one()
            return aliasrow.ndbno
        except NoResultFound:
            return None

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
        if gramweights.has_key(unit):
            mass = gramweights[unit] * amt
            return mass * 0.01
        # Otherwise, we are trying to find our density...
        cnv = None
        if (',' in unit) or ('(' in unit): # Check for density in unit description...
            print 'Checking for density in unit...','densities=',densities
            if ',' in unit:
                unit,description = unit.split(',')
            if '(' in unit:
                unit,description = unit.split('(')
                description = description.strip(')')
            description = description.strip()
            unit = unit.strip()
            print 'description=',description
            if densities.has_key(description):
                print 'We got a density!','unit=',unit
                density = densities[description]
                print density,type(density),'(unit=',unit,')'
                cnv = self.conv.converter('g.',unit,density=density)
                print 'We got a conversion!',cnv
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
            if self.conv.unit_dict.has_key(unit):
                unit = self.conv.unit_dict[unit]
            elif not unit:
                unit = ''
            try:
                lookup = self.session.query(NutritionConversion).filter_by(ingkey=key).filter_by(unit=unit).one()
                cnv = lookup.factor
            except NoResultFound:
                # otherwise, cycle through any units we have and see
                # if we can get a conversion via those units...
                for conv in self.session.query(NutritionConversion).filter_by(ingkey=key).all():
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
        if not row: return {}
        if self.conv.density_table.has_key(key):
            return {'':self.conv.density_table[key]}
        else:
            densities = {}       
            for gd,gw in self.get_gramweights(row).items():
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
        nutweights = self.session.query(UsdaWeight).filter_by(ndbno=row.ndbno).all()
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
        if densities.has_key(''): densities[None]=densities['']
        if key: keyrow=self._get_key(key)
        if densities:
            if key and keyrow and keyrow.density_equivalent and densities.has_key(keyrow.density_equivalent):
                return densities[keyrow.density_equivalent]
            elif densities.has_key(None):
                self.conv.density_table[key]=densities[None]
                return densities[None]
            elif len(densities)==1:
                return densities.values()[0]
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

            
if __name__ == '__main__':
    import gourmet.recipeManager as rm
    db=rm.RecipeManager(**rm.dbargs)
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
                print n,a
            choice = None
            while not choice:
                choice = raw_input('Enter number of choice: ')
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
            key=raw_input('Enter ingredient key: ')
            amt = convert.frac_to_float(raw_input('Enter amount: '))
            unit = raw_input('Enter unit: ')
            if not self.ings:
                self.ings = NutritionInfoList([self.nd.get_nutinfo_for_item(key,amt,unit)])
            else:
                self.ings = self.ings + self.nd.get_nutinfo_for_item(key,amt,unit)

        def add_key (self):
            key=raw_input('Enter key for which we add info: ')
            matches = self.nd.get_matches(key,10)
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
                for v in vv:
                    explanation = v._wheres_the_vapor()
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
    #    row=random.choice(db.nutrition_table)
    #    print 'Information: ',row.desc, nd.get_conversions(row=row)
    #    #print 'Gramweights: ',nd.get_gramweights(row)
    #    #print 'Density of ',row.desc,' = ',nd.get_densities(row)
