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

    def set_key_from_nbdno (self, key, nbdno):
        self.db.naliases.append({'nbdno':nbdno,
                                 'ingkey':key})

    def get_key (self, key):
        print 'key=',key
        rows=self.db.naliases.select({'ingkey':str(key)})
        if rows: return rows[0]
        else: return None

    def get_conversion_for_amt (self, amt, unit, key, row):
        # our default is 100g
        cnv=self.conv.converter('g.',unit)
        if not cnv:
            cnv = self.conv.converter('g.',unit,
                                      density=self.get_density(key,row)
                                      )
        if cnv:
            print 'returning conversion factory ',(.01*amt)/cnv
            return (0.01*amt)/cnv
        else:
            return None

    def get_density (self,key,row=None):
        if not row: row = self.get_key(key)
        if not row: return None
        if self.conv.density_table.has_key(key):
            return self.conv.density_table[key]
        else:
            print 'Calculating density'
            grm1 = self.parse_gramweight_measure(row.gramdsc1)
            grm2 = self.parse_gramweight_measure(row.gramdsc2)
            densities = {}
            for gd,gw in [(grm1,row.gramwt1),(grm2,row.gramwt2)]:
                a,u,e = gd
                if not a:
                    continue
                convfactor=self.conv.converter(u,'ml')
                if convfactor: # if we are a volume
                    # divide mass by volume converted to milileters
                    # (gramwts are in grams)
                    print gw,'/','(',a,'*',convfactor,')'
                    density = float(gw) / (a * convfactor)
                    if e: print '(for ',e,')'
                    densities[e]=density
            if densities:
                if densities.has_key(None):
                    self.conv.density_table[key]=densities[None]
                    return densities[None]
                else:
                    return self.choose_density(densities)

    def choose_density (self, densdic):
        # this will eventually query the user...
        print "Choosing an arbitrary density..."
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
    import gourmet.recipeManager as rm
    rm.dbargs['file']='/tmp/fdsa/recipes.mk'
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
        print 'Density of ',row.desc,' = ',nd.get_density(fake_key,row)
        fake_key = "%s"%(int(fake_key)+1)
    
    
