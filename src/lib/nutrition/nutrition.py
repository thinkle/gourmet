import re
import sys

class NutritionData:
    def __init__ (self, db, conv):
        self.db = db
        self.conv = conv
        self.conv.density_table
        self.gramwght_regexp = re.compile("([0-9.]+)?( ?([^,]+))?(, (.*))?")

    def set_key (self, key, row):
        density=self.get_density(key,row)
        row = self.get_key(key)
        if row: self.row.nbdno=row.nbdno
        else:
            self.db.naliases.append({'nbdno':row.nbdno,
                                  'ingkey':key})

    def set_key_from_ndbno (self, key, nbdno):
        self.db.naliases.append({'nbdno':nbdno,
                                 'ingkey':key})

    def get_key (self, key):
        #print 'key=',key
        rows=self.db.naliases.select({'ingkey':str(key)})
        if rows:
            return rows[0]
        else: return None

    def get_nut_from_key (self, key):
        aliasrow = self.get_key(key)
        if aliasrow:
            nvrows=self.db.nview.select({'ndbno':aliasrow.ndbno})
            if len(nvrows)==1:
                return nvrows[0]
            elif len(nvrows)>1:
                raise "Too many rowd returned for ndbno %s"%aliasrow.ndbno
        # if we don't have a nutritional db row, return None
        return None

    def get_conversion_for_amt (self, amt, unit, key, row):
        # our default is 100g
        cnv=self.conv.converter('g.',unit)
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
            cnv = self.conv.converter('g.',unit,density)
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
        if not row: row = self.get_key(key)
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
        

    
    
