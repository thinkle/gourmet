import sys, shutil, os, os.path, time, re, urllib
import HTMLParser
from xml.sax.saxutils import quoteattr

# customize the following if you want to change your defaults
# (you can also tweak all these via commandline options)
PRODUCT = 'grecipe-manager'
MODULE = 'gourmet'
CREDITS = 'translator-credits'
BASE_URL='https://launchpad.ubuntu.com/rosetta/products/%(product)s/%(module)s/%(locale)s'
#       https://launchpad.ubuntu.com/products/grecipe-manager/unknown/+pots/gourmet/de_DE/+po
PO_URL='https://launchpad.ubuntu.com/products/%(product)s/unknown/+pots/%(module)s/%(locale)s/+po'
#PO_URL='https://launchpad.ubuntu.com/rosetta/products/%(product)s/%(module)s/%(locale)s/po'
LANG_LIST_URL="https://launchpad.ubuntu.com/rosetta/products/%(product)s/%(module)s"
MAX_TODO_THAT_WE_FETCH = 400

class TableParser (HTMLParser.HTMLParser):
    """A base scraper for grabbing HTML tables"""
    def __init__ (self):
        HTMLParser.HTMLParser.__init__(self)
        self.properties = []
        self.tables = []
        self.in_table = False
        self.collect_data = False
        self.data = ""

    def handle_data (self,data):
        if self.collect_data: self.data += data

    def handle_charref (self,data):
        if self.collect_data: self.data += "&#%s;"%data

    def handle_entityref (self,data):
        if self.collect_data: self.data += "&%s;"%data
    
    def handle_starttag (self,tag, attrs):
        if tag=='table':
            self.headers = []
            self.current_table = []
            self.in_table=True
        elif tag=='tr' and self.in_table:
            self.row = {}
            self.column = 0
        elif tag=='th' and self.in_table:
            self.collect_data=True
            self.data = ""
        elif tag=='td' and self.in_table:
            self.collect_data=True
            self.data = ""
        elif self.collect_data:
            self.collect_starttag(tag,attrs)

    def reset_data (self):
        self.data=""
        self.collect_data=False
    
    def collect_starttag (self,tag, attrs):
        self.data += "<%s"%tag
        for a,v in attrs:
            self.data += " %s=%s"%(a,quoteattr(v))
        self.data += ">"
        
    def collect_endtag (self,tag):
        self.data += '</%s>'%tag

    def handle_endtag (self,tag):
        if tag=='table':
            self.in_table=False
            self.tables.append(self.current_table)
            self.reset_data()
        elif tag=='tr':
            self.current_table.append(self.row)
        elif tag=='th':
            self.headers.append(self.data.strip())
            self.reset_data()
            self.column += 1
        elif tag=='td':
            if len(self.headers) > self.column:
                head=self.headers[self.column]
            else:
                head=self.column
            self.row[head]=self.data.strip()
            self.reset_data()
            self.column += 1
        elif self.collect_data:
            self.collect_endtag(tag)

class LangTableParser (TableParser):
    """Scrape an Ubuntu Rosetta page for the table of languages translated."""

    def close (self):
        """When we finish eating our data, we set up self.lang_table with our language dictionary.
        This "table" is keyed by language code (es_ES/cs/etc.) and has as its value a dictionary
        with the field names provided on the Ubuntu webpage and some special fields as well:
        date: date parsed into seconds since 1972
        lang: language code (redundant)
        """
        TableParser.close(self)
        if self.tables:
            self.lang_base_table = self.tables[0]
        for r in self.lang_base_table:
            r['date']=0
            le = r['Last Edited']
            if le != '&mdash;':
                try:
                    r['date']=time.mktime(time.strptime(le,'%Y-%m-%d %Z'))
                except ValueError:
		    try:
                        r['date']=time.mktime(time.strptime(le,'%Y-%m-%d'))
                    except ValueError:
                        print 'Unable to parse time: ',le
                        raise
        self.lang_table = {}
        for row in self.lang_base_table:
            self.lang_table[row['lang']]=row

    def collect_starttag (self,tag,attrs):
        """We only care about the language attribute from the URL of our Language <a href="">"""
        if tag=='a':
            hrefs=filter(lambda a: a[0]=='href',attrs)
            if hrefs:
                href=hrefs[0][1]
                # we rely on URLs like this: "+translate?languages=bg"
                #lang=href.split('=')[-1]
                #
                # language URLs have changed (6/4/05)
                # we now rely on URLs looking like this
                # .../bg/+translate
                lang = href.split('/')[-2]
                self.row['lang']=lang
    def collect_endtag (self,tag):
        pass
    
            

def get_langlist ():
    """Return a dictionary with information on latest translations.
        
    {LOCALE_CODE : {'lang':language code,'Last Edited': date last edited as string,...}

    See LangTableParser.close for more details.
    """
    ifi=urllib.urlopen(LANG_LIST_URL%{'product':PRODUCT,'module':MODULE})
    ltp = LangTableParser()
    ltp.feed(ifi.read())
    ltp.close()
    return ltp.lang_table

def get_base_page (locale):
    """Handed a locale, return the base page for it as a string."""
    ifi = urllib.urlopen(BASE_URL%{'locale':locale,
                                   'product':PRODUCT,
                                   'module':MODULE})
    wholepage=ifi.read()
    return wholepage

def get_contriblist (wholepage):
    """grab our contributor list handed our webpage as a string

    This is a very primitive scraper."""
    m=re.search('<h2>Contributors for this translation:</h2>(.|\n)*<div>((.|\n)*?)</div>',wholepage)
    if not m: return None
    contriblist=m.groups()[1]
    # we now strip out tags and assume we'll end up with a one-contributor-per-line setup, which
    # we return to our user, filtering out all the empty lines (e.g. lines that used to have only
    # a tag on them
    return filter(lambda x: x, [s.strip() for s in re.sub('<[^>]*>','',contriblist).split('\n')])

def get_po (locale):
    """Return a file object with our PO file"""
    print 'PO_URL:',PO_URL
    print 'locale:',locale
    print 'product:',PRODUCT
    print 'module:',MODULE
    print 'Attempting to fetch %s'%PO_URL%{'locale':locale,
                                  'product':PRODUCT,
                                  'module':MODULE}
    return urllib.urlopen(PO_URL%{'locale':locale,
                                  'product':PRODUCT,
                                  'module':MODULE})

def write_contribs (out, contribs, current_contribs):
    """Write list of contributors in gettexty format."""
    current_contribs = filter(lambda x: x.strip(), current_contribs) #get rid of blank lines
    for c in current_contribs:
        # add to our list if we don't have any matches for our contrib
        # (we assume useful changes would be made by appending to our
        # name, e.g. Thomas M. Hinkle -> Thomas M. Hinkle <Thomas_Hinkle@alumni.brown.edu>
        if not 0 in [cont.find(c) for cont in contribs]:
            contribs.append(c)
    out.write('msgstr ')
    if not contribs: out.write('""')
    else:
        print 'Adding contributors %s'%contribs
        for c in contribs:
            print 'Adding contributor ',c
            out.write('"%s"\n'%c.replace('"','')) # remove any quotation marks
    out.write("\n\n")
    
def write_po_with_contribs (pofi, ofi, contribs=None):
    """Write a PO file based on file-object pofi into file named ofi

    Possibly modify the PO file to give credit to a list of contributors
    contribs
    """
    ofi=open(ofi,'w')
    if contribs:
        flag = False
        current_contribs = []
        for l in pofi.readlines():
            if flag and (l.find("#")>=0 or l.find("msgid")>=0):
                write_contribs(ofi,contribs,current_contribs)
                flag=False
                ofi.write(l) # and then add our line
            elif flag and l.strip():
                current_contribs.append(l[l.find('"')+1:l.rfind('"')])
            else:
                ofi.write(l) #otherwise, just echo our line out
            if l.find('msgid "%s"')%CREDITS==0:
                flag=True
    else:
        # otherwise just spit this into a file
        ofi.write(pofi.read())
    ofi.close()

def get_translations (locales, do_credits=True):
    """Get translations for locales in list locales

    do_credits is a flag telling us whether to bother trying to rewrite
    translator-credits with proper credits
    """
    retval = []
    for l in locales:
        if l.strip().find('#')==0:
            # ignore comments
            continue
        locale = l.strip()
        if do_credits:
            try:
                credits=get_contriblist(get_base_page(locale))
            except IOError:
                credits=None
                print 'Unable to fetch contriblist for %s'%locale
        else: credits=None
        outfile = "%s.po"%locale
        if os.path.exists(outfile):
            # make a backup file
            shutil.move(outfile,outfile+'.backup_%s'%time.strftime('%d-%m'))
        try:
            print 'Writing PO for %s'%locale
            write_po_with_contribs (get_po(locale),
                                    outfile,
                                    credits)
            retval.append(l)
        except IOError:
            print 'unable to fetch PO file for %s'%locale
    return retval

def pad (string,n,cut=True):
    if len(string) < n:
        return string + " " * (n - len(string))
    elif cut and len(string) > n:
        return string[0:n]
    else:
        return string

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser(
        version='0.1',
        description='A simple script to fetch PO files from Rosetta.',
        usage="""If called with no options or arguments, we will attempt to fetch all PO files for which
        there are translations.

        If called with arguments, we will assume each argument is a
        locale code (es_ES, en, etc.) for which PO files should be
        grabbed.
        """,
        option_list=[
        optparse.make_option('-s','--show-translation-info',dest='action',action='store_const',
                             const='show_info',help='Show information about latest rosetta translations.'),
        optparse.make_option('--product',action='store',
                             dest='PRODUCT',
                             help='Project name (as given to rosetta)',
                             default=PRODUCT),
        optparse.make_option('--module',
                             action='store',
                             dest='MODULE',
                             help='Module name (name for individual POT file within Rosetta)',
                             default=MODULE),
        optparse.make_option('-g','--grab',dest='action',action='store_const',const='grab',
                             help='get new PO files from rosetta',default='grab'),
        optparse.make_option('--grab-from-file',
                             dest='localefile',action='store',
                             default=None,
                             help='Pointer to file with list of translations to be used (if none are given on the commandline)'),
        optparse.make_option('-c','--add-contributors-translator-credits',dest='do_credits',action='store_const',
                             const=True,
                             help='Automatically add contributors to field for translator-credits'),
        optparse.make_option('--custom-credits-field',dest='CREDITS',action='store',
                             default=CREDITS),
        ]
        )
    options,args=parser.parse_args()
    PRODUCT=options.PRODUCT
    MODULE=options.MODULE
    CREDITS=options.CREDITS
    if options.action=='grab':
        record_time=False
        if args:
            locales = args
        elif options.localefile:
            ifi = open(options.localefile,'r')
            locales = filter(lambda ln: ln.strip().find('#')==0,ifi.readlines())
        else:
            ll=get_langlist().items()
            print 'Rosetta knows about %s possible translations'%len(ll)
            ll=filter(lambda x: int(x[1].get('Todo','1000'))<MAX_TODO_THAT_WE_FETCH,ll) #only include translations that have been completed
            print 'There are at least some translations in %s languages'%len(ll)
            if os.path.exists('.rosetta_last_date_grabbed'):
                ifi=open('.rosetta_last_date_grabbed','r')
                date=float(ifi.read().strip()) #a simple integer stores our time...
                ifi.close()
            else: date=0
            ll=filter(lambda x: x[1]['date']>date,ll)
            locales=[x[0] for x in ll]
            print 'There are %s new translations since last update.'%len(ll)
            record_time=True
        translated_locales = get_translations(locales,do_credits=options.do_credits)
        print 'Successfully grabbed translations for: ',
        for l in translated_locales: print l,
        print ''
        if record_time:
            # only record time for translated locales
            dates = [x[1]['date'] for x in filter(lambda x: x[0] in translated_locales,
                                                  ll)]
            dates.sort()
            if dates:
                print 'Recording timestamp of this grab.'
                ofi=open('.rosetta_last_date_grabbed','w')
                ofi.write("%s"%dates[-1]) # take our most recent file as our date
                ofi.close()
    elif options.action=='show_info':
        print pad('Language',12),pad('Last-Edited',15),pad('Done',6),pad('Todo',6)
        ll = get_langlist().items()
        ll.sort()
        for lang,d in ll:
            print pad(lang,12),pad(d.get('Last Edited',''),15),pad(d.get('Done',''),6),pad(d.get('Todo',''),6)
