#!/usr/bin/python
import importer, plaintext_importer
import re, os.path, string, array
from gourmet import convert, check_encodings
from gourmet.gdebug import debug,TimeAction
from gourmet.gglobals import gt
from gettext import gettext as _

class mmf_constants:
    def __init__ (self):
        self.committed = False
        self.recattrs={'Title':'title',
                       'Categories':'category',
                       'Servings':'servings',
                       'Source':'source',
                       'Recipe by':'source',
                       'Yield':'servings',
                       'Preparation Time':'preptime',
                       }
        
        self.unit_conv = {'ts':'tsp.',
                          'tb':'tbs.',
                          'sm':'small',
                          'md':'medium',
                          'ea':'',
                          'lg':'large',
                          'c':'c.',
                          'pn':'pinch',
                          'ds':'dash',
                          'T' : 'tbs.',
                          't' : 'tsp.',
                          'pk' : 'package',
                          'x' : '',
                          'ea' : '',
                          't' : 'tsp.',
                          'pt' : 'pt.',
                          'qt' : 'qt.',
                          'oz' : 'oz.'
                          }
        self.unit_convr = {}
        for k,v in self.unit_conv.items():
            self.unit_convr[v]=k

mmf=mmf_constants()
mm_start_pattern=r"^(?i)([m-][m-][m-][m-][m-])-*.*(recipe|meal-?master).*"

class mmf_importer (plaintext_importer.TextImporter):

    """Mealmaster(tm) importer class.

    We read in a text file a line at a time and parse
    attributes/ingredients/instructions as best we can.

    We're following, more or less, the specs laid out here
    <http://phprecipebook.sourceforge.net/docs/MM_SPEC.DOC>

    The problem with Mealmaster(tm) files is that they rarely conform
    to the above spec.  So, we are a bit more flexible -- we can
    handle one or two columns of ingredients for example. However,
    it's hard to handle all cases. Also, mealmaster (as described in
    the above spec) allows for essentially a continuous flow of text
    with ingredient and text blocks interspersed. Gourmet separates
    out the ingredients from the instructions, which means that we
    have to change the presentation of mealmaster files when they
    intersperse instructions and ingredients.

    To allow for this flexibility also means we are less flexible
    about both instructions and ingredients: instructions that look
    like ingredients or ingredients that look like instructions will
    be parsed the wrong way, regardless of their position in the file,
    since the spec above does not specify that mealmaster files must
    follow the normal pattern.

    The result is that anyone importing large numbers of mealmaster
    files from various internet sources should expect to tweak files
    by hand with some frequency.
    """

    committed = False
    
    def __init__ (self,rd,filename='Data/mealmaster.mmf',
                  progress=None, source=None,threaded=True,
                  two_col_minimum=38,conv=None):
        """filename is the file to parse (or filename). rd is the recData instance
        to start with.  progress is a function we tell about our
        progress to (we hand it a single arg)."""

        testtimer = TimeAction('mealmaster_importer.__init__',10)
        debug("mmf_importer start  __init__ ",5)
        self.source=source
        self.header=False
        self.instr=""
        self.ingrs=[]
        self.ing_added=False
        self.in_variation=False
        self.fn = filename
        self.progress = progress
        self.unit_length = 2
        self.two_col_minimum = two_col_minimum
        self.last_line_was = None
        plaintext_importer.TextImporter.__init__(self,filename,rd,progress=progress,
                                                 threaded=threaded,conv=conv)
        testtimer.end()
        
    def compile_regexps (self):
        testtimer = TimeAction('mealmaster_importer.compile_regexps',10)
        debug("start compile_regexps",5)
        plaintext_importer.TextImporter.compile_regexps(self)
        self.start_matcher = re.compile(mm_start_pattern)
        self.end_matcher = re.compile("^[M-][M-][M-][M-][M-]\s*$")
        self.group_matcher = re.compile("^\s*([M-][M-][M-][M-][M-])-*\s*([^-]+)\s*-*",re.IGNORECASE)
        self.ing_cont_matcher = re.compile("^\s*[-;]")
        self.ing_opt_matcher = re.compile("(.+?)\s*\(?\s*optional\)?\s*$",re.IGNORECASE)
        self.ing_or_matcher = re.compile("^[- ]*[Oo][Rr][- ]*$",re.IGNORECASE)
        self.variation_matcher = re.compile("^\s*(VARIATION|HINT|NOTES?)(:.*)?",re.IGNORECASE)
        # a crude ingredient matcher -- we look for two numbers,
        # intermingled with spaces followed by a space or more,
        # followed by a two digit unit (or spaces)
        self.ing_num_matcher = re.compile(
            "^\s*%s+\s+[a-z ]{1,2}\s+.*\w+.*"%convert.NUMBER_REGEXP,
            re.IGNORECASE)
        self.amt_field_matcher = re.compile("^(\s*%s\s*)$"%convert.NUMBER_REGEXP)
        # we build a regexp to match anything that looks like
        # this: ^\s*ATTRIBUTE: Some entry of some kind...$
        self.mmf = mmf
        attrmatch="^\s*("
        for k in self.mmf.recattrs.keys():
            attrmatch += "%s|"%re.escape(k)
        attrmatch="%s):\s*(.*)\s*$"%attrmatch[0:-1]
        self.attr_matcher = re.compile(attrmatch)
        testtimer.end()
        
    def handle_line (self,l):

        """Handle an individual line of a mealmaster file.

        We're quite loose at handling mealmaster files. We look at
        each line and determine what it is most likely to be:
        ingredients and instructions can be intermingled: instructions
        will simply be added to the instructions and ingredients to
        the ingredient list.  This may result in loss of information
        (for instructions that specifically follow ingredients) or in
        mis-parsing (for instructions that look like ingredients). But
        we're following, more or less, the specs laid out here
        <http://phprecipebook.sourceforge.net/docs/MM_SPEC.DOC>"""
        
        testtimer =TimeAction('mealmaster_importer.handle_line',10)
        debug("start handle_line",10)
        gt.gtk_update()
        if self.start_matcher.match(l):
            debug("recipe start %s"%l,4)
            self.new_rec()
            self.last_line_was = 'new_rec'
            self.in_variation = False
            return
        if self.end_matcher.match(l):
            debug("recipe end %s"%l,4)
            self.commit_rec()
            self.last_line_was = 'end_rec'
            return
        groupm = self.group_matcher.match(l)
        if groupm:
            debug("new group %s"%l,4)
            self.handle_group(groupm)
            self.last_line_was = 'group'
            return
        attrm = self.attr_matcher.match(l)
        if attrm:
            debug('Found attribute in %s'%l,4)
            attr,val = attrm.groups()
            debug("Writing attribute, %s=%s"%(attr,val),4)
            self.rec[self.mmf.recattrs[attr]]=val.strip()
            self.last_line_was = 'attr'
            return
        if not self.instr and self.blank_matcher.match(l):
            debug('ignoring blank line before instructions',4)
            self.last_line_was = 'blank'
            return
        if self.variation_matcher.match(l):
            debug('in variation',4)
            self.in_variation = True
        if self.is_ingredient(l) and not self.in_variation:
            debug('in ingredient',4)
            contm = self.ing_cont_matcher.match(l)
            if contm:
                # only continuations after ingredients are ingredients
                if self.ingrs and self.last_line_was == 'ingr':
                    debug('continuing %s'%self.ingrs[-1][0],4)
                    continuation = " %s"%l[contm.end():].strip()
                    self.ingrs[-1][0] += continuation
                    self.last_line_was = 'ingr'
                else:
                    self.instr += l
                    self.last_line_was = 'instr'
            else:
                self.last_line_was = 'ingr'
                self.ingrs.append([l,self.group])
        else:
            ## otherwise, we assume a line of instructions
            if self.last_line_was == 'blank': add_blank=True
            else: add_blank = False
            if self.in_variation:
                debug('Adding to instructions: %s'%l,4)
                self.last_line_was = 'mod'
                add_to = 'mod'
            else:
                debug('Adding to modifications: %s'%l,4)
                self.last_line_was = 'instr'
                add_to = 'instr'
            if getattr(self,add_to):
                if add_blank: setattr(self,add_to,
                                      getattr(self,add_to)+"\n")
                setattr(self,add_to,
                        getattr(self,add_to) + l.strip() + "\n")
            else:
                setattr(self,add_to,
                        l.strip() + "\n")
        testtimer.end()
                
    def is_ingredient (self, l):
        """Return true if the line looks like an ingredient.

        We're going to go with a somewhat hackish approach
        here. Once we have the ingredient list, we can determine
        columns more appropriately.  For now, we'll assume that a
        field that starts with at least 5 blanks (the specs suggest 7)
        or a field that begins with a numeric value is an ingredient"""
        testtimer = TimeAction('mealmaster_importer.is_ingredient',10)
        if self.ing_num_matcher.match(l):
            testtimer.end()
            return True
        if len(l) >= 7 and self.blank_matcher.match(l[0:5]):
            testtimer.end()
            return True
        
    def new_rec (self):
        """Start a new recipe."""
        testtimer = TimeAction('mealmaster_importer.new_rec',10)
        debug("start new_rec",5)
        if self.rec:
            # this shouldn't happen if recipes are ended properly
            # but we'll be graceful if a recipe starts before another
            # has ended... 
            self.commit_rec()
        self.committed=False
        self.start_rec()
        debug('resetting instructions',5)
        self.instr=""
        self.mod = ""
        self.ingrs=[]
        self.header=False
        testtimer.end()

    def commit_rec (self):
        """Commit our recipe to our database."""
        testtimer = TimeAction('mealmaster_importer.commit_rec',10)
        if self.committed: return
        debug("start _commit_rec",5)
        self.instr = self.unwrap_lines(self.instr)
        self.mod = self.unwrap_lines(self.mod)
        self.rec['instructions']=self.instr
        if self.mod:
            self.rec['modifications']=self.mod
        self.parse_inglist()
        if self.source:
            self.rec['source']=self.source
        importer.Importer.commit_rec(self)
        # blank rec
        self.committed = True
        self.in_variation=False
        testtimer.end()
        
    def handle_group (self, groupm):
        """Start a new ingredient group."""
        testtimer = TimeAction('mealmaster_importer.handle_group',10)
        debug("start handle_group",10)
        # the only group of the match will contain
        # the name of the group. We'll put it into
        # a more sane title case (MealMaster defaults
        # to all caps
        name = groupm.groups()[1].title()
        self.group=name
        if re.match('^[^A-Za-z]*$',self.group): self.group=None
        testtimer.end()
        # a blank line before a group could fool us into thinking
        # we were in instructions. If we see a group heading,
        # we know that's not the case!

    def find_ing_fields (self):
        """Find fields in an ingredient line."""
        testtimer = TimeAction('mealmaster_importer.find_ing_fields',10)
        all_ings = [i[0] for i in self.ingrs]
        fields = find_fields(all_ings)
        fields_is_numfield = fields_match(all_ings,fields,self.amt_field_matcher)
        #fields = [[r,field_match(all_ings,r,self.amt_field_matcher)] for r in find_fields(all_ings)]
        aindex,afield = self.find_amt_field(fields,fields_is_numfield)
        if aindex != None:
            fields = fields[aindex+1:]
            fields_is_numfield = fields_is_numfield[aindex+1:]
        ufield = fields and self.find_unit_field(fields,fields_is_numfield)
        if ufield:
            fields = fields[1:]
            fields_is_numfield = fields_is_numfield[1:]
        if fields:
            ifield = [fields[0][0],None]
        else:
            ifield = 0,None
        retval = [[afield,ufield,ifield]]
        sec_col_fields = filter(lambda x: x[0]>self.two_col_minimum,fields)        
        if sec_col_fields:
            ibase = fields.index(sec_col_fields[0])
            while sec_col_fields and not fields_is_numfield[ibase]:
                ibase += 1
                sec_col_fields = sec_col_fields[1:]
                # if we might have a 2nd column...
        if sec_col_fields and len(sec_col_fields) > 2:            
            fields_is_numfield = fields_is_numfield[ibase:]
            aindex2,afield2 = self.find_amt_field(sec_col_fields,fields_is_numfield)
            if aindex2 != None and len(sec_col_fields[aindex2+1:]) >= 1:
                # then it's a go! Shift our first ifield
                retval[0][2]=[ifield[0],fields[ibase-1][1]]
                sec_col_fields = sec_col_fields[aindex2 + 1:]
                fields_is_numfield = fields_is_numfield[aindex2+1:]
                ufield2 = self.find_unit_field(sec_col_fields,fields_is_numfield)
                if ufield2:
                    sec_col_fields=sec_col_fields[1:]
                    fields_is_numfield = fields_is_numfield[1:]
                ifield2 = sec_col_fields[0][0],None
                retval.append([afield2,ufield2,ifield2])
        testtimer.end()
        return retval
        
    def find_unit_field (self, fields, fields_is_numfield):
        testtimer = TimeAction('mealmaster_importer.find_unit_field',10)
        if 0 < fields[0][1]-fields[0][0] <= self.unit_length and len(fields)>1:
            testtimer.end()
            return fields[0]
        testtimer.end()
        
    def find_amt_field (self, fields, fields_is_numfield):
        """Return amount field and field index for the last amount field.

        In other words, if we the following fields...

        0 1   2  3     4      5       6  7
        1 1/2 ts green onions chopped in 1/2

        ...we will return the index for our first two fields [1] and
        we will return the field corresponding to the first two fields
        (0,5)
        """
        afield = None
        aindex = None
        for i,f in enumerate(fields):
            # if our field is a numeric field...
            if fields_is_numfield[i]:
                if not afield:
                    afield = f
                    aindex = i
                # if we our contiguous
                elif i == aindex + 1:
                    afield = [afield[0],f[1]] # give it a new end
                    aindex = i
                else:
                    return aindex,afield
        return aindex, afield

    def add_item (self, item):
        testtimer = TimeAction('mealmaster_importer.add_item',10)
        self.ing['item']=item.strip()
        # fixing bug 1061363, potatoes; cut and mashed should become just potatoes
        # for keying purposes
        key_base = self.ing['item'].split(";")[0]
        self.ing['ingkey']=self.km.get_key_fast(key_base)
        testtimer.end()
        
    def parse_inglist(self):
        testtimer = TimeAction('mealmaster_importer.parse_inglis',10)
        debug("start parse_inglist",5)
        """We handle our ingredients after the fact."""
        ingfields =self.find_ing_fields()
        debug("ingredient fields are: %s"%ingfields,10)
        for s,g in self.ingrs:
            for afield,ufield,ifield in ingfields:
                self.group = g
                amt,u,i = get_fields(s,(afield,ufield,ifield))
                debug("""amt:%(amt)s
                u:%(u)s
                i:%(i)s"""%locals(),0)
                # sanity check...
                if not amt.strip() and not u.strip():
                    if not i: continue
                    # if we have not amt or unit, let's do the right
                    # thing if this just looks misaligned -- in other words
                    # if the "item" column has 2 c. parsley, let's just parse
                    # the damned thing as 2 c. parsley
                    parsed = self.rd.parse_ingredient(i,conv=self.conv,get_key=False)
                    if parsed and parsed.get('amount','') and parsed.get('item',''):
                        amt = "%s"%parsed['amount']
                        u = parsed.get('unit','')
                        i = parsed['item']
                        debug("""After sanity check
                        amt:%(amt)s
                        u:%(u)s
                        i:%(i)s"""%locals(),0)
                if amt.strip() or u.strip() or i.strip():
                    self.start_ing()
                    if amt:
                        self.add_amt(amt)
                    if u:
                        self.add_unit(u)
                    optm=self.ing_opt_matcher.match(i)
                    if optm:
                        item=optm.groups()[0]
                        self.ing['optional']=True
                    else:
                        item = i
                    self.add_item(item)
                    debug("committing ing: %s"%self.ing,6)
                    self.commit_ing()
        testtimer.end()
                    
    def add_unit (self, unit):
        testtimer = TimeAction('mealmaster_importer.add_unit',10)
        unit = unit.strip()
        if self.mmf.unit_conv.has_key(unit):
            unit = self.mmf.unit_conv[unit]
        importer.Importer.add_unit(self,unit)
        testtimer.end()

def split_fields (strings, char=" "):
    testtimer = TimeAction('mealmaster_importer.split_fields',10)
    debug("start split_fields",10)
    fields=find_fields(strings,char)
    testtimer.end()
    
def fields_match (strings, fields, matcher):
    testtimer = TimeAction('mealmaster_importer.fields_match',10)
    """Return an array of True or False values representing
    whether matcher is a match for each of fields in string."""
    #retarray = array.array('H',[1]*len(fields))
    ret = []
    for f in fields:
        strs = [s[f[0]:f[1]] for s in strings]
        matches = [matcher.match(s) and True or False for s in strs]
        if True in matches: ret.append(1)
        else: ret.append(0)
    return ret
    #return array.array('H',[True in [matcher.match(s[f[0]:f[1]]) and 1 or 0 for s in strings] for f in fields])
    
    # cycle through each string broken into our fields
    #for ff in [[s[f[0]:f[1]] for f in fields] for s in strings]:
    #    for i,fld in enumerate(ff):
    #        if fld and retarray[i] and not matcher.match(fld):
    #            retarray[i]=False
    #            if not True in retarray: return retarray
    #testtimer.end()
    #return retarray


def field_match (strings, tup, matcher):
    testtimer = TimeAction('mealmaster_importer.field_match',10)
    debug("start field_match",10)
    if type(matcher)==type(""):
        matcher=re.compile(matcher)
    for f in [s[tup[0]:tup[1]] for s in strings]:
        #f=s[tup[0]:tup[1]]
        if f and not matcher.match(f):
            testtimer.end()
            return False
    testtimer.end()
    return True


def get_fields (string, tuples):
    testtimer = TimeAction('mealmaster_importer.get_fields',10)
    debug("start get_fields",10)
    lst = []
    for t in tuples:
        if t:
            lst.append(string[t[0]:t[1]])
        else:
            lst.append("")
    testtimer.end()
    return lst


def field_width (tuple):
    testtimer = TimeAction('mealmaster_importer.field_width',10)
    debug("start field_width",10)
    if tuple[1]:
        testtimer.end()
        return tuple[1]-tuple[0]
    else:
        testtimer.end()
        return None
    
    
def find_fields (strings, char=" "):
    testtimer = TimeAction('mealmaster_importer.find_fields',10)
    cols = find_columns(strings, char)
    if not cols: return []
    cols.reverse()
    fields = []
    lens = map(len,strings)
    lens.sort()
    end = lens[-1]
    last_col = end
    for col in cols:
        if col == last_col - 1:
            end = col
        else:
            fields.append([col+1,end])
            end = col
        last_col = col
    if end != 0: fields.append([0,end])
    fields.reverse()
    testtimer.end()
    return fields


def find_columns (strings, char=" "):
    testtimer = TimeAction('mealmaster_importer.find_columns',10)
    """Return a list of character indices that match char for each string in strings."""
    debug("start find_columns",10)
    # we start with the columns in the first string
    if not strings:
        return None
    strings=strings[0:]
    strings.sort(lambda x,y: len(x)>len(y))
    columns = [match.start() for match in re.finditer(re.escape(char),strings[0])]
    if len(strings)==1:
        return columns
    # we eliminate all columns that aren't blank for every string
    for s in strings:
        for c in columns[0:]: # we'll be modifying columns
            if c < len(s) and s[c]!=char:
                columns.remove(c)
    columns.sort()
    testtimer.end()
    return columns


        
if __name__ == '__main__':
    import gourmet.recipeManager as recipeManager
    import tempfile, sys, profile, os.path
    from gourmet.OptionParser import *
    print 'Testing MealMaster import'
    tmpfile = tempfile.mktemp()
    import backends.rmetakit
    rd = backends.rmetakit.RecipeManager(tmpfile)
    if not args: args = ['/home/tom/Projects/recipe/Data/200_Recipes.mmf']
    for a in args:
        profi = os.path.join(tempfile.tempdir,'MMI_PROFILE')
        profile.run("mmf_importer(rd,a,progress=lambda *args: sys.stdout.write('|'),threaded=False)",
                    profi)
        import pstats
        p = pstats.Stats(profi)
        p.strip_dirs().sort_stats('cumulative').print_stats()
        
    
