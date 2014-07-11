import sys
import urllib, zipfile, tempfile, os.path, re, string
from gettext import gettext as _
from parser_data import ABBREVS, ABBREVS_STRT, FOOD_GROUPS, NUTRITION_FIELDS, WEIGHT_FIELDS
from gourmet.gdebug import TimeAction
expander_regexp = None

from sqlalchemy.types import Integer, Float

from models import Nutrition, UsdaWeight

def compile_expander_regexp ():    
    regexp = "(?<!\w)("
    regexp += string.join(ABBREVS.keys(),"|")
    regexp += ")(?!\w)"
    return re.compile(regexp)

def expand_abbrevs ( line ):
    """Expand standard abbreviations."""
    global expander_regexp
    for k,v in ABBREVS_STRT.items():
        line = line.replace(k,v)
    if not expander_regexp:
        expander_regexp=compile_expander_regexp()
    ematch = expander_regexp.search(line)
    while ematch:
        matchstr=ematch.groups()[0]
        replace=ABBREVS[str(matchstr)]
        line = line[0:ematch.start()] + replace + line[ematch.end():]
        ematch = expander_regexp.search(line)
    return line

class DatabaseGrabber:
    USDA_ZIP_URL = "http://www.nal.usda.gov/fnic/foodcomp/Data/SR17/dnload/sr17abbr.zip"
    ABBREV_FILE_NAME = "ABBREV.txt"
    DESC_FILE_NAME = "FOOD_DES.txt"
    WEIGHT_FILE_NAME = "WEIGHT.txt"

    def __init__ (self,
                  session,
                  show_progress=None):
        self.show_progress=show_progress
        self.session = session
        
    def get_zip_file (self):
        if hasattr(self,'zipfile'):
            return self.zipfile
        else:
            ofi = urllib.urlopen(self.USDA_ZIP_URL)
            tofi = tempfile.TemporaryFile()
            tofi.write(ofi.read())
            tofi.seek(0)
            self.zipfile = zipfile.ZipFile(tofi,'r')
            return self.zipfile
        
    def get_file_from_url (self, filename):
        zf = self.get_zip_file()
        tofi2 = tempfile.TemporaryFile()
        tofi2.write(zf.read(filename))
        tofi2.seek(0)
        return tofi2

    def get_abbrev (self, filename=None):
        if filename:
            afi = open(filename,'r')
        else:
            afi = self.get_file_from_url(self.ABBREV_FILE_NAME)
        self.parse_abbrevfile(afi)
        afi.close()
        del self.foodgroups_by_ndbno

    def get_groups (self, filename=None):
        self.group_dict = {}
        if filename:
            afi = open(filename,'r')
        else:
            afi = self.get_file_from_url(self.DESC_FILE_NAME)
        self.foodgroups_by_ndbno = {}
        for l in afi.readlines():
            flds = l.split('^')
            ndbno = int(flds[0].strip('~'))
            grpno = int(flds[1].strip('~'))
            self.foodgroups_by_ndbno[ndbno] = grpno

    def get_weight (self, filename=None):
        if filename:
            wfi = open(filename,'r')
        else:
            wfi = self.get_file_from_url(self.WEIGHT_FILE_NAME)
        self.parse_weightfile(wfi)
        wfi.close()

    def grab_data (self, directory=None):
        self.get_groups((isinstance(directory,str)
                         and
                         os.path.join(directory,self.DESC_FILE_NAME)))
        self.get_abbrev((isinstance(directory,str)
                         and
                         os.path.join(directory,self.ABBREV_FILE_NAME)))
        self.get_weight((isinstance(directory,str)
                         and
                         os.path.join(directory,self.WEIGHT_FILE_NAME)))

    def parse_line (self, line, SqlaClass, split_on='^'):
        """Handed a line and field definitions, return an SQLAlchemy object of
        type SqlaClass for the line parsed.

        The line is a line with fields split on '^'
        """
        d = SqlaClass()
        fields = line.split("^")
        field_defs = [(i.name, i.type) for i in SqlaClass.__table__.columns]

        # If our SqlaClass adds an id field as first column (as UsdaWeight
        # does), our parsing routine would get confused by it, so we need to
        # remove it from field_defs first.
        name_of_first, _ = field_defs[0]
        if name_of_first != 'ndbno':
            field_defs.pop(0)

        for n,fl in enumerate(fields):
            try:
                sname,typ = field_defs[n]
            except IndexError:
                print n,fields[n],'has no definition in ',field_defs,len(field_defs)
                print 'Ignoring problem and forging ahead!'
                break

            fl = fl.strip('~')

            if isinstance(typ, Float):
                try:
                    setattr(d, sname, float(fl))
                except ValueError:
                    pass
            elif isinstance(typ, Integer):
                try:
                    setattr(d, sname, int(float(fl)))
                except ValueError:
                    pass
            else:
                setattr(d, sname, fl)

        return d

    def parse_abbrevfile (self, abbrevfile):
        if self.show_progress:
            self.show_progress(float(0.03),_('Parsing nutritional data...'))
        self.datafile = tempfile.TemporaryFile()
        ll=abbrevfile.readlines()
        tot=len(ll)
        n = 0
        for n,l in enumerate(ll):
            l = unicode(l.decode('latin_1'))
            tline=TimeAction('1 line iteration',2)
            t=TimeAction('split fields',2)
            d = self.parse_line(l, Nutrition)
            d.desc=expand_abbrevs(d.desc)
            d.foodgroup=FOOD_GROUPS[
                self.foodgroups_by_ndbno[d.ndbno]
                ]
            t.end()
            if self.show_progress and n % 50 == 0:
                self.show_progress(float(n)/tot,_('Reading nutritional data: imported %s of %s entries.')%(n,tot))
            t = TimeAction('append to db',3)
            self.session.add(d)
            t.end()                        
            tline.end()
        self.session.commit()

    def parse_weightfile (self, weightfile):
        if self.show_progress:
            self.show_progress(float(0.03),_('Parsing weight data...'))
        ll=weightfile.readlines()
        tot=len(ll)
        n=0
        for n,l in enumerate(ll):
            l = unicode(l.decode('latin_1'))
            if self.show_progress and n % 50 == 0:
                self.show_progress(
                    float(n)/tot,
                    _('Reading weight data for nutritional items: imported %s of %s entries')%(n,tot)
                    )
            d = self.parse_line(l, UsdaWeight)
            d.stdev = None
            self.session.add(d)
        self.session.commit()
            


if __name__ == '__main__':
    tot_prog = 0
    def show_prog (perc, msg):
        perc = perc * 100
        if perc - tot_prog: print "|" * int(perc - tot_prog)
    print 'getting our recipe database'
    import gourmet.recipeManager
    db = gourmet.recipeManager.RecipeManager(**gourmet.recipeManager.dbargs)
    print 'getting our grabber ready'
    grabber = DatabaseGrabber(db,show_prog)
    print 'grabbing recipes!'
    grabber.grab_data('/home/tom/Projects/grm/data/')
    #grabber.parse_weightfile(open('/home/tom/Projects/grm/data/WEIGHT.txt','r'))
    #grabber.get_weight('/home/tom/Projects/nutritional_data/WEIGHT.txt')    
    
