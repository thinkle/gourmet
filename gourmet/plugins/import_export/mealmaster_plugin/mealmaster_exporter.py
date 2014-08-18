import textwrap
from gourmet import gglobals,  convert
from gourmet.exporters.exporter import exporter_mult
from gourmet.gdebug import debug

class mealmaster_exporter (exporter_mult):
    def __init__ (self, rd, r, out, conv=None, change_units=True, mult=1):
        import mealmaster_importer
        self.add_to_instructions=""
        self.conv = conv
        mmf2mk = mealmaster_importer.mmf_constants()
        self.uc=mmf2mk.unit_convr
        recattrs_orig=mmf2mk.recattrs
        self.recattrs={}
        for k,v in recattrs_orig.items():
            self.recattrs[v]=k
        self.categories = ""
        exporter_mult.__init__(self, rd, r, out,
                               conv=conv,
                               order=['attr','ings','text'],
                               attr_order=['title',
                                           'cuisine',
                                           'category',
                                           'yields',
                                           'cooktime',
                                           'preptime',
                                           'rating',
                                           'source',
                                           'link'],
                               convert_attnames=False,
                               change_units=change_units,
                               mult=mult)

    def write_head (self):
        self.out.write("MMMMM----- Recipe via Meal-Master (tm)\n\n")

    def write_attr (self, label, text):
        if label=='category' or label=='cuisine':
            if not self.categories:
                self.categories=text
                return
            else:
                self.categories="%s, %s"%(self.categories,text)
                self.write_categories()
        # Move attributes that MealMaster doesn't understand to the instructions
        elif label=='preptime' or label=='rating' or label=='source':
            self.add_to_instructions += "\n\n%s: %s"%(gglobals.REC_ATTR_DIC[label],text)
        else:
            if label and text:
                if self.recattrs.has_key(label):
                    label=self.recattrs[label]
                else:
                    label=label.capitalize()
                label=self.pad(label,8)
                self.out.write("%s: %s\n"%(label, text))

    def write_categories (self):
        self.out.write("%s: %s\n"%(self.pad("Categories",8),self.categories))
        self.categories = ""

    def write_attr_foot (self):
        if self.categories: self.write_categories() # if these haven't been written yet...

    def pad (self, text, chars):
        text=text.strip()
        fill = chars - len(text)
        return "%s%s"%(" "*fill,text)
    
    def write_text (self, label, text):
        if label=='instructions' and self.add_to_instructions:
            text = text + self.add_to_instructions
            self.add_to_instructions = ""
        ll=text.split("\n")
        for l in ll:
            for wrapped_line in textwrap.wrap(l):
                self.out.write("\n  %s"%wrapped_line)
            self.out.write("\n  ")
            
    def write_inghead (self):
        self.master_ings=[] # our big list
        # self.ings is what we add to
        # this can change when we add groups
        self.ings = self.master_ings
        self.ulen=1
        # since the specs we found suggest it takes 7 blanks
        # to define an ingredient, our amtlen needs to be at
        # least 6 (there will be an extra space added
        self.amtlen=6
        self.out.write("\n")

    def write_grouphead (self, name):
        debug('write_grouphead called with %s'%name,0)
        group = (name, [])
        self.ings.append(group) # add to our master
        self.ings = group[1] # change current list to group list

    def write_groupfoot (self):
        self.ings = self.master_ings # back to master level

    def write_ing (self, amount="1", unit=None, item=None, key=None, optional=False):
        if type(amount)==type(1.0) or type(amount)==type(1):
            amount = convert.float_to_frac(amount)
            if not amount: amount = ""
        if not unit: unit = ""
        unit_bad = False
        if len(unit) > 2 or '.' in unit:
            unit_bad = True
            # Try to fix the unit
            if self.conv.unit_dict.has_key(unit):
                new_u = self.conv.unit_dict[unit]
                if len(new_u) <= 2 and not '.' in new_u:
                    unit = new_u; unit_bad = False
                else:
                    if self.uc.has_key(new_u):
                        unit = self.uc[new_u]; unit_bad = False
        if unit_bad: # If we couldn't fix the unit...  we add it to
            # the item
            if unit: item="%s %s"%(unit,item)
            unit=""
        if len(unit)>self.ulen:
            self.ulen=len(unit)
        if len(amount)>self.amtlen:
            self.amtlen=len(amount)
            #print "DEBUG: %s length %s"%(amount,self.amtlen)
        # we hold off writing ings until we know the lengths
        # of strings since we need to write out neat columns
        if optional: item="%s (optional)"%item
        self.ings.append([amount,unit,item])

    def write_ingfoot (self):
        """Write all of the ingredients"""
        ## where we actually write the ingredients...
        for i in self.master_ings:
            # if we're a tuple, this is a group...
            if type(i)==type(()):
                # write the group title first...
                group = i[0]
                width = 70
                dashes = width - len(group)
                left_side = dashes/2 - 5
                right_side = dashes/2
                self.out.write("-----%s%s%s\n"%(left_side * "-",
                                           group.upper(),
                                           right_side * "-")
                          )
                map(self._write_ingredient,i[1])
                self.out.write("\n") # extra newline at end of groups
            else:
                self._write_ingredient(i)
        # we finish with an extra newline
        self.out.write("\n")
                        
    def _write_ingredient (self, ing):
        a,u,i = ing
        self.out.write("%s %s %s\n"%(self.pad(a,self.amtlen),
                                     self.pad(u,self.ulen),
                                     i))

    def write_foot (self):
        self.out.write("\n\n")
        self.out.write("MMMMM")
        self.out.write("\n\n")
