import urllib, zipfile, tempfile, os.path, re, string
from gettext import gettext as _
from parser_data import *
from gourmet.gdebug import *
expander_regexp = None

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

    def __init__ (self,
                  db,
                  show_progress=None):
        self.show_progress=show_progress
        self.db = db
        
    def get_zip_file (self):
        ofi = urllib.urlopen(self.USDA_ZIP_URL)
        tofi = tempfile.TemporaryFile()
        tofi.write(ofi.read())
        tofi.seek(0)
        return zipfile.ZipFile(tofi,'r')

    def get_abbrev_from_url (self):
        zf = self.get_zip_file()
        tofi2 = tempfile.TemporaryFile()
        tofi2.write(zf.read(self.ABBREV_FILE_NAME))
        tofi2.seek(0)
        return tofi2

    def get_abbrev (self, filename=None):
        if filename:
            afi = open(filename,'r')
        else:
            afi = self.get_abbrev_from_url()
        self.parse_abbrevfile(afi)
        afi.close()

    def parse_abbrevfile (self, abbrevfile):
        if self.show_progress:
            self.show_progress(float(0.03),'Parsing nutritional data.')
        self.datafile = tempfile.TemporaryFile()
        ll=abbrevfile.readlines()
        tot=len(ll)
        n = 0
        for n,l in enumerate(ll):
            tline=TimeAction('1 line iteration',0)            
            t=TimeAction('split fields',0)
            fields = l.split("^")
            # first field is our description, where the abbrevs are :)
            fields[1]=expand_abbrevs(fields[1])
            t.end()
            d = {}
            t=TimeAction('enumerate fields',0)
            for nn,fl in enumerate(fields):
                lname,sname,typ = NUTRITION_FIELDS[nn]
                if fl and fl[0]=="~" and fl[-1]=="~":
                    d[sname]=fl[1:-1]
                if typ=='float':
                    try:
                        d[sname]=float(d.get(sname,fl))
                    except:
                        d[sname]=None
                if typ=='int':
                    try:
                        d[sname]=int(d.get(sname,fl))
                    except:
                        d[sname]=fl
                        raise
            # Figure out the food group from the ndbno
            for i in FOOD_GROUPS:
                if 1000+i > d['ndbno'] >= i:
                    d['foodgroup']=FOOD_GROUPS[i]
                    break
            t.end()
            if self.show_progress and n % 20 == 0:
                self.show_progress(float(n)/tot,_('Reading nutritional data: imported %s of %s entries.')%(n,tot))
            t = TimeAction('append to db',0)
            self.db.nview.append(d)
            t.end()                                
            tline.end()
        


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
    grabber.get_abbrev('/home/tom/Projects/nutritional_data/ABBREV.txt')
    
