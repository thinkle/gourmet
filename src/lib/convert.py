#!/usr/bin/python
import re, locale
from defaults import lang as defaults
from gettext import gettext as _
from gettext import ngettext
from gdebug import *

FRACTIONS_ALL = 1
FRACTIONS_NORMAL = 0
FRACTIONS_ASCII = -1
FRACTIONS_OFF = -2

USE_FRACTIONS = FRACTIONS_NORMAL

class PossiblyCaseInsensitiveDictionary (dict):

    transformations = ["lower","title","upper"]

    def has_key (self, k):
        if dict.has_key(self,k): return True
        else:
            for t in self.transformations:
                if hasattr(k,t):
                    if dict.has_key(self,getattr(k,t)()): return True
        return False

    def __getitem__ (self, k):
        if dict.has_key(self,k):
            return dict.__getitem__(self,k)
        else:
            for t in self.transformations:
                if hasattr(k,t):
                    nk = getattr(k,t)()
                    if dict.has_key(self,nk):
                        return dict.__getitem__(self,nk)
        # Raise plain old error
        dict.__getitem__(self,k)
        

class converter:

    unit_to_seconds = {
    'seconds':1,
    'minutes':60,
    'hours':60*60,
    'days':24*60*60,
    'weeks':7*24*60*60,
    'months':31*24*60*60,
    'years':365.25*24*60*60,
    #'decades':10*365.25*24*60*60,
    #'centuries':100*365.25*24*60*60,
    #'millenia':1000*365.25*24*60*60,
    }

    # this is a bit of a hackish attempt to make a matcher for all
    # plural forms of time units. We use range(5) since as far as I
    # can see, enumerating the forms for 0 through 5 should give you
    # all possible forms in all languages.
    #
    # See http://www.sbin.org/doc/glibc/libc_8.html
    time_units = [('seconds',[ngettext('second','seconds',n) for n in range(5)] + ['s.', 'sec', 'secs' ]),
                  # min. = abbreviation for minutes
                  ('minutes',[_('min'),'min.','min','mins'] + [ngettext('minute','minutes',n) for n in range(5)]),
                  # hrs = abbreviation for hours
                  ('hours',[_('hrs.'),'hrs','hr'] + [ngettext('hour','hours',n) for n in range(5)]),
                  ('days',[ngettext('day','days',n) for n in range(5)]),
                  ('years',[ngettext('year','years',n) for n in range(5)]),
                  #('decades',[ngettext('decade','decades',n) for n in range(5)]),
                  #('centuries',[ngettext('century','centuries',n) for n in range(5)]),
                  #('millenia',[ngettext('millenium','millenia',n) for n in range(5)]),
                  ]
    
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
        self.add_time_table()
        self.build_converter_dictionary()
        self.build_converter_dictionary(self.v2m_table,density=True)
        

    def add_time_table (self):
        for u,conv in self.unit_to_seconds.items():
            self.conv_table[(u,'seconds')]=conv        

    def create_conv_table(self):
        self.conv_table = defaults.CONVERTER_TABLE.copy()

    def create_density_table (self):
        self.density_table = defaults.DENSITY_TABLE.copy()

    def create_vol_to_mass_table (self):
        self.v2m_table = defaults.VOL_TO_MASS_TABLE.copy()

    def create_cross_unit_table (self):
        self.cross_unit_table = defaults.CROSS_UNIT_TABLE.copy()

    def create_unit_dict(self):
        self.units = defaults.UNITS[0:]
        for u,alts in self.time_units:
            lst = []
            for a in alts:
                if not a in lst: lst.append(a)
                if not a.title() in lst: lst.append(a.title())
                if not a.capitalize() in lst: lst.append(a.capitalize())
                if not a.upper() in lst: lst.append(a.upper())
                if not a.lower() in lst: lst.append(a.lower())
            self.units.append((u,lst))
        self.unit_dict=PossiblyCaseInsensitiveDictionary()
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
                # Ignore anything that doesn't need density
                if self.convert_simple(u1,u2): return None
                return self.convert_w_density(u1,u2,density=1)
        units = []
        if not table:
            table=self.conv_table
        #else:
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
                                # If we're doing density, we want to
                                # make sure we always have our tuples
                                # (volume,density)
                                if density and itm not in [key[0] for key in table.keys()]:
                                    table[(u,k)]=float(1)/conversion
                                else: table[(k,u)]= conversion
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
        """We rate the readability of a number and unit

        This is rather advanced. We presume a few things -- such as that we
        like integers and simple fractions 1/2 1/3 1/4 better than other things.

        We also learn from the defaults module what the bounds are for readability
        for each amount given.
        """
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
                    if (amt-mx): readability += - ((amt - mx)/float(mx))*2
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

    def adjust_unit (self, amt, unit, item=None, favor_current_unit=True):

        """Return the most readable equivalent of amount and unit for item ITM

        amt - our amount
        unit - our current unit
        item - the item (in case it makes a difference -- currently not implemented)
        favor_current_item - a flag; if True (default) we give our current unit a slight
                             preference, to avoid changing the unit if unnecessary.
        Here we do our best to provide readable units, so that the user is presented
        with 1/2 cup rather than 8 tablespoons, for example.
        """
        if not amt: return amt,unit
        try:
            u = self.unit_dict[unit]
            ugroup,n = defaults.unit_group_lookup[u]
        except KeyError:
            return amt,unit
        else:
            units=defaults.UNIT_GROUPS[ugroup]
            ret_readability = self.readability_score(amt,unit)
            if favor_current_unit: ret_readability += 1
            ret_amt = amt
            ret_unit = unit
            ret_distance = 0
            n1 = 0
            for u2,rng in units:
                conv = self.converter(u,u2)
                if not conv: return amt,unit
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
        into fractions here so that they will look easily readable.

        We can also handle amounts handed to us as tuples (as ranges)!"""
        num = amt[0]
        un = amt[1]
        if type(num)==tuple or type(num)==list:
            nstring=float_to_frac(num[0],approx=approx).strip()
            if len(num)>1 and num[1]:
                nstring += "-"
                nstring += float_to_frac(num[1],approx=approx).strip()
        else:
            nstring = float_to_frac(num,approx=approx)
        if un:
            return "%s %s" %(nstring, un)
        else:
            return "%s"%nstring

    def timestring_to_seconds (self, timestring):
        """Take a timestring and parse it into seconds.

        We assume numbers come before time units - surely this will
        break some languages(?). We'll build the parameter in when the
        time comes...
        """
        # Before we do our real work, parse times that look like this 0:30
        # Note the following will be true
        # 1:30 = 1 1/2 hours
        # 00:00:20 = 20 seconds
        if re.match('^\d\d?:\d\d(:\d\d)?',timestring):
            times = [locale.atof(s) for s in timestring.split(':')]
            if len(times) == 3:
                h,m,s = times
            else:
                h,m = times; s = 0
            return h*60*60 + m*60 + s
        numbers = []
        for match in NUMBER_FINDER.finditer(timestring):
            if numbers: numbers[-1].append(match.start())
            numbers.append([match.start(),match.end()])
        if numbers: numbers[-1].append(None)
        secs = 0
        for num_start,num_end,section_end in numbers:
            num = frac_to_float(timestring[num_start:num_end])
            unit = timestring[num_end:section_end].strip()
            if self.unit_dict.has_key(unit):
                conv = self.converter(unit,'seconds')
                if conv:
                    secs += num * conv
        return secs

    def timestring_to_seconds_old (self, timestring):
        """Take a timestring and parse it into seconds.

        This logic may be a little fragile for non-English languages.
        """
        words = re.split('[ \s,;]+',str(timestring))
        seconds = 0
        num = []
        for n,w in enumerate(words):
            if NUMBER_MATCHER.match(w): num.append(w)
            elif num and self.unit_dict.has_key(w):                
                conv = self.converter(w,'seconds')
                if conv:
                    n = frac_to_float(" ".join(num))
                    if n: seconds += n * conv
                    num = []
        if seconds: return seconds
    

# Each of our time formatting functions takes two arguments, which
# allows us to handle fractions in the outside world
time_formatters = {
    #'millennia':lambda decades: ngettext("millenium","millenia",round(decades))
    #'centuries':lambda decades: ngettext("century","centuries",round(decades))
    #'decades':lambda decades: ngettext("decade","decades",round(decades))
    'years':lambda years: ngettext("year","years",years),
    'months':lambda months: ngettext("month","months",months),
    'weeks':lambda weeks: ngettext("week","weeks",weeks),
    'days':lambda days: ngettext("day","days",days),
    'hours':lambda hours: ngettext("hour","hours",hours),
    'minutes':lambda minutes: ngettext("minute","minutes",minutes),
    'seconds':lambda seconds: ngettext("second","seconds",seconds),
    }    

def seconds_to_timestring (time, round_at=None, fractions=FRACTIONS_NORMAL):
    time = int(time)
    time_strings = []
    units = converter.unit_to_seconds.items()
    units.sort(lambda a,b: a[1]<b[1] and 1 or a[1]>b[1] and -1 or 0)
    for unit,divisor in units:  
        time_covered = time / int(divisor)
        # special case hours, which we English speakers anyway are
        # used to hearing in 1/2s -- i.e. 1/2 hour is better than 30
        # minutes.
        add_half = 0
        if time % divisor == .5*divisor and not time_strings:
            add_half = 0.5
            time_covered += 0.5
        if time_covered or add_half:
            #print time_covered,'(rounds to ',round(time_covered),')'
            if round_at and len(time_strings)+1>=round_at:
                if not add_half: time_covered = int(round(float(time)/divisor))
                time_strings.append(" ".join([
                    float_to_frac(time_covered,fractions=fractions),
                    # round because 1/2 = 1 as far as plural formas are concerned
                    time_formatters[unit](round(time_covered)) 
                    ])
                                    )
                break
            else:
                time_strings.append(" ".join([
                    float_to_frac(time_covered,fractions=fractions),
                    # round because 1/2 = 1 as far as plural forms are concerned
                    time_formatters[unit](round(time_covered))
                    ]))
                time = time - time_covered * divisor
                if time==0: break
    if len(time_strings)>2:
        # Translators... this is a messay way of concatenating
        # lists. In English we do lists this way: 1, 2, 3, 4, 5
        # and 6. This set-up allows for variations of this system only.
        # You can of course make your language only use commas or
        # ands or spaces or whatever you like by translating both
        # ", " and " and " with the same string.
        return _(" and ").join([_(", ").join(time_strings[0:-1]),time_strings[-1]])
    else:
        return _(" ").join(time_strings)    

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


# Fractions used in most charsets -- for certain exports, etc., we
# want to limit special fractions to these and use straight-up ascii
# fractions otherwise. These fractions must also be keys in
# NUM_TO_FRACTIONS

NUMBER_WORDS = {}
if hasattr(defaults,'NUMBERS'):
    for n,words in defaults.NUMBERS.items():
        for w in words:
            NUMBER_WORDS[w] = n
all_number_words = NUMBER_WORDS.keys()
all_number_words.sort(
    lambda x,y: ((len(y)>len(x) and 1) or (len(x)>len(y) and -1) or 0)
    )

NUMBER_WORD_REGEXP = '|'.join(all_number_words).replace(' ','\s+')
FRACTION_WORD_REGEXP = '|'.join(filter(lambda n: NUMBER_WORDS[n]<1.0,
                                       all_number_words)
                                ).replace(' ','\s+')

NORMAL_FRACTIONS = [(1,2),(1,4),(3,4)] 

NUM_TO_FRACTIONS = {
    (1,2) : u'\u00BD',
    (1,4) : u'\u00BC',
    (3,4) : u'\u00BE',
    (1,3) : u'\u2153',
    (2,3) : u'\u2154',
    (1,5) : u'\u2155',
    (2,5) : u'\u2156',
    (3,5) : u'\u2157',
    (4,5) : u'\u2158',
    (1,6) : u'\u2159',
    (5,6) : u'\u215A',
    (1,8) : u'\u215B',
    (3,8) : u'\u215C',
    (5,8) : u'\u215D',
    (7,8) : u'\u215E',
    }

UNICODE_FRACTIONS = {
    # a dictionary of funky unicode numbers not recognized by standard
    # python float() and int() functions
    u'\u00BD':1.0/2,
    u'\u00BC':1.0/4,
    u'\u00BE':3.0/4,
    u'\u2153':1.0/3,
    u'\u2154':2.0/3,
    u'\u2155':1.0/5,
    u'\u2156':2.0/5,
    u'\u2157':3.0/5,
    u'\u2158':4.0/5,
    u'\u2159':1.0/6,
    u'\u215A':5.0/6,
    u'\u215B':1.0/8,
    u'\u215C':3.0/8,
    u'\u215D':5.0/8,
    u'\u215E':7.0/8,
    }

SUP_DICT = {1:u'\u00B9',
            2:u'\u00B2',
            3:u'\u00B3',
            }

SLASH = u'\u2044'
SUB_DICT = {1:u'\u2081',
            2:u'\u2082',
            3:u'\u2083',
            4:u'\u2084',
            5:u'\u2085',
            6:u'\u2086',
            7:u'\u2087',
            8:u'\u2088',
            9:u'\u2089',
            }
            
# nonstandard integers (sub or sup) that may be used in fractions
UNICODE_INTEGERS = {}
for d in SUB_DICT,SUP_DICT:
    for k,v in d.items():
        UNICODE_INTEGERS[v]=k

NUMBER_REGEXP = "[\d.,"
#for k in UNICODE_INTEGERS.keys(): NUMBER_REGEXP+=k # COVERED by re.UNICODE
for k in UNICODE_FRACTIONS.keys(): NUMBER_REGEXP+=k
NUMBER_START_REGEXP = NUMBER_REGEXP + ']'
NUMBER_END_REGEXP = NUMBER_REGEXP + SLASH
NUMBER_END_NO_RANGE_REGEXP = NUMBER_END_REGEXP + " /]"
NUMBER_END_REGEXP += " /-"
NUMBER_END_REGEXP += "]"
NUMBER_REGEXP = "("+NUMBER_START_REGEXP+NUMBER_END_REGEXP+"*"
if NUMBER_WORD_REGEXP:
     NUMBER_REGEXP = NUMBER_REGEXP + '|' + NUMBER_WORD_REGEXP + ')'
     NUMBER_NO_RANGE_REGEXP = '(' + NUMBER_START_REGEXP + '+|' + NUMBER_WORD_REGEXP + ')'
else:
    NUMBER_REGEXP = NUMBER_REGEXP + ")"
    NUMBER_NO_RANGE_REGEXP = NUMBER_START_REGEXP + '+'
NUMBER_MATCHER = re.compile("^%s$"%NUMBER_REGEXP,re.UNICODE)

UNICODE_FRACTION_REGEXP = "[" + "".join(UNICODE_FRACTIONS.keys()) + "]"
DIVIDEND_REGEXP = "[0-9" + "".join(SUP_DICT.values()) + "]+"
SLASH_REGEXP = "[/" + SLASH + "]"
SLASH_MATCHER = re.compile(SLASH_REGEXP)
DIVISOR_REGEXP = "[0-9" + "".join(SUB_DICT.values()) + "]+"
FRACTION_REGEXP = "(" + UNICODE_FRACTION_REGEXP + "|" + DIVIDEND_REGEXP + \
                          SLASH_REGEXP + DIVISOR_REGEXP + ")"

AND_REGEXP = "(\s+%s\s+|\s*[&+]\s*|\s+)"%_('and')

# Match a fraction
if NUMBER_WORD_REGEXP:
    NUM_AND_FRACTION_REGEXP = "((?P<int>%s+|%s)%s)?(?P<frac>(%s|%s))"%(NUMBER_START_REGEXP,
                                                                       NUMBER_WORD_REGEXP,
                                                                       AND_REGEXP,
                                                                       FRACTION_REGEXP,
                                                                       FRACTION_WORD_REGEXP
                                                                       )
    
else:
    NUM_AND_FRACTION_REGEXP = re.compile("((?P<int>%s)+\s+)?(?P<frac>%s)"%(NUMBER_START_REGEXP,FRACTION_REGEXP),re.UNICODE)

FRACTION_MATCHER = re.compile(NUM_AND_FRACTION_REGEXP,re.UNICODE)

NUMBER_FINDER_REGEXP = "(%(NUM_AND_FRACTION_REGEXP)s|%(NUMBER_NO_RANGE_REGEXP)s)(?=($| |[\W]))"%locals()
NUMBER_FINDER = re.compile(NUMBER_FINDER_REGEXP,re.UNICODE)

# Note: the order matters on this range regular expression in order
# for it to properly split things like 1 - to - 3, which really do
# show up sometimes.
RANGE_REGEXP = '([ -]*%s[ -]*|\s*-\s*)'%_('to') # for 'to' used in a range, as in 3-4
RANGE_MATCHER = re.compile(RANGE_REGEXP[1:-1]) # no parens for this one


# We need a special matcher to match known units when they are more
# than one word. The assumption remains that units should be one word
# -- but if we already know about two word units, then we should
# recognize them.

multi_word_units = []
for canonical_name,other_names in defaults.UNITS:
    if ' ' in canonical_name: multi_word_units.append(canonical_name)
    for n in other_names:
        if ' ' in n: multi_word_units.append(n)
MULTI_WORD_UNIT_REGEXP = '(' + \
                       '|'.join([re.escape(u) for u in multi_word_units]) \
                       + ')'


# generic ingredient matcher. This is far from a good matcher -- it's
# used as a fallback to test for things that obviously look like
# ingredients (e.g. 1 cup milk) that get misparsed by other ingredient
# parsers. This is often necessary because formats like mealmaster and
# mastercook are rarely actually followed.
NUMBER_FINDER_REGEXP2 = NUMBER_FINDER_REGEXP.replace('int','int2').replace('frac','frac2')
ING_MATCHER_REGEXP = """
 \s* # opening whitespace
 (?P<amount>
 %(NUMBER_FINDER_REGEXP)s # a number
 \s* # Extra whitespace
 (%(RANGE_REGEXP)s # a possible range delimiter
 \s* #More extra whitespace
 %(NUMBER_FINDER_REGEXP2)s)? # and more numbers
 )? # and of course no number is possible
 \s* # Whitespace between number and unit
 (?P<unit>\s*(%(MULTI_WORD_UNIT_REGEXP)s|[\w.]+))?\s+ # a unit
 (?P<item>.*?)$ # and the rest of our stuff...
 """%locals()

ING_MATCHER = re.compile(ING_MATCHER_REGEXP,
                         re.VERBOSE|re.UNICODE)

ING_MATCHER_AMT_GROUP = 'amount'
ING_MATCHER_UNIT_GROUP = 'unit'
ING_MATCHER_ITEM_GROUP = 'item'

def convert_fractions_to_ascii (s):
    """Convert all unicode-like fractions in string S with their ASCII equivalents"""
    for nums,uni in NUM_TO_FRACTIONS.items():
        s=re.sub(uni,"%s/%s"%(nums[0],nums[1]),s)
    for d in SUB_DICT,SUP_DICT:
        for num,uni in d.items():
            s=re.sub(uni,str(num),s)
    s=re.sub(SLASH,'/',s)
    return s

def fractify (decimal, divisor, approx=0.01, fractions=FRACTIONS_NORMAL):
    """Return fraction equivalent of decimal using divisor

    If we don't have a fit within our approximation, return the
    fraction. Otherwise, return False.
    """
    dividend = integerp(decimal*divisor)
    if dividend:
        if fractions==FRACTIONS_ASCII:
            return "%s/%s"%(dividend,divisor)
        elif fractions==FRACTIONS_ALL:
            # otherwise, we have to do nice unicode magic
            if NUM_TO_FRACTIONS.has_key((dividend,divisor)):
                return NUM_TO_FRACTIONS[(dividend,divisor)]
            else:
                if SUP_DICT.has_key(dividend): dividend = SUP_DICT[dividend]
                if SUB_DICT.has_key(divisor): divisor = SUB_DICT[divisor]
                return '%s%s%s'%(dividend,SLASH,divisor)
        else: # fractions==FRACTIONS_NORMAL
            #fallback to "normal" fractions -- 1/4, 1/2, 3/4 are special
            if (dividend,divisor) in NORMAL_FRACTIONS:
                return NUM_TO_FRACTIONS[(dividend,divisor)]
            else:
                return "%s/%s"%(dividend,divisor)
            
def float_to_frac (n, d=[2,3,4,5,6,8,10,16],approx=0.01,fractions=FRACTIONS_NORMAL):
    """Take a number -- or anything that can become a float --
    and attempt to return a fraction with a denominator in the list `d'. We
    approximate fractions to within approx. i.e. if approx=0.01, then 0.331=1/3"""
    if USE_FRACTIONS == FRACTIONS_OFF:
        return float_to_metric(n)
    else:
        if not n: return ""
        n=float(n)
        i = int(n)
        if i >= 1:
            i="%s"%int(n)
        else:
            i=""
        rem = n - int(n)
        if rem==0:
            if i:
                return "%s"%i
            else:
                return "0"
        else:
            flag = False
            for div in d:
                f = fractify(rem,div,approx=approx,fractions=fractions)
                if f:
                    return " ".join([i,f]).strip()
             # use locale-specific metric formatting if fractions don't work
            return float_to_metric(n)

def float_to_metric(n):
    """Returns a formatted string in metric format, using locale-specific formatting"""    
    if len("%s"%n) > 5:
        return locale.format("%.2f",n,True) # format(formatstring, number, use_thousands_separator)
    else:
        return locale.format("%s",n,True)
    
def float_string (s):
    """Convert string to a float, assuming it is some sort of decimal number

    locale.atof should handle this, but we wrote our own to be a bit more flexible.
    Specifically, we assume most numbers are decimals since recipes calling for
    thousands and thousands of things are rare.
    Also, we recognize items outside of our locale, since e.g. American might well be
    importing British recipes and viceversa.
    """
    if NUMBER_WORDS.has_key(s.lower()):
        print 'We have key',s.lower()
        return NUMBER_WORDS[s.lower()]
    THOUSEP = locale.localeconv()['thousands_sep']
    DECSEP = locale.localeconv()['decimal_point']
    if s.count(',') > 1 and s.count('.') <= 1:
        # if we have more than one comma and less than one .
        # then we assume ,s are thousand-separators
        s=s.replace(',','')
        return float(s)
    elif s.count(',') <= 1 and s.count('.') > 1:
        # if we have more than one . and less than one ,,
        # then we assume . is the thousand-separators
        s=s.replace('.','')
        s=s.replace(',','.')
        return float(s)
    # otherwise let's check if this actually looks like a thousands separator
    # before trusting our locale
    elif re.match('[0-9]+%s[0-9][0-9][0-9]'%THOUSEP,s):
        return locale.atof(s)
    elif THOUSEP and s.find(THOUSEP)>-1 and THOUSEP != '.':
        # otherwise, perhaps our thousand separator is really a
        # decimal separator (we're out of our locale...)
        print 'Warning: assuming %s is a decimal point in %s'%(THOUSEP,s)
        s = s.replace(THOUSEP,'.')
        s = s.replace(',','.') # and remove any commas for good measure
        return float(s)
    else:
        # otherwise just trust our locale float
        return locale.atof(s)

def frac_to_float (s):
    """We assume fractions look like this (I )?N/D"""
    if NUMBER_WORDS.has_key(s): return NUMBER_WORDS[s]
    if hasattr(s,'lower') and NUMBER_WORDS.has_key(s.lower()):
        return NUMBER_WORDS[s.lower()]    
    s = unicode(s)
    m=FRACTION_MATCHER.match(s)
    if m:
        i = m.group('int')
        frac = m.group('frac')
        if i: i=float_string(i)
        else: i = 0
        if UNICODE_FRACTIONS.has_key(frac):
            return i+UNICODE_FRACTIONS[frac]
        elif NUMBER_WORDS.has_key(frac):
            return i+NUMBER_WORDS[frac]
        else:
            n,d = SLASH_MATCHER.split(frac)
            n = SUP_DICT.get(n,n)
            d = SUB_DICT.get(d,d)
            return float(i)+(float(n)/float(d))
    # else...
    try:
        return float_string(s)
    except:
        None
    else:
        #If this isn't a fraction, we're just using float
        try:
            return float_string(s)
        except:
            None



if __name__ == '__main__' and False:
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
        
    
    #i=interactive()
