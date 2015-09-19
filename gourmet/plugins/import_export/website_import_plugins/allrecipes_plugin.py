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
                AllRecipesParserBase.preparse(self, False)

        return AllRecipesParser

