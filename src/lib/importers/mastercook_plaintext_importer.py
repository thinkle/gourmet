import importer, re, string
from gourmet import check_encodings
from gourmet.gdebug import *
from gettext import gettext as _

class mastercook_importer (importer.importer):
    ATTR_DICT = {'Recipe By':'source',
                 'Serving Size':'servings',
                 'Preparation Time':'preptime',
                 'Categories':'category',
                 }
    def __init__ (self, file, rd, progress=None, threaded=False):
        print 'rd=',rd,' file=',file
        self.fn = file
        self.rec = {}
        self.ing = {}
        self.progress = progress
        self.compile_regexps()
        self.instr = ""
        self.in_ings = False
        self.in_instructions = False
        self.in_or = False
        self.looking_for_title = False
        self.last_attr = ""
        self.in_attrs=False
        self.in_mods=False
        importer.importer.__init__(self,rd,threaded=threaded)
        
    def run (self):
        ll = check_encodings.get_file(self.fn)
        tot=len(ll)
        for n in range(tot):
            l=ll[n]
            if self.progress:
                if n % 15 == 0:
                    prog = float(n)/float(tot)
                    msg = _("Imported %s recipes.")%(len(self.added_recs))
                    self.progress(prog,msg)
            self.handle_line(l)
        # commit the last rec if need be
        if self.rec:
            self.commit_rec()
        importer.importer.run(self)

    def compile_regexps (self):
        self.rec_start_matcher = re.compile("^\s*\*\s*Exported\s*from\s*MasterCook\s*\*\s*$")
        self.blank_matcher = re.compile("^\s*$")
        self.rec_col_matcher = re.compile("(\s*Amount\s*)(Measure\s*)(Ingredient.*)")
        # match a string enclosed in a possibly repeated non-word character
        # such as *Group* or ---group--- or =======GROUP======
        # grabbing groups()[1] will get you the enclosed string
        self.dash_matcher = re.compile("^[ -]*[-][- ]*$")
        self.ing_or_matcher = re.compile("\W*[Oo][Rr]\W*")
        self.ing_group_matcher = re.compile("\s*(\W)\\1*(.+?)(\\1+)")
        self.mods_matcher = re.compile("^\s*NOTES\.*")
        attr_matcher = "\s*(" + string.join(self.ATTR_DICT.keys(),"|") + ")\s*:(.*)"
        self.attr_matcher = re.compile(attr_matcher)
        
    def handle_line (self, line):
        if self.dash_matcher.match(line): return
        if self.rec_start_matcher.match(line):
            debug('rec_start! %s'%line,0)
            self.looking_for_title = True
            if self.rec: self.commit_rec()
            self.instr = ""
            self.mods = ""
            self.in_instructions=False
            self.in_mods = False
            self.in_ings = False
            self.in_attrs = False
            self.start_rec()
            return
        rcm=self.rec_col_matcher.match(line)
        if rcm:
            debug('Found ing columns',0)
            self.looking_for_title=False
            self.in_attrs=False
            self.last_attr = ""
            self.get_ing_cols(rcm)
            self.in_ings = True
            return
        if self.blank_matcher.match(line):            
            # blank line ends ingredients
            if self.in_ings:
                debug('blank line, end of ings',0)
                self.in_ings = False
                self.in_instructions = True
                if self.ing: self.commit_ing()
            if self.in_instructions:
                debug('blank line added to instructions: %s'%line,0)
                if self.in_mods: self.mods += "\n"
                else: self.instr+="\n"
        elif self.looking_for_title:
            debug('found my title! %s'%line.strip(),0)
            self.rec['title']=line.strip()
            self.looking_for_title = False
            self.in_attrs=True
            return
        elif self.in_ings:
            debug('handling ingredient line %s'%line,0)
            self.handle_ingline (line)
            return
        elif self.in_attrs:
            debug('handing attrline %s'%line,0)
            self.handle_attribute(line)
        else:
            self.in_instructions = True
            if self.mods_matcher.match(line):
                self.in_mods = True
            if self.in_mods:
                debug('handling modifications line %s'%line,0)
                self.add_to_attr('mods',line)
            else:
                debug('handling instructions line %s'%line,0)
                self.add_to_attr('instr',line)

    def add_to_attr (self, attr, txt):
        orig = getattr(self,attr)
        if orig:
            if len(txt.strip()) < 50:
                setattr(self,attr,orig+"%s\n"%txt.strip())
            elif not self.blank_matcher.match(orig[-1]):
                setattr(self,attr,orig+" %s"%txt.strip())
            else:
                setattr(self,attr,orig+txt.strip())
        else:
            setattr(self,attr,txt)

    def get_ing_cols (self,rcm):
        amt,unit,itm=rcm.groups()
        lamt,lunit,litm = len(amt),len(unit),len(itm)
        self.amt_col = 0,lamt
        self.unit_col = lamt,lamt+lunit
        self.itm_col = lamt+lunit,None

    def handle_attribute (self,line):
        m=self.attr_matcher.match(line)
        if m:            
            attr,val = m.groups()
            SecndColMatch = self.attr_matcher.search(val)
            if SecndColMatch:
                s=SecndColMatch.start()
                self.handle_attribute(val[s:])
                val = val[:s]
            val = self.join_multiple_attvals(val.strip())
            attr = attr.strip()
            self.last_attr = self.ATTR_DICT[attr]
            self.rec[self.ATTR_DICT[attr]]=val
        else:            
            if self.last_attr:
                # attribute values can run over one line...
                self.rec[self.last_attr]=string.join([self.rec[self.last_attr],
                                                      self.join_multiple_attvals(line.strip())
                                                      ], ", ")
            else:
                # otherwise, we add this to instructions, like we do with all junk
                self.instr += line

    def join_multiple_attvals (self, txt):
        """We take replace more than one space with a comma."""
        return string.join(filter(lambda x: x, txt.split("  ")),", ")

    def handle_ingline (self,line):
        if self.ing_or_matcher.match(line):
            self.in_or = True
            return
        amt = line.__getslice__(*self.amt_col).strip()
        unit = line.__getslice__(*self.unit_col).strip()
        itm = line[self.itm_col[0]:].strip()
        gm=self.ing_group_matcher.match(itm)
        if gm:
            if self.ing: self.commit_ing()
            self.group = gm.groups()[1]
            return
        if amt or unit:
            if self.in_or: self.ing['optional']='yes'
            if self.ing: self.commit_ing()
            self.start_ing()
            if self.in_or:
                self.ing['optional']='yes'
                self.in_or = False
            self.add_amt(amt)
            self.add_unit(unit)
            self.add_item(itm)
            return
        elif self.ing and self.ing.has_key('item'):
            # otherwise, we assume we are a continuation and
            # add onto the previous item
            self.ing['item']=self.ing['item']+' '+itm.strip()
        else:
            print '"%s" in the midst of ingredients looks like instructions!'%itm.strip()
            self.instr += "\n"+itm.strip()

    def commit_ing (self):
        if not self.ing.has_key('item'):
            print 'wtf, ingredient has no item!'
            print 'self.ing=',self.ing
            return
        key_base = self.ing['item'].split('--')[0]
        self.ing['ingkey']=self.km.get_key_fast(key_base)
        importer.importer.commit_ing(self)
        self.ing = {}

    def commit_rec (self):
        self.rec['instructions']=self.instr
        self.rec['modifications']=self.mods
        importer.importer.commit_rec(self)
        
class Tester (importer.Tester):
    def __init__ (self):
        importer.Tester.__init__(self,regexp='\s*\*\s*Exported\s*from\s*MasterCook\s*\*\s*')
        self.not_me = "<[?]?(xml|mx2|RcpE|RTxt)[^>]*>"

    def test (self, filename):
        if not hasattr(self,'matcher'):
            self.matcher=re.compile(self.regexp)
            self.not_matcher = re.compile(self.not_me)
        self.ofi = open(filename,'r')
        l = self.ofi.readline()
        while l:
            if self.not_matcher.match(l):
                self.ofi.close()
                return False
            if self.matcher.match(l):
                self.ofi.close()
                return True
            l = self.ofi.readline()
        self.ofi.close()
