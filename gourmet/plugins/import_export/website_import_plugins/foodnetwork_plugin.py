from gourmet.plugin import PluginPlugin
import re

class FoodNetworkPlugin(PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url(self, url, data):
        if 'foodnetwork.com' in url:
            return 5
        return 0

    def get_importer(self, webpage_importer):

        class FoodNetworkParser(webpage_importer.MenuAndAdStrippingWebParser):

            imageexcluders = [re.compile('foodnetworkstore|googlead|ft-|banner')]

            def preparse(self):
                self.preparsed_elements = []

                title = self.soup.find("h1", class_="fn_name", itemprop="name")
                self.preparsed_elements.append((title.text, "title"))

                instructions = self.soup.find("div", class_="fn_instructions",
                                              itemprop="recipeInstructions")
                for p in instructions.find_all("p"):
                    self.preparsed_elements.append((p.text.strip(), "recipe"))
                preptime = self.soup.find("meta", itemprop="prepTime")
                if preptime:
                    self.preparsed_elements.append((preptime.text, "preptime"))
                cooktime = self.soup.find("meta", itemprop="cookTime")
                if cooktime:
                    self.preparsed_elements.append((cooktime.text, "cooktime"))
                servings = self.soup.find("meta", itemprop="recipeYield")
                if servings:
                    self.preparsed_elements.append((servings.text, "servings"))
                ingredients = self.soup.find_all("li", itemprop="ingredients")
                for ingredient in ingredients:
                    self.preparsed_elements.append((ingredient.text, "ingredients"))

                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    webpage_importer.MenuAndAdStrippingWebParser.preparse(self)

        return FoodNetworkParser
