from gourmet.plugin import PluginPlugin
import schema_org_parser
from schema_org_parser import Excluder

class AllRecipesPlugin (PluginPlugin):
    target_pluggable = 'webimport_plugin'

    def do_activate (self, pluggable):
        pass
    
    def test_url (self, url, data):
        if 'allrecipes.com' in url: 
            return 5
        return 0

    def get_importer (self, webpage_importer):
        AllRecipesParserBase = schema_org_parser.generate(webpage_importer.WebParser)

        class AllRecipesParser(AllRecipesParserBase):
            def preparse (self):
                AllRecipesParserBase.preparse(self)
                instructions = self.soup.find(attrs={"class": "directLeft"}).find('ol')
                self.preparsed_elements.append((instructions,'instructions'))
                #for li in instructions.findAll('li'):
                #    self.preparsed_elements.append((li,'instructions'))
                preptime = self.soup.find(id='liPrep').find('span')
                self.preparsed_elements.append((preptime,'preptime'))
                cooktime = self.soup.find(id='liCook').find('span')
                self.preparsed_elements.append((cooktime,'cooktime'))

        return AllRecipesParser

