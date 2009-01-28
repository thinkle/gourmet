from gourmet.plugin import PluginPlugin
import re

class FoodNetworkPlugin (PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        if 'foodnetwork.com' in url:
            return 5

    def get_importer (self, webpage_importer):

        class FoodNetworkParser (webpage_importer.MenuAndAdStrippingWebParser):

            imageexcluders = [re.compile('foodnetworkstore|googlead|ft-|banner')]
            
            def preparse (self):
                headm = re.compile('rcp-head.*')
                textm = re.compile('body-text.*')
                infom = re.compile('rcp-info.*')
                self.preparsed_elements = []
                for el in self.soup('div',{'class':textm}):
                    self.preparsed_elements.append((el,'recipe'))
                for el in self.soup('div',{'class':headm}):
                    self.preparsed_elements.append((el,'recipe'))
                    self.preparsed_elements.append((el('h1'),'title'))
                for el in self.soup('ul',{'class':infom}):
                    self.preparsed_elements.append((el,'recipe'))
                preptime = self.soup('dt',text='Prep')
                if preptime:
                    self.preparsed_elements.append((preptime[0].next,'preptime'))
                cooktime = self.soup('dt',text='Cook')
                if cooktime:
                    self.preparsed_elements.append((cooktime[0].next,'cooktime'))
                servings = self.soup(text='Yield')
                if servings:
                    self.preparsed_elements.append((servings[0].next,'servings'))
                ingredients = self.soup(text='Ingredients')
                if ingredients:
                    if ingredients[0].parent:
                        if ingredients[0].parent.findNextSiblings('ul'):
                            self.preparsed_elements.append((ingredients[0].parent.findNextSiblings('ul')[0],'ingredients'))
                #import sys; sys.argv = []
                #from IPython.Shell import IPShellEmbed
                #ipshell = IPShellEmbed()
                #Ipshell()
                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    webpage_importer.MenuAndAdStrippingWebParser.preparse(self)

        return FoodNetworkParser
        
