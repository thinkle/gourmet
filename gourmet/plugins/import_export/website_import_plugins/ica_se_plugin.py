"""
A plugin that tries to import recipes from the ica.se site
"""
from gourmet.plugin import PluginPlugin
from . import schema_org_parser
from .state import WebsiteTestState


class IcaSePlugin (PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        "Is this url from ica.se"
        if 'ica.se' in url:
            return WebsiteTestState.SUCCESS
        return WebsiteTestState.FAILED

    def get_importer(self, webpage_importer):
        IcaSeParserBase = schema_org_parser.generate(webpage_importer.WebParser)
        # ica.se doesn't specify cookTime, so we use totalTime instead
        IcaSeParserBase.schema_org_mappings['totalTime'] = 'cooktime'

        class IcaSeParser(IcaSeParserBase):

            def preparse(self):
                IcaSeParserBase.preparse(self)

                howto = self.soup.find("howto-steps")
                modifications = howto.find("h2")
                if modifications:
                    if modifications.text == "Tips":
                        text = modifications.next_sibling
                        if text:
                            self.preparsed_elements.append((text.strip(), "modifications"))
                
                if not self.recipe:
                    return

                if "nutrition" in self.recipe:
                    entry = self.recipe["nutrition"]
                    if "servingSize" in entry:
                        value = entry["servingSize"]
                        self.preparsed_elements.append((value, "yields"))

                if "recipeCategory" in self.recipe:
                    categories = self.recipe["recipeCategory"].split(",")
                    for category in categories:
                        self.preparsed_elements.append((category, "category"))

        return IcaSeParser

