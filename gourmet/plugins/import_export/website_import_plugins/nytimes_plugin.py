from gourmet.plugin import PluginPlugin
from bs4 import BeautifulSoup

from . import schema_org_parser
from .state import WebsiteTestState


NYT_CUISINES = [
    "African",
    "American",
    "Asian",
    "Australian",
    "Austrian",
    "Belgian",
    "Brazilian",
    "British",
    "Cajun",
    "Caribbean",
    "Central American",
    "Chinese",
    "Creole",
    "Cuban",
    "Eastern European",
    "Filipino",
    "French",
    "German",
    "Greek",
    "Icelandic",
    "Indian",
    "Indonesian",
    "Indian",
    "Indonesian",
    "Irish",
    "Italian",
    "Japanese",
    "Jewish",
    "Korean",
    "Latin American",
    "Malaysian",
    "Mediterranean",
    "Mexican",
    "Middle Eastern",
    "Moroccan",
    "New England",
    "Pakitani",
    "Portuguese",
    "Provencal",
    "Russian",
    "Scandinavian",
    "South American",
    "Southern",
    "Southwestern",
    "Spanish",
    "Thai",
    "Tibetan",
    "Turkish",
    "Vietnamese",
]

class NYTPlugin(PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        if 'nytimes.com' in url:
            return WebsiteTestState.SUCCESS
        return WebsiteTestState.FAILED

    def get_importer(self, webpage_importer):
        NYTParserBase = schema_org_parser.generate(webpage_importer.WebParser)
        # NYT doesn't specify cookTime, so we use totalTime instead
        NYTParserBase.schema_org_mappings['totalTime'] = 'cooktime'

        class NYTParser(NYTParserBase):

            def preparse(self):
                NYTParserBase.preparse(self)
                
                if not self.recipe:
                    return

                if "author" in self.recipe:
                    author = self.recipe["author"]["name"]
                    self.preparsed_elements.append((author, "source"))

                if "recipeCuisine" in self.recipe:
                    cuisine = self.recipe["recipeCuisine"].capitalize()
                    if cuisine in NYT_CUISINES:
                        self.preparsed_elements.append((cuisine, "cuisine"))


        return NYTParser

