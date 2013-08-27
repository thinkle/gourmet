"""
A plugin that tries to import recipes from the ica.se site
"""
from gourmet.plugin import PluginPlugin
import re

class Excluder(object):
    def __init__(self, url):
        self.url = url
    def search(self, other_url):
        return not (other_url.endswith(self.url))


class IcaSePlugin (PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        "Is this url from ica.se"
        if 'ica.se' in url:
            return 5
        return 0

    def get_importer (self, webpage_importer):

        class IcaSeParser (webpage_importer.WebParser):

            imageexcluders = []

            def preparse (self):
                self.preparsed_elements = []
                for tag in self.soup.findAll(itemprop=True):
                    itemprop = tag["itemprop"]
                    if itemprop == "name":
                        self.preparsed_elements.append((tag,'recipe'))
                    elif itemprop == "totalTime":
                        self.preparsed_elements.append((tag,'cooktime'))
                    elif itemprop == "ingredients":
                        self.preparsed_elements.append((tag,'ingredients'))
                    elif itemprop == "recipeInstructions":
                        self.preparsed_elements.append((tag,'instructions'))
                    elif itemprop == "image":
                        self.imageexcluders.append(Excluder(tag["src"]))

                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    webpage_importer.WebParser.preparse(self)

        return IcaSeParser

