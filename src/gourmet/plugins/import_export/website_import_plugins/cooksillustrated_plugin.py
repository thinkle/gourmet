import keyring
from bs4 import BeautifulSoup
from selenium import webdriver

import gourmet.threadManager
from gourmet.gtk_extras import dialog_extras as de
from gourmet.i18n import _
from gourmet.plugin import ImportManagerPlugin, PluginPlugin
from gourmet.prefs import Prefs

from .state import WebsiteTestState

global driver
if 'driver' not in globals():
    driver = None

class LogInWebReader (gourmet.threadManager.SuspendableThread):

    def __init__ (self, url):
        self.url = url
        self.prefs = Prefs.instance()
        self.logged_in = True
        gourmet.threadManager.SuspendableThread.__init__(
            self,
            name=_('Downloading %s'%url)
            )

    def do_run (self):
        self.read()

    def get_username_and_pw (self):
        print('Let us get a password...')
        username = self.prefs.get('cooksillustrated-username','')
        print('Username=',username)
        if username:
            pw = keyring.get_password(
                'http://www.cooksillustrated.com',
                username
                )
        else:
            pw = ''
        print('Initial password: ',pw)
        print('Launch dialog...')
        #
        username, pw = de.getUsernameAndPassword(
            username=username,
            pw=pw
            )
        # broken :( - temporary workaround?
        #username,pw = 'USERNAME','PASSWORD'
        print('Done with dialog')
        self.prefs['cooksillustrated-username'] = username
        keyring.set_password(
            'http://www.cooksillustrated.com',username,pw
            )
        return username, pw

    def read (self):
        self.emit('progress',0,_('Logging into %s')%'www.cooksillustrated.com')
        global driver
        if driver:
            # Don't log in twice :)
            self.d = driver
        else:
            #self.d = webdriver.Chrome()
            self.d = webdriver.Firefox()
            print('Logging in...')
            driver = self.d
            self.d.get('https://www.cooksillustrated.com/sign_in/')
            username,pw = self.get_username_and_pw()
            #un=self.d.find_element_by_xpath('//*[@name="user[email]"]')
            un=self.d.find_element_by_xpath('//*[@id="email"]')
            print('Got email element',un)
            un.send_keys(username)
            #pw_el = self.d.find_element_by_xpath('//*[@name="user[password]"]')
            pw_el = self.d.find_element_by_xpath('//*[@id="password"]')
            print('Got password element',pw_el)
            pw_el.send_keys(pw+'\n')
        # Now get URL
        # First log in...
        self.emit('progress',0.5,_('Logging into %s')%'www.cooksillustrated.com')
        self.emit('progress',0.6,_('Retrieving %s')%self.url)
        self.d.get(self.url)
        self.emit('progress',1,_('Retrieving %s')%self.url)
        self.content_type = 'text/html'
        self.data = self.d.page_source

class WebImporterPlugin (ImportManagerPlugin):

    url_needs_login_patterns = {
        'cooksillustrated.com' : LogInWebReader,
        'cookscountry.com' : LogInWebReader,
        'americastestkitchen.com' : LogInWebReader,
    }

class CooksIllustratedPlugin (PluginPlugin):
    target_pluggable = 'webimport_plugin'

    def do_activate (self, pluggable):
        pass

    def test_url (self, url, data):
        if 'cooksillustrated.com' in url:
            return WebsiteTestState.SUCCESS
        if 'cookscountry.com' in url:
            return WebsiteTestState.SUCCESS
        if 'americastestkitchen.com' in url:
            return WebsiteTestState.SUCCESS
        if 'cooksillustrated.com' in data:
            return WebsiteTestState.SUCCESS_UNKNOWN
        if 'cookscountry.com' in data:
            return WebsiteTestState.SUCCESS_UNKNOWN
        if 'americastestkitchen.com' in data:
            return WebsiteTestState.SUCCESS_UNKNOWN

        return WebsiteTestState.FAILED

    def get_importer (self, webpage_importer):

        class CooksIllustratedParser (webpage_importer.MenuAndAdStrippingWebParser):
        #class CooksIllustratedParser (MenuAndAdStrippingWebParser):

            do_postparse = False

            def maybe_add (self, el, tag, ignoreSlug=False):
                if el:
                    if isinstance(el, (list,BeautifulSoup.ResultSet)):
                        for e in el:
                            self.maybe_add(e,tag,ignoreSlug)
                    else:
                        if not str(el).strip():
                                return # Don't add empty strings or we screw things up royally
                        self.preparsed_elements.append((el,tag))
                        if ignoreSlug:
                            self.maybe_add(el.findAll('h4',{'class':'section-slug'}),'ignore')


            def preparse (self):
                self.preparsed_elements = []
                self.maybe_add(self.soup.find('section',{'class':'why'}),'modifications')
                self.maybe_add(self.soup.find('h2',{'class':'document-header__title'}),'title')
                self.maybe_add(self.soup.find('h2',{'itemprop':'name'}),'title')
                self.maybe_add(self.soup.find('h1'),'title')
                self.maybe_add(self.soup.findAll('div',{'class':'ingredient'}), 'ingredients')
                self.maybe_add(self.soup.findAll('section',{'class':'ingredients'}),'ingredients',ignoreSlug=True)
                for ingSection in self.soup.findAll('section',{'class':'ingredients'}):
                    self.maybe_add(ingSection.findAll('h5'),'inggroup')
                contents = self.soup.findAll('div',{'class':'content'})
                for content in contents:
                    self.maybe_add(content.findAll('div',{'class':'long'}),'modifications')
                self.maybe_add(self.soup.findAll('li',{'itemprop':'ingredients'}),'ingredients')
                self.maybe_add(self.soup.findAll('div',{'class':'recipe__ingredient'}),'ingredients')
                self.maybe_add(self.soup.findAll('li',{'itemprop':'recipeInstructions'}),'instructions')
                self.maybe_add(self.soup.findAll('div',{'class':'recipe__instructions'}),'instructions')
                self.maybe_add(self.soup.findAll('section',{'class':'instructions'}),'instructions',ignoreSlug=True)
                self.maybe_add(self.soup.findAll('section',{'class':'recipe-instructions'}),'instructions',ignoreSlug=True)
                self.maybe_add(self.soup.findAll('section',{'class':'asides'}),'modifications')
                self.maybe_add(self.soup.findAll('div',{'class':'recipe-instructions'}), 'instructions',ignoreSlug=True)
                self.maybe_add(self.soup.findAll('div',{'class':'asides'}), 'modifications')
                self.maybe_add(self.soup.findAll('div',{'class':'publish-date'}), 'modifications')
                self.maybe_add(self.soup.find('span',{'class':'recipe-instructions__yield'}), 'yields')
                self.maybe_add(self.soup.find('nav'),'ignore')
                self.maybe_add(self.soup.find('header'),'ignore')
                self.maybe_add(self.soup.find('section',{'class':'detail-top'}),'ignore')
                self.maybe_add(self.soup.find('footer'),'ignore')
                self.maybe_add(self.soup.findAll('a',{'class':'truncate'}),'ignore')
                self.maybe_add(self.soup.findAll('div',{'class':'truncated'}),'ignore')
                self.maybe_add(self.soup.find('section',{'class':'serves'}), 'yields')
                self.maybe_add(self.soup.find({'itemprop':'recipeYield'}), 'yields')
                self.maybe_add(self.soup.find('span',{'class':'recipe__yield'}),'yields')

                # Do we use automatic settings or not...
                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    self.ignore_unparsed = False

        return CooksIllustratedParser

if __name__ == '__main__':
#if True:
    import sys, os.path
    sys.path = [os.path.abspath('../')]+sys.path
    import web_import_plugin.webpage_importer as webpage_importer
    cip = CooksIllustratedPlugin()
    #url = ''http://www.cookscountry.com/recipes/6922-english-muffin-bread?ref=new_search_experience_7&extcode=MCSKD10L0'
    url = 'http://www.cookscountry.com/recipes/4075-choco-apricot-muffins?ref=new_search_experience_5&extcode=MCSKD10L0'
    reader = LogInWebReader(url)
    reader.read()
    ciParser = cip.get_importer(webpage_importer)
    #ciParser = cip.get_importer(None)
    parser = ciParser(reader.url, reader.data, reader.content_type)
    parser.do_run()
    # parser.parse()
    # print 'Unmatched preparsed elements:'
    # for p in parser.preparsed_elements:
    #     if p not in parser.matched:
    #         print '<UNMATCHED>',p,'</UNMATCHED>'
    #     else:
    #         print '<MATCHED>',p,'</MATCHED>'
