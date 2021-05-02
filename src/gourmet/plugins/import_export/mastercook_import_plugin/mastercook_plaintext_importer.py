import re

from gourmet import check_encodings
from gourmet.gdebug import debug
from gourmet.importers import importer, plaintext_importer

MASTERCOOK_START_REGEXP=r'\s*\*\s*Exported\s*from\s*MasterCook.*\*\s*'

class MastercookPlaintextImporter (plaintext_importer.TextImporter):
    ATTR_DICT = {'Recipe By':'source',
                 'Serving Size':'servings',
                 'Preparation Time':'preptime',
                 'Categories':'category',
                 }
    def __init__ (self, filename):
        self.compile_regexps()
        self.instr = ""
        self.in_ings = False
        self.in_instructions = False
        self.in_or = False
        self.looking_for_title = False
        self.last_attr = ""
        self.in_attrs=False
        self.in_mods=False
        self.reccol_headers = False
        plaintext_importer.TextImporter.__init__(self,filename)

    def compile_regexps (self):
        plaintext_importer.TextImporter.compile_regexps(self)
        self.rec_start_matcher = re.compile(MASTERCOOK_START_REGEXP)
        self.blank_matcher = re.compile(r"^\s*$")
        # strange thing has happened -- some archives have the column
        # off by exactly 1 character, resulting in some fubar'ing of
        # our parsing.  to solve our problem, we first recognize
        # rec_col_matcher, then parse fields using the ------
        # underlining, which appears to line up even in fubared
        # archives.
        self.rec_col_matcher = re.compile(r"(\s*Amount\s*)(Measure\s*)(Ingredient.*)")
        self.rec_col_underline_matcher = re.compile(r"(\s*-+)(\s*-+)(\s*-+.*)")
        # match a string enclosed in a possibly repeated non-word character
        # such as *Group* or ---group--- or =======GROUP======
        # grabbing groups()[1] will get you the enclosed string
        self.dash_matcher = re.compile(r"^[ -]*[-][- ]*$")
        self.ing_or_matcher = re.compile(r"\W*[Oo][Rr]\W*")
        self.ing_group_matcher = re.compile(r"\s*(\W)\\1*(.+?)(\\1+)")
        self.mods_matcher = re.compile(r"^\s*NOTES\.*")
        attr_matcher = fr"\s*({'|'.join(list(self.ATTR_DICT.keys()))})\s*:(.*)"
        self.attr_matcher = re.compile(attr_matcher)

    def handle_line (self, line):
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
        if self.reccol_headers:
            # we try to parse underlining after our standard ing headers.
            rcm = self.rec_col_underline_matcher.match(line)
            # if there is no underlining, use our headers themselves for fields
            if not rcm: rcm = self.reccol_headers
            debug('Found ing columns',0)
            self.get_ing_cols(rcm)
            self.in_ings = True
            self.reccol_headers=False

        if self.dash_matcher.match(line): return

        rcm=self.rec_col_matcher.match(line)
        if rcm:
            self.reccol_headers = rcm
            self.looking_for_title=False
            self.in_attrs=False
            self.last_attr = ""
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
            return
        if self.looking_for_title:
            debug('found my title! %s'%line.strip(),0)
            self.rec['title']=line.strip()
            self.looking_for_title = False
            self.in_attrs=True
            return
        if self.in_ings:
            debug('handling ingredient line %s'%line,0)
            self.handle_ingline (line)
            return
        if self.in_attrs:
            debug('handing attrline %s'%line,0)
            self.handle_attribute(line)
            return
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
                self.rec[self.last_attr]=', '.join([self.rec[self.last_attr],
                                                    self.join_multiple_attvals(line.strip())
                                                    ])
            else:
                # otherwise, we add this to instructions, like we do with all junk
                self.instr += line

    def join_multiple_attvals (self, txt):
        """We take replace more than one space with a comma."""
        return ', '.join(re.split('  +',txt))

    def handle_ingline (self,line):
        if self.ing_or_matcher.match(line):
            self.in_or = True
            return
        amt = line[slice(*self.amt_col)].strip()
        unit = line[slice(*self.unit_col)].strip()
        itm = line[self.itm_col[0]:].strip()
        gm=self.ing_group_matcher.match(itm)
        if gm:
            if self.ing: self.commit_ing()
            self.group = gm.groups()[1]
            # undo grouping if it has no letters...
            if re.match('^[^A-Za-z]*$',self.group): self.group=None
            return
        if amt or unit:
            if self.in_or: self.ing['optional']=True
            if self.ing: self.commit_ing()
            self.start_ing()
            if self.in_or:
                self.ing['optional']=True
                self.in_or = False
            self.add_amt(amt)
            self.add_unit(unit)
            self.add_item(itm)
            return
        elif self.ing and 'item' in self.ing:
            # otherwise, we assume we are a continuation and
            # add onto the previous item
            self.ing['item']=self.ing['item']+' '+itm.strip()
        else:
            debug('"%s" in the midst of ingredients looks like instructions!'%itm.strip(),2)
            self.instr += "\n"+itm.strip()

    def commit_ing (self):
        if 'item' not in self.ing:
            return
        key_base = self.ing['item'].split('--')[0]
        self.ing['ingkey']=self.km.get_key_fast(key_base)
        importer.Importer.commit_ing(self)
        self.ing = {}

    def commit_rec (self):
        ll=self.instr.split('\n')
        self.rec['instructions']=self.unwrap_lines(self.instr)
        self.rec['modifications']=self.unwrap_lines(self.mods)
        importer.Importer.commit_rec(self)

class Tester (importer.Tester):
    def __init__ (self):
        importer.Tester.__init__(self,regexp=MASTERCOOK_START_REGEXP)
        self.not_me = "<[?]?(xml|mx2|RcpE|RTxt)[^>]*>"

    def test (self, filename):
        if not hasattr(self,'matcher'):
            self.matcher=re.compile(self.regexp)
            self.not_matcher = re.compile(self.not_me)
        if isinstance(filename, str):
            self.ofi = open(filename,'r')
            CLOSE = True
        else:
            self.ofi = filename
            CLOSE = False
        l = self.ofi.readline()
        while l:
            if self.not_matcher.match(l):
                self.ofi.close()
                return False
            if self.matcher.match(l):
                self.ofi.close()
                return True
            l = self.ofi.readline()
        if CLOSE: self.ofi.close()
        else: self.ofi.seek(0)
