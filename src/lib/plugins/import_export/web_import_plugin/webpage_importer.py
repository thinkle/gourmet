# This is a basic
import BeautifulSoup
from gourmet.importers.generic_recipe_parser import RecipeParser
from gourmet.importers.interactive_importer import InteractiveImporter
import gourmet.importers.importer
import re, urllib
#import gourmet.plugin_loader

class WebParser (InteractiveImporter):

    BREAK_AROUND = ['p','title','h1','h2','h3','h4','h5','h6',
                    'table','p','blockquote','title','div']
    IS_BREAK = ['br']
    NESTED = {'tr':['table'],
              'li':['ol','ul'],
              'dd':['dl'],
              }
    TAB_BEFORE = ['td','dt']
    IGNORE = ['script','meta','select','link','img']
    TAB = '  '
    JOINABLE = ['instructions','notes','recipe','ignore','ingredients','include',None]
    INVISIBLE_TYPES = [
        BeautifulSoup.CData,
        BeautifulSoup.Comment,
        BeautifulSoup.Declaration,
        BeautifulSoup.ProcessingInstruction]

    do_postparse = True
    imageexcluders = None # This could be a list of compiled regexps which would
                         # be used to search image URL strings for
                         # potential ads, etc.
    def __init__ (self, url, data, content_type):
        self.ignore_unparsed = False
        self.url = url
        #self.name = 'Web Parser'
        self.soup = BeautifulSoup.BeautifulSoup(data,
                                                convertEntities=BeautifulSoup.BeautifulStoneSoup.XHTML_ENTITIES,
                                                )
        InteractiveImporter.__init__(self)        
        #self.generic_parser = RecipeParser()
        self.preparse()
        self.get_images()
        self.text_parser = RecipeParser()

    def commit_rec (self):
        if not self.rec.get('link',''): self.rec['link'] = self.url
        gourmet.importers.importer.Importer.commit_rec(self)

    def preparse (self):
        self.preparsed_elements = []

    def identify_match (self, tag):
        for t,label in self.preparsed_elements:
            if tag==t:
                return label

    def get_images (self):
        self.images = []
        for i in self.soup('img'):
            try:
                src = i['src']
            except KeyError:
                continue
            img_url = urllib.basejoin(self.url,src)
            if self.imageexcluders:
                exclude = False
                for exc in  self.imageexcluders:
                    if exc.search(img_url):
                        exclude = True
                        break
                if exclude: continue
            self.images.append(img_url)
        
    def parse (self, tag=None):
        if not tag: tag = self.soup
        self.parsed = []
        self.buffer = ''
        self.last_label = None
        self.crawl(tag)
        if self.buffer:
            self.add_buffer_to_parsed()
        return self.parsed
    
    def crawl (self, tag, parent_label=None):
        formatting = self.format_tag_whitespace(tag)
        if formatting == -1:
            return # special case allows formatting method to
                   # auto-skip scripts and what-not
        else:
            start_ws,end_ws = formatting
            self.buffer += start_ws
        label = self.identify_match(tag)        
        if not label and parent_label:
            # inherit...
            label = parent_label
        elif self.ignore_unparsed and not label:
            label = 'ignore'
        #elif not label:
        #    print 'DONT IGNORE'
        #print 'ID TAG',tag,'with',label            
        if hasattr(tag,'contents') and tag.contents:
            for child in tag.contents:
                self.crawl(child,label)
        else:
            if label != self.last_label or self.last_label not in self.JOINABLE:
                if self.buffer:
                    self.add_buffer_to_parsed()
                self.last_label = label
            #print 'ADD TO BUFFER:',tag.string
            if hasattr(tag,'string'):
                self.buffer += self.reduce_whitespace(tag.string or '')
            #else:
            #    print 'Ignoring tag',tag
        if end_ws: self.buffer += end_ws
        return label

    def reduce_whitespace (self, s):
        if not hasattr(self,'__whitespace_regexp'):
            self.__whitespace_regexp = re.compile('\s+')
        return self.__whitespace_regexp.sub(' ',s)

    def cut_extra_whitespace (self, s):
        if s.count('\n')>2:
                s = s.replace(
                    '\n','',
                    s.count('\n')-2)
        return s
    
    def add_buffer_to_parsed (self):
        if not self.buffer.strip(): return
        tws = 0 #tws = # of trailing whitespace characters
        while tws+1 < len(self.buffer) and self.buffer[-(tws+1)].isspace():
            tws += 1
        if not tws:
            to_add = self.buffer
            self.buffer = ''
        else:
            to_add = self.buffer[:-tws]
            self.buffer = self.buffer[-tws:]
            self.buffer = self.cut_extra_whitespace(self.buffer)
        lws = 0
        while lws+1 < len(to_add) and to_add[lws].isspace():
            lws += 1
        if lws:
            # In this case, we're going to add the white space separately with no label...
            pre_add = to_add[:lws]
            pre_add = self.cut_extra_whitespace(pre_add)
            to_add = to_add[lws:]
            self.parsed.append((pre_add,None))
        # Do extra substitution of MS Characters -- shouldn't be necessary...
        for char,tup in BeautifulSoup.UnicodeDammit.MS_CHARS.items():
            char = char.decode('iso-8859-1').encode('utf-8')
            if to_add.find(char) >= 0:
                to_add = to_add.replace(char,unichr(long(tup[1],16)))
        self.parsed.append((to_add,self.last_label))

    def format_tag_whitespace (self, tag):
        '''Return any whitespace required by tag, or -1 if tag should
        not be considered for text
        '''
        for klass in self.INVISIBLE_TYPES:
            if isinstance(tag,klass):
                return -1
        if not hasattr(tag,'name'):
            return '',''
        elif tag.name in self.IGNORE:
            return -1
        if tag.name in self.IS_BREAK:
            return '\n',''
        elif tag.name in self.NESTED:
            parent_types = self.NESTED[tag.name]; parents = 0
            for typ in parent_types:
                parents += len(tag.fetchParents(typ))
            return '\n'+self.TAB*parents,''
        elif tag.name in self.TAB_BEFORE:
            return self.TAB,''
        elif tag.name in self.BREAK_AROUND:
            return '\n','\n'
        else:
            return '',''

    def postparse (self, parsed):
        '''Do purely text-based parsing of content.
        '''
        new_parse = []
        for p,attr in parsed:
            if attr == None or attr == 'recipe':
                new_parse.extend(
                    self.text_parser.parse(p)
                    )
            else:
                new_parse.append((p,attr))
        return new_parse

    def parse_webpage (self):
        self.preparse()
        tags = [pp[1] for pp in self.preparsed_elements]
        if 'include' in tags:
            self.ignore_unparsed = True
        parsed = self.parse()
        if self.do_postparse:
            return self.postparse(parsed)
        else:
            return parsed

    def do_run (self):
        parsed = self.parse_webpage()
        self.set_parsed(parsed)
        return InteractiveImporter.do_run(self)

class MenuAndAdStrippingWebParser (WebParser):

    def preparse (self):
        self.preparsed_elements = []
        tit = self.soup('title')
        if tit:
            self.preparsed_elements.append((tit,'title'))
        self.cut_sponsored_links()
        self.cut_menus()

    def cut_menus (self):
        menu_regexp = re.compile('.*(menu|nav|crumb).*',re.IGNORECASE)
        els = self.soup(id=menu_regexp)
        els.extend(self.soup(attrs={'class':menu_regexp}))
        for menu in els:
            self.preparsed_elements.append((menu,'ignore'))
        menu_text_regexp = re.compile(
            '.*sitemap.*|^\s-*about\s-*',re.IGNORECASE
            )
        for menu in self.soup(text=menu_text_regexp):
            self.preparsed_elements.append((menu,'ignore'))

    def cut_sponsored_links (self):
        ad_re = re.compile('ad.*|.*advert.*',re.IGNORECASE)
        spons = self.soup(id=ad_re)
        spons.extend(self.soup(attrs={'class':ad_re}))
        for spon in spons:
            self.preparsed_elements.append((spon,'ignore'))
        
class WebParserTester (WebParser):

    def preparse (self):
        self.preparsed_elements = []
        head = self.soup('h1')
        if head:
            self.preparsed_elements.append((head[0],'title'))
        ings = self.soup('li')
        if ings:
            for i in ings: self.preparsed_elements.append((i,'ingredient'))
        author = self.soup('i')
        self.preparsed_elements.append((author[0],'source'))

class AboutDotComWebParser (MenuAndAdStrippingWebParser):

    def preparse (self):
        includes = [('rInt','instructions'),
                    ('rIng','ingredients'),
                    ('rPrp','instructions')]
        self.preparsed_elements = []
        for i,t in includes:
            for el in self.soup(id=i):
                self.preparsed_elements.append((el,t))
        if self.preparsed_elements:
            self.ignore_unparsed = True
            self.preparsed_elements.append((self.soup('title')[0],'title'))
            # Now get rid of the annoying "More... recipes..."
            try:
                boldyLinks = self.soup(id='rPrp')[0]('b')
                boldyLinks.extend(self.soup(id='rPrp')[0]('a'))
            except IndexError:
                pass
            else:
                regexp = re.compile('More.*|.*Recipes.*')
                for bold in boldyLinks:
                    if bold(text=regexp):
                        self.preparsed_elements.append((bold,'ignore'))
        else:
            MenuAndAdStrippingWebParser.preparse(self)
    
    def cut_sponsored_links (self):
        for sl in self.soup(text=re.compile('.*(Sponsored Links|Advertisement|Cooking Ads).*')):
            addiv = sl.findParent('div')
            self.preparsed_elements.append((addiv,'ignore'))
        MenuAndAdStrippingWebParser.cut_sponsored_links(self)
        
    def cut_menus (self):
        for mi in self.soup(text=re.compile('.*(Most Popular|Must Reads|By Category|iGoogle|More from About.com).*')):
            mendiv = mi.findParent('div')
            self.preparsed_elements.append((mendiv,'ignore'))        
        for mi in self.soup(text='Email'):
            mendiv = mi.findParent('div')
            self.preparsed_elements.append((mendiv,'ignore'))
        for div in self.soup('div',attrs={'class':'hlist'}):
            self.preparsed_elements.append((div,'ignore'))
        MenuAndAdStrippingWebParser.cut_menus(self)

def test_parser ():
    txt = '''<html><h1>Recipe</h1><p>This is my recipe<p><i>by Joe Shmoe</i></p><ul><li>1 cup sugar</li><li>2 cups flour</li><li>1 cup water</li>'''
    parser = WebParserTester('http://www.foo.bar',txt,None)
    parsed = parser.parse_webpage()
    for p,lab in parsed:
        print 'LABEL:',lab
        print 'TEXT:',p
    return parser

def test_webpage ():
    ifi = file('/tmp/test_recipe.htm','r')
    test = ifi.read(); ifi.close()
    parser = AboutDotComWebParser('http://www.foo.bar',test,None)
    parsed = parser.parse_webpage()
    for p,lab in parsed:
        if lab=='ignore': continue
        print 'LABEL:',lab
        print 'TEXT:',p
    return parser

if __name__ == '__main__':
    parser = test_parser()
    p = test_webpage()
    p.do_run()
