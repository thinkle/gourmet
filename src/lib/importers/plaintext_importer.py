import importer, re, string
from gourmet import check_encodings
from gourmet.gdebug import *
from gettext import gettext as _

class TextImporter (importer.importer):
    ATTR_DICT = {'Recipe By':'source',
                 'Serving Size':'servings',
                 'Preparation Time':'preptime',
                 'Categories':'category',
                 }
    def __init__ (self, filename, rd, progress=None, threaded=False):
        print 'rd=',rd,' file=',file
        self.fn = filename
        self.rec = {}
        self.ing = {}
        self.progress = progress
        self.compile_regexps()
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

    def handle_line (self):
        raise NotImplementedError

    def compile_regexps (self):
        self.blank_matcher = re.compile("^\s*$")
        # out unwrap regexp looks for a line with no meaningful characters, or a line that starts in
        # ALLCAPS or a line that is only space. (we use this with .split() to break text up into
        # paragraph breaks.
        self.unwrap_matcher = re.compile('\n\W*\n')
        self.find_header_breaks_matcher = re.compile('\s+(?=[A-Z][A-Z][A-Z]+:.*)')
        
    def unwrap_lines (self, blob):
        outblob = ""
        newline = True
        for l in blob.split('\n'):
            if re.match('^\W*$',l):
                # ignore repeated nonword characters (hyphens, stars, etc.)
                outblob += "\n"
                continue
            # if we have a non-word character at the start of the line,
            # we assume we need to keep the newline.
            if len(l)>=3 and re.match('(\W|[0-9])',l[3]):
                outblob += "\n"
                outblob += l
                newline = False
                continue
            # if we are continuing an old line, we add a space
            # (because we're generally stripping all spaces when
            # we write)
            if not newline: outblob += " "            
            hmatch = self.find_header_breaks_matcher.search(l)
            if hmatch:
                # if there's a header in the middle, we go ahead
                # and start a new line
                outblob += l[:hmatch.start()]
                outblob += "\n"
                outblob += l[hmatch.start():]
                continue
            #else...
            outblob += l.strip()
            if len(l) < 60: #60 is our hard-coded end-o-paragraph length
                outblob += "\n"
                newline = True
            else:
                newline = False
        return outblob
        
class Tester (importer.Tester):
    def __init__ (self):
        importer.Tester.__init__(self,regexp=MASTERCOOK_START_REGEXP)
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
