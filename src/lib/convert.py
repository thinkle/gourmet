#!/usr/bin/python
import re
from defaults import lang as defaults
from gdebug import *

class converter:
    def __init__(self):
        self.create_conv_table()
        self.create_density_table()
        self.create_cross_unit_table()
        self.create_vol_to_mass_table()
        # right now we only track densities, but we might convert
        # between other kinds of units eventually
        self.cross_unit_dicts={'density':self.density_table}
        ## This allows for varied spellings of units to be entered.
        self.create_unit_dict()
        self.build_converter_dictionary()
        self.build_converter_dictionary(self.v2m_table,density=True)

    def create_conv_table(self):
        self.conv_table = defaults.CONVERTER_TABLE

    def create_density_table (self):
        self.density_table = defaults.DENSITY_TABLE

    def create_vol_to_mass_table (self):
        self.v2m_table = defaults.VOL_TO_MASS_TABLE

    def create_cross_unit_table (self):
        self.cross_unit_table = defaults.CROSS_UNIT_TABLE

    def create_unit_dict(self):
        self.units = defaults.UNITS
        self.unit_dict={}
        for itm in self.units:
            key = itm[0]
            variations = itm[1]
            self.unit_dict[key] = key
            for v in variations:
                self.unit_dict[v] = key

    def build_converter_dictionary (self, table=None, density=False):
        # first, make a list of all units in our dictionaries
        #print 'build converter dictionary!'
        if not density:
            convert = self.convert_simple
        else:
            def convert (u1,u2):
                return self.convert_w_density(u1,u2,density=1)
        units = []
        if not table:
            table=self.conv_table
        else:
            #print "We were handed a table: ",table
        for u1,u2 in filter(lambda x: len(x)==2, table.keys()):
            if u1 not in units: units.append(u1)
            if u2 not in units: units.append(u2)
        #print 'done looping through list'
        for u in units:
            #print 'grabbing possible conversions for ',u
            debug('unit=%s'%u)
            d=self.possible_conversions(u,dict=table)
            to_expand = d.keys()
            # keep a list of what we've expanded
            expanded = []
            while len(to_expand) >= 1:
                itm = to_expand.pop()
                if itm not in expanded:
                    #debug('Expanding %s'%itm)
                    factor = convert(itm,u)
                    #debug('There are %s %s in a %s'%(factor,u,itm))
                    d2 = self.possible_conversions(itm)
                    if factor:
                        for k,v in d2.items():
                            if not convert(u,k):
                                #debug('and there are %s %s in a %s'%(v,itm,k))
                                conversion = float(v) * float(factor)
                                table[(k,u)]= conversion
                                #debug("Adding: There are %s %s in a %s (via %s)"%(conversion,u,k,itm))
                            if k not in expanded and k not in to_expand and k != itm and k != u:
                                to_expand.append(k)
                    expanded.append(itm)

    def convert_simple (self, u1, u2, item=None):
        if u1 == u2:
            return 1.0
        else:
            dict=self.conv_table
            if dict.has_key((u1,u2)):
                return dict[(u1,u2)]
            elif dict.has_key((u2,u1)):
                return float(1) / float(dict[(u2,u1)])
            else:
                return 0

    def convert_w_density (self, u1, u2, density=None, item=None):
        if u1 == u2:
            return 1.0
        if not density:
            if self.density_table.has_key(item):
                density=self.density_table[item]
            else:
                return None
        if self.v2m_table.has_key((u1,u2)):
            conv = self.v2m_table[(u1,u2)]                
            return conv * density
        elif self.v2m_table.has_key((u2,u1)):
            conv = float(1) / float(self.v2m_table[(u2,u1)])
            return conv / density
        else:
            return None

    def list_of_cu_tables (self, dictcu=None):
        if (not dictcu):
            dictcu = self.cross_unit_table
        values = dictcu.values()
        ret = []
        for v in values:
            if not v[0] in ret:
                ret.append(v[0])
        return ret
                
    def conv_dict_for_item (self, item=None, dictcu=None, mult=None):
        """item overrides mult"""
        if (not dictcu):
            dictcu = self.cross_unit_table
#        tbls = self.list_of_cu_tables(dictcu)
#        my_tbls = []
        ret = {}
        for itm in dictcu.items():
            k = itm[0]
            v = itm[1]
            dct = self.cross_unit_dicts[v[0]]
            conv = v[1]
            if item and dct.has_key(item):
                mult = dct[item]
            if mult: 
                ret[k] = conv * mult
        return ret

    def converter (self, u1, u2, item=None, density=None):
        ## Just a front end to convert_fancy that looks up units
        if self.unit_dict.has_key(u1):
            unit1 = self.unit_dict[u1]
        else:
            unit1 = u1
        if self.unit_dict.has_key(u2):
            unit2 = self.unit_dict[u2]
        else:
            unit2 = u2
        ## provide some kind of item lookup?
        return self.convert_fancy(unit1, unit2, item=item, density=density)

    def convert_fancy (self, u1, u2, item=None, density=None):
        simple = self.convert_simple(u1,u2,self.conv_table)
        if simple: return simple
        # otherwise, we need to grab use a density table
        debug('using density data')
        return self.convert_w_density(u1,u2,item=item,density=density)

    def get_conversions (self, u, item=None, density=None):
        dct = None
        if item or density:
            dct = self.conv_table.copy()
            if item:
                dct.update(self.conv_dict_for_item(item))
            elif density:
                dct.update(self.conv_dict_for_item(mult=density))
        return self.possible_conversions(u, dct)

    def get_all_conversions (self, u, item=None, density=None):
        dict = self.get_conversions(u, item, density)
        expanded = []
        conversions = dict.keys()
        lst = conversions[0:] # make another copy to chew up
        while len(lst) >= 1:
            itm = lst.pop()
            if not itm in conversions:
                conversions.append(itm)
            if not itm in expanded:
                d = self.get_conversions(u,itm,density)
                lst.extend(d.keys())
                expanded.append(itm)
        return conversions
    
    def possible_conversions(self, u, dict=0):
        """Return a dictionary of everything that unit u can convert to
        The keys are what it can convert to and the values are the conversion
        factor."""
        if (not dict):
            dict=self.conv_table
        ret = {}
        entries = dict.items()
        for item in entries:
            i1 = item[0][0]
            i2 = item[0][1]
            if u == i1:
                ret[i2] = float(1) / item[1]
            elif u == i2:
                ret[i1] = float(item[1])
        return ret            

    def readability_score (self,amt,unit=None):
        """We rate the readability of a number"""
        readability = 0
        ## We like our numbers whole or in normal fractions
        if integerp(amt):
            readability += 1
        elif integerp(amt * 2):
            readability += 1
        elif integerp(amt * 4):
            readability += 1
        elif integerp(amt * 3):
            readability += 1
        elif integerp (amt * 8):
            readability += 0.8
        elif integerp (amt * 6):
            readability += 0.3
        elif integerp (amt * 5):
            readability += 0.2
        elif integerp (amt * 10):
            readability += 0.05
        ## If it is not a normal fraction, readability takes a hit
        else:
            readability += -3
        ## If it is exactly 1 it gets a bump:
        if amt == 1: readability += 0.5
        if unit:
            # if we are beyond the min or max for our group, we take
            # a substantial readability hit (this is worse than anything
            # else)
            try:
                u = self.unit_dict[unit]
            except KeyError:
                debug("KeyError looking up unit",1)
                u = unit
            try:
                ugroup,n = defaults.unit_group_lookup[u]
            except KeyError:
                debug('Key Error for %s in \nunit_group_lookup: %s'%(unit,defaults.unit_group_lookup),
                      0)
                #raise
                return -10
            else:
                u,rng = defaults.UNIT_GROUPS[ugroup][n]
                mn,mx = rng
                debug('Readability range for %s = %s:%s'%(u,mn,mx),8)
                if mn and amt and  amt < mn:
                    readability += -2
                    # we add a penalty proportional to the undersizedness
                    if (mn-amt): readability += -(2 * (mn - amt))/amt
                if mx and amt > mx:
                    readability += -2
                    # now we get clever and add a penalty proportional to the oversizedness
                    if (amt-mx): readability += - (amt - mx)/(float(mx)*2)
        else:
            # otherwise, we'll make some assumptions about numbers
            # we don't like things over a thousand and we really don't
            # or under a hundredth
            if amt > 1000: readability += -2
            elif amt < .1:
                readability += -1
                if amt < .01:
                    readability += -1
                    if amt < .001:
                        readability += -1
                        if amt < .0001:
                            readability += -1
        ## And we like numbers between 1/8 and 4
        #if 0.25 <= amt <= 4:
        #    readability += 1
        ### Less than 1/10th is getting too small
        #elif 0.1 >= amt:
        #    readability += -1
        ## And we rather dislike numbers over 10
        #elif 20 >= amt > 10:
        #    readability += -0.9
        ## And we really can't have numbers over 20
        #elif 100 >= amt > 20:
        #    readability += -5
        ## And we really, really, really can't have numbers over 100
        #elif 1000 >= amt > 100:
        #    readability += -10
        #elif amt >= 1000:
        #    readability += -20
        return readability

    def adjust_unit (self, amt, unit, item=None):
        try:
            u = self.unit_dict[unit]
            ugroup,n = defaults.unit_group_lookup[u]
        except KeyError:
            return amt,unit
        else:
            units=defaults.UNIT_GROUPS[ugroup]
            ret_readability = self.readability_score(amt,unit)
            ret_amt = amt
            ret_unit = unit
            ret_distance = 0
            n1 = 0
            for u2,rng in units:
                conv = self.converter(u,u2)
                new_amt = conv * amt
                readability = self.readability_score(new_amt,u2)
                debug('%s %s, Readability = %s'%(new_amt,u2,readability),6)
                use_us = False
                if readability > ret_readability:
                    use_us = True
                elif readability == ret_readability and abs(n-n1) < ret_distance:
                    use_us = True
                if use_us:
                    ret_amt = new_amt
                    ret_distance = abs(n-n1)
                    ret_unit = u2
                    ret_readability = readability
                n1 += 1
                    
            debug('adjust unit called with %s %s, returning %s %s (R:%s)'%(amt,unit,ret_amt,ret_unit,
                                                                           ret_readability),
                  3)
            return ret_amt,ret_unit

    def use_reasonable_unit (self, amt1, u1, amt2, u2, conv):
        """Given the conversion factor and the amounts,
        we're going to try to figure out which unit
        is the most human-readable.  conv is what converts
        from amt1 into amt2.  We return a list of
        amt unit, where the amount is our total, and the unit
        is our chosen unit."""
        u1amt = amt1 + amt2 * (1 / float(conv))
        u2amt = amt2 + amt1 * conv
        if self.readability_score(u1amt) >= self.readability_score(u2amt):
            return [u1amt, u1]
        else:
            return [u2amt, u2]

    def add_reasonably (self, a1, u1, a2, u2, item=None):
        """Return a list with amount and unit if conversion is possible.
        Else return None"""
        if not (a1 and a2):
            # we give up if these aren't numbers
            return None
        conv = self.converter(u1,u2, item)
        if conv:
            ## Don't bother with all the work if the conversion factor is 1
            if conv == 1:
                return [a1 + a2, u1]
            else:
                return self.use_reasonable_unit(a1, u1, a2, u2, conv)
        else:
            return None

    def amt_string(self, amt, approx=0.01):
        """Given list of [amount unit], hand back a string
        representing amount.  We'll do our best to turn numbers back
        into fractions here so that they will look easily readable"""
        num = amt[0]
        un = amt[1]
        return "%s %s" %(float_to_frac(num, approx=approx), un)

    
def integerp (num, approx=0.01):
    """approx can be a decimal that is a guide to rounding.
    That is, if approx is 0.001, then we will consider
    0.9991 and 1.0009 both to be the integer 1.  This feature
    will only work for positive, non-zero numbers."""
    try:
        if int(num) == float(num):
            return int(num)
        elif approx:
            bigside = int(num+approx)
            smallside = int(num-approx)
            if bigside != smallside:
                return bigside
            else:
                return None
    except:
        return None

def float_to_frac (n, d=[2,3,4,5,6,8,10,16],approx=0.01):
    """Take a number -- or anything that can become a float --
    and attempt to return a fraction with a denominator in the list `d'. We
    approximate fractions to within approx. i.e. if approx=0.01, then 0.331=1/3"""
    if not n: return ""
    n=float(n)
    i = int(n)
    if i >= 1:
        i="%s "%int(n)
    else:
        i=""
    rem = n - int(n)
    if rem==0:
        if i:
            return "%s"%i
        else:
            return "0"
    else:
        def fractify(decimal, divisor, approx):
            dividend = decimal*divisor
            if integerp(dividend, approx):
                return "%s/%s"%(integerp(dividend, approx), divisor)
            else:
                return False
        flag = False
        for div in d:
            f = fractify(rem,div,approx)
            if f:
                flag = True
                return "%s%s"%(i,f)
        if not flag:
            if len("%s"%n) > 3:
                return "%.2f"%(n)
            else:
                return "%s"%n
        

def frac_to_float (s):
    """We assume fractions look like this (I )?N/D"""
    if s.find("/"):
        m=re.match("([0-9]+\s+)?([0-9]+)/([1-9]+)",s)
        if m:
            i,n,d=m.groups()
            if not i: i=0
            return float(i)+(float(n)/float(d))
        else:
            try:
                return float(s)
            except:
                None
    else:
        #If this isn't a fraction, we're just using float
        try:
            return float(s)
        except:
            None



if __name__ == '__main__':
    class interactive:
        def __init__ (self):
            self.c = converter()
            self.options = {'Convert':self.converter,
                            'Add':self.adder,
                            'Adjust':self.adjuster,
                            'Quit':self.quit}
            while 1:
                self.offer_options()
            
        def offer_options (self):
            print 'Choose one of the following actions:'
            for k in self.options.keys(): print k
            choice = raw_input('Type your choice: ')
            if self.options.has_key(choice):
                self.options[choice]()
            else:
                print "I'm afraid I didn't understand your choice!"
                self.return_to_continue()
                self.offer_options()
                          
        def get_unit (self, prompt="Enter unit: "):
            u = raw_input(prompt).strip()
            if self.c.unit_dict.has_key(u):
                return u
            elif u=='list':
                for u in self.c.unit_dict.keys():
                    print u,", ",
                print ""
                return self.get_unit(prompt)
            else:
                print u, 'Is not a unit I know about! Please try again.'
                print '(Type "list" for a list of valid units)'
                return self.get_unit(prompt)

        def get_amount (self, prompt="Enter amount: "):
            amt = frac_to_float(raw_input(prompt))
            if not amt:
                print "Please enter an amount!"
                return self.get_amount(prompt)
            else:
                return amt
                
        def converter (self):
            u1 = self.get_unit("Enter source unit: ")
            amt = self.get_amount("Enter source amount: ")
            u2 = self.get_unit("Enter target unit: ")
            conv = self.c.converter(u1,u2)
            print '%s %s = %s %s'%(amt,u1,conv*amt,u2)
            self.return_to_continue()

        def adjuster (self):
            u1 = self.get_unit('Original unit: ')
            a1 = self.get_amount('Original amount: ')
            a,u = self.c.adjust_unit(a1,u1)
            print 'Most readable unit = %s %s'%(a,u)

        def return_to_continue (self):
            print 'Enter return to continue: '
            raw_input()

        def adder (self):
            u1 = self.get_unit('Enter unit 1: ')
            a1 = self.get_amount("Enter amount 1: ")
            u2 = self.get_unit('Enter unit 2: ')
            a2 = self.get_amount('Enter amount 2: ')
            result = self.c.add_reasonably(a1,u1,a2,u2)
            if result:
                print "%s %s + %s %s = %s"%(u1,a1,u2,a2,result)
            else:
                print "I'm sorry, I couldn't add that together!"
            self.return_to_continue()
            
        def quit (self):
            import sys
            sys.exit()
        
    
    i=interactive()
