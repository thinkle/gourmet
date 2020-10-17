from gourmet.plugin import PluginPlugin
import re

from .state import WebsiteTestState


class FoodNetworkPlugin(PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url(self, url, data):
        if 'foodnetwork.co.uk' in url:
            return WebsiteTestState.SUCCESS
        return WebsiteTestState.FAILED

    def get_importer(self, webpage_importer):

        class FoodNetworkParser(webpage_importer.WebParser):

            recipe_head_mapping = {
                "Preparation Time": "preptime",
                "Cooking Time": "cooktime",
                "Serves": "yields"
            }

            def preparse(self):
                self.preparsed_elements = []

                title = self.soup.title
                self.preparsed_elements.append((title.text, "title"))

                instructions = self.soup.find("div", class_="recipe-text")
                for p in instructions.find_all("p"):
                    self.preparsed_elements.append((p.text.strip(), "recipe"))

                recipe_head = self.soup.find("ul", class_="recipe-head")
                for entry in self.soup.find_all("li"):
                    span = entry.find("span")
                    if not span:
                        continue
                    key = span.text
                    if key in self.recipe_head_mapping:
                        value = entry.find("strong")
                        if not value:
                            continue
                        self.preparsed_elements.append((value.text, self.recipe_head_mapping[key]))

                ingredients = self.soup.find_all("div", class_="ingredient")
                for ingredient in ingredients:
                    self.preparsed_elements.append((ingredient.text, "ingredients"))

                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    webpage_importer.WebParser.preparse(self)

        return FoodNetworkParser
