from gourmet.plugin import PluginPlugin
from . import schema_org_parser

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

                yields = self.soup.find("div", class_="recipe-adjust-servings__original-serving")
                if yields:
                    yields = yields.text
                    yields = yields.split("yields ")[1].replace("  ", " ").strip()
                    self.preparsed_elements.append((yields, "yields"))

        return AllRecipesParser

