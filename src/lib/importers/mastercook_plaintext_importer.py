import importer

class mastercook_importer (importer.importer):
    ATTR_DICT = {'Recipe By':'source',
                 'Serving Size':'servings',
                 'Preparation Time':'preptime',
                 'Categories':'category',
                 }
    def __init__ (self, rd, file, prog=None, threaded=False):
        importer.importer.__init__(rd,threaded=threaded)
        self.compile_regexps()
        self.in_ings = False
        self.in_instructions = False
        self.looking_for_title = False
        self.in_attrs=False
        
    def compile_regexps (self):
        self.rec_start_matcher = re.compile("^\s*\*\s*Exported\s*from\s*MasterCook\s*\*\s*$")
        self.blank_matcher = re.compile("^\s*$")
        self.rec_col_matcher = re.compile("(\s*Amount\s*)(Measure\s*)(Ingredient.*)")
        # match a string enclosed in a possibly repeated non-word character
        # such as *Group* or ---group--- or =======GROUP======
        # grabbing groups()[1] will get you the enclosed string
        self.ing_group_matcher = re.compile("\s*(\W)\\1*(.+?)(\\1+)")
        attr_matcher = "\s*(" + string.join(self.ATTR_DICT.keys(),"|") + ")\s*:(.*)"
        self.attr_matcher = re.compile(attr_matcher)
        
    def handle_line (self, line):
        if self.rec_start_matcher.match(line):
            self.looking_for_title = True
            if self.rec: self.commit_rec()
            self.start_rec()
        rcm=self.rec_col_matcher.match(line)
        if rcm:
            self.looking_for_title=False
            self.in_attrs=False
            self.get_ing_cols(rcm)
            self.in_ings = True
            return
        if self.blank_matcher.match(line):
            # blank line ends ingredients
            if self.in_ings: 
                self.in_ings = False
                self.in_instructions = True
                if self.ing: self.commit_ing()
            if self.in_instructions:
                self.instr+="\n"
        elif self.looking_for_title:
            self.rec['title']=line.strip()
            self.looking_for_title = False
            self.in_attrs=True
            return
        elif in_ings:
            self.handle_ingline (line)
            return
        elif in_attrs:
            self.handle_attribute(line)
        else:
            self.in_instructions = True
            if self.instr:
                if len(line.strip()) < 50:
                    self.instr += "%s\n"%line.strip()
                elif not self.blank_matcher(self.instr[-1]):
                    self.instr += " %s"%line.strip()
                else:
                    self.instr += line.strip()
            else:
                self.instr = line.strip()
    
    def get_ing_cols (rcm):
        amt,unit,itm=rcm.groups()
        lamt,lunit,litm = len(amt),len(unit),len(itm)
        self.amt_col = 0,lamt
        self.unit_col = lamt,lamt+lunit
        self.itm_col = lamt+lunit,None

    def handle_attribute (line):
        m=self.attr_matcher.match(line)
        if m:
            attr,val = m.groups()
            2ndColMatch = self.attr_matcher.search(val)
            if 2ndColMatch:
                s=2ndColMatch.start()
                self.handle_attribute(val[s:])
                val = val[:s]
            val = val.strip()
            attr = attr.strip()
            self.rec[self.ATTR_DICT[attr]]=val
        else:
            debug('Non-Attribute hanging out with the attributes: %s'%line)
            self.instr += line

    def handle_ingline (line):        
        amt = line.__getslice__(*self.amt_col).strip()
        unit = line.__getslice__(*self.unit_col).strip()
        itm = line[self.itm_col[0]:].strip()
        if amt or unit:
            if self.ing: self.commit_ing()
            self.start_ing()
            self.add_amt(amt)
            self.add_unit(unit)
            self.add_item(itm)
        else:
            # otherwise, we assume we are a continuation and
            # add onto the previous item
            gm=self.ing_group_matcher(itm)
            if gm:
                self.commit_ing()
                self.group = gm.groups()[1]
            self.ing['item']=self.ing['item']+' '+itm.strip()
        self.commit_ing()
        

    def commit_ing (self):
        key_base = self.ing['item'].split('--')[0]
        self.ing['ingkey']=self.km.get_key_fast(key_base)
        
