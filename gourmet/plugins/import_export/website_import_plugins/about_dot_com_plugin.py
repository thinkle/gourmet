from gourmet.plugin import PluginPlugin
import re

class AboutDotComPlugin (PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def do_activate (self, pluggable):
        #print 'Activating ',self,'for',pluggable
        pass

    def test_url (self, url, data):
        if 'about.com' in url:
            return 5

    def get_importer (self, webpage_importer):

        class AboutDotComWebParser (webpage_importer.MenuAndAdStrippingWebParser):

            def preparse (self):
                includes = [('rInt','instructions'),
                            ('rIng','ingredients'),
                            ('rPrp','instructions'),
                            ('articlebody','recipe'),]
                self.preparsed_elements = []
                for i,t in includes:
                    for el in self.soup(id=i):
                        self.preparsed_elements.append((el,t))
                if self.preparsed_elements:
                    self.ignore_unparsed = True
                    self.preparsed_elements.append((self.soup('title')[0],'title'))
                    # Now get rid of the annoying "More... recipes..."
                    for wrapper in ['rPrp','articlebody']:
                        try:
                            boldyLinks = self.soup(id=wrapper)[0]('b')
                            boldyLinks.extend(self.soup(id=wrapper)[0]('a'))
                        except IndexError:
                            pass
                        else:
                            regexp = re.compile('More.*|.*Recipes.*')
                            for bold in boldyLinks:
                                if bold(text=regexp):
                                    self.preparsed_elements.append((bold,'ignore'))
                else:
                    webpage_importer.MenuAndAdStrippingWebParser.preparse(self)

            def cut_sponsored_links (self):
                for sl in self.soup(text=re.compile('.*(Sponsored Links|Advertisement|Cooking Ads).*')):
                    addiv = sl.findParent('div')
                    self.preparsed_elements.append((addiv,'ignore'))
                webpage_importer.MenuAndAdStrippingWebParser.cut_sponsored_links(self)

            def cut_menus (self):
                for mi in self.soup(text=re.compile('.*(Most Popular|Must Reads|By Category|iGoogle|More from About.com).*')):
                    mendiv = mi.findParent('div')
                    self.preparsed_elements.append((mendiv,'ignore'))        
                for mi in self.soup(text='Email'):
                    mendiv = mi.findParent('div')
                    self.preparsed_elements.append((mendiv,'ignore'))
                for div in self.soup('div',attrs={'class':'hlist'}):
                    self.preparsed_elements.append((div,'ignore'))
                webpage_importer.MenuAndAdStrippingWebParser.cut_menus(self)

        return AboutDotComWebParser
        
