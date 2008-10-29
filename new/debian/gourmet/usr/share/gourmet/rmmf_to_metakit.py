#!/usr/bin/python

import importer, re, convert, os.path
import rmetakit, check_encodings
from gdebug import debug

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
                          'pk' : 'package',
                          'x' : '',
                          't' : 'tsp.',
                          }
        self.unit_convr = {}
        for k,v in self.unit_conv.items():
            self.unit_convr[v]=k

        

mmf=mmf_constants()
class mmf_importer (importer.importer):
    def __init__ (self,rd,filename='Data/mealmaster.mmf',
                  progress=None, source=None,threaded=True):
        debug("mmf_importer start  __init__ ",5)
        """filename is the file to parse. rd is the recData instance
        to start with.  progress is a function we tell about our
        progress to (we hand it a single arg)."""
        self.rec={}
        self.source=source
        self.header=False
        self.instr=""
        self.ingrs=[]
        self.ing_added=False
        self.compile_regexps()
        self.fn = filename
        self.progress = progress
        importer.importer.__init__(self,rd=rd,threaded=threaded)        

    def run (self):
        #self.file=open(self.fn,'r')
        self.base=os.path.split(self.fn)[1]
        #ll=self.file.readlines() #slurp
        ll = check_encodings.get_file(self.fn)
        tot=len(ll)
        for n in range(tot):
            # we do the loop this way so we can
            # conveniently report our progress to
            # the outside world :)
            l=ll[n]
            # we update our progress bar every 15 lines
            if n % 15 == 0:
                prog= float(n)/float(tot)
                #print "DEBUG: progress=",prog
                if self.progress:
                    self.progress(prog)
            self.handle_line(l)
        # commit the last recipe if need be
        if self.rec:
            self._commit_rec()

    def compile_regexps (self):
        debug("start compile_regexps",5)
        self.start_matcher = re.compile("^([M-][M-][M-][M-][M-])-*\s*(Recipe|[Mm]eal-?[Mm]aster).*")
        self.end_matcher = re.compile("^[M-][M-][M-][M-][M-]\s*$")
        self.group_matcher = re.compile("^([M-][M-][M-][M-][M-])-*\s*([^-]+)\s*-*")
        self.blank_matcher = re.compile("^\s*$")
        self.ing_cont_matcher = re.compile("^\s*[-;]")
        self.ing_opt_matcher = re.compile("(.+?)\s*\(?\s*[Oo]ptional\)?\s*$")
        self.ing_or_matcher = re.compile("^[- ]*[Oo][Rr][- ]*$")
        # a crude ingredient matcher -- we look for two numbers, intermingled with spaces
        # followed by a space or more, followed by a two digit unit (or spaces)
        self.ing_num_matcher = re.compile("^\s*[0-9]+[0-9/ -]+\s+[A-Za-z ][A-Za-z ] .*")
        # we build a regexp to match anything that looks like
        # this: ^\s*ATTRIBUTE: Some entry of some kind...$
        attrmatch="^\s*("
        for k in mmf.recattrs.keys():
            attrmatch += "%s|"%re.escape(k)
        attrmatch="%s):\s*(.*)\s*$"%attrmatch[0:-1]
        self.attr_matcher = re.compile(attrmatch)

    def handle_line (self,l):
        """We're quite loose at handling mealmaster files. We look at
        each line and determine what it is most likely to be: ingredients
        and instructions can be intermingled: instructions will simply be
        added to the instructions and ingredients to the ingredient list.
        This may result in loss of information (for instructions that specifically
        follow ingredients) or in mis-parsing (for instructions that look like
        ingredients). But we're following, more or less, the specs laid out
        here <http://phprecipebook.sourceforge.net/docs/MM_SPEC.DOC>"""
        debug("start handle_line",10)
        if self.start_matcher.match(l):
            #print "DEBUG: New recipe"
            debug("recipe start %s"%l,4)
            self.new_rec()
            return
        if self.end_matcher.match(l):
            debug("recipe end %s"%l,4)            
            self._commit_rec()
            return
        groupm = self.group_matcher.match(l)
        if groupm:
            debug("new group %s"%l,4)            
            self.handle_group(groupm)
            return
        attrm = self.attr_matcher.match(l)
        if attrm:        
            # a match for an attribute has two groups,
            # (ATTRIBUTE): (VALUE)
            attr,val = attrm.groups()
            debug("attribute %s (%s:%s)"%(l,attr,val),4)
            self.rec[mmf.recattrs[attr]]=val.strip()
            return

        if not self.instr and self.blank_matcher.match(l):
            debug('ignoring blank line before instructions',4)
            return
        
        if self.is_ingredient(l):
            contm = self.ing_cont_matcher.match(l)
            if contm and self.ingrs:
                debug('continuing %s'%self.ingrs[-1][0],4)
                continuation = " %s"%l[contm.end():].strip()
                self.ingrs[-1][0] += continuation
            else:
                self.ingrs.append([l,self.group])
        else:
            ## otherwise, we assume a line of instructions
            debug('Adding to instructions: %s'%l,4)
            self.instr += l

    def is_ingredient (self, l):
        """We're going to go with a somewhat hackish approach
        here. Once we have the ingredient list, we can determine
        columns more appropriately.  For now, we'll assume that a
        field that starts with at least 5 blanks (the specs suggest 7)
        or a field that begins with a numeric value is an ingredient"""
        if self.ing_num_matcher.match(l):
            return True
        if len(l) > 5 and self.blank_matcher.match(l[0:5]):
            return True

    def new_rec (self):
        debug("start new_rec",5)
        if self.rec:
            # this shouldn't happen if recipes are ended properly
            # but we'll be graceful if a recipe starts before another
            # has ended... 
            self._commit_rec()
        self.committed=False
        self.start_rec(base=self.base)
        debug('resetting instructions',5)
        self.instr=""
        self.ingrs=[]
        self.header=False

    def _commit_rec (self):
        if self.committed: return
        debug("start _commit_rec",5)
        self.rec['instructions']=self.instr
        self.parse_inglist()
        if self.source:
            self.rec['source']=self.source
        self.commit_rec()
        # blank rec
        self.committed = True

    def handle_group (self, groupm):
        debug("start handle_group",10)
        # the only group of the match will contain
        # the name of the group. We'll put it into
        # a more sane title case (MealMaster defaults
        # to all caps
        name = groupm.groups()[1].title()
        self.group=name
        # a blank line before a group could fool us into thinking
        # we were in instructions. If we see a group heading,
        # we know that's not the case!

    def find_ing_fields (self):
        debug("start find_ing_fields",7)
        all_ings = map(lambda tupl: tupl[0], self.ingrs)
        fields = find_fields(all_ings)        
        a = []
        while fields and field_match(all_ings,fields[0],
                                     "^[0-9- /]+$"):
            # amounts are 
            a.append(fields[0])
            del fields[0]
        if a:
            a=(a[0][0],a[-1][1]) #a is the range from least to most
        if fields and field_match(all_ings,fields[0],
                                  "^..?$"):
            u=fields[0]
            del fields[0]
        else: u=""
        if fields:
            i=(fields[0][0],fields[-1][1])
        else:
            debug("No items? this seems odd.",0)
            i=""
        debug("Returning fields: %s,%s,%s"%(a,u,i),10)
        return a,u,i
            
    def add_item (self, item):
        self.ing['item']=item.strip()
        # fixing bug 1061363, potatoes; cut and mashed should become just potatoes
        # for keying purposes
        key_base = self.ing['item'].split(";")[0]
        self.ing['key']=self.km.get_key(key_base,0.9)

    def parse_inglist(self):
        debug("start parse_inglist",5)
        """We handle our ingredients after the fact."""
        afield,ufield,ifield=self.find_ing_fields()
        debug("ingredient fields are: %s,%s,%s"%(afield,ufield,ifield),10)
        for s,g in self.ingrs:
            self.start_ing()
            self.group = g
            amt,u,i = get_fields(s,(afield,ufield,ifield))
            if amt:
                self.add_amt(amt)
            if u:
                self.add_unit(u)
            optm=self.ing_opt_matcher.match(i)
            if optm:
                item=optm.groups()[0]
                self.add_item(item)
                self.ing['optional']='yes'
            #elif self.ing_or_matcher.match(i):
            #    ?
            else:
                self.add_item(i)
            debug("committing ing: %s"%self.ing,6)
            self.commit_ing()
                

def split_fields (strings, char=" "):
    debug("start split_fields",10)
    fields=find_fields(strings,char)

def field_match (strings, tuple, matcher):
    debug("start field_match",10)
    if type(matcher)==type(""):
        matcher=re.compile(matcher)
    for s in strings:
        f=s[tuple[0]:tuple[1]]
        if not matcher.match(f):
            return False
    return True

def get_fields (string, tuples):
    debug("start get_fields",10)
    lst = []
    for t in tuples:
        if t:
            lst.append(string[t[0]:t[1]])
        else:
            lst.append("")
    return lst

def field_width (tuple):
    debug("start field_width",10)
    if tuple[1]:
        return tuple[1]-tuple[0]
    else:
        return None

def find_fields (strings, char=" "):
    debug("start find_fields",10)
    cols=find_columns(strings, char)
    if not cols:
        return
    fields = []
    if cols[0] > 0:
        fields.append((0,cols[0]))
    range_start = None
    for n in range(cols[0],cols[-1]+1):
        if n not in cols:
            if not range_start: range_start = n
        else:
            if range_start:
                fields.append((range_start,n))
                range_start=None
    if range_start: fields.append((range_start,None))
    else: fields.append((cols[-1]+1,None))
    return fields
            
def find_columns (strings, char=" "):
    debug("start find_columns",10)
    # we start with the columns in the first string
    if not strings:
        return None
    columns = map(lambda match: match.start(),re.finditer(re.escape(char),strings[0]))
    if len(strings)==1:
        return columns
    # we eliminate all columns that aren't blank for every string
    for s in strings:
        for c in columns[0:]: # we'll be modifying columns
            if c < len(s) and s[c]!=char:
                columns.remove(c)
    columns.sort()
    return columns

        
if __name__ == '__main__':
    def printprog (prog):
        print "%i percent done"%(prog * 100)
    mmf_importer(rmetakit.recipeManager(),'/home/tom/Projects/MM132501',
                 progress=printprog, source="MM132501")
