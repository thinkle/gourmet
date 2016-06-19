# encoding: utf-8
from __future__ import print_function

import os.path
import unittest
import BeautifulSoup

from gourmet.plugins.import_export.website_import_plugins import allrecipes_plugin

class DummyImporter(object):
    class WebParser(object):
        pass


class TestAllRecipesPlugin(unittest.TestCase):

    url = "http://allrecipes.com/recipe/asian-beef-with-snow-peas/"

    def _read_html(self):
        filename = os.path.join(os.path.dirname(__file__),
                                'recipe_files',
                                (os.path.splitext(os.path.basename(__file__))[0])[5:-7]+".html")
        return (open(filename).read())

    def setUp(self):
        self.text = self._read_html()
        self.plugin = allrecipes_plugin.AllRecipesPlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.allrecipes.com/recipe", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://allrecipes.com/recipe", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://allrecipes.net/", self.text), 0)
        self.assertEqual(self.plugin.test_url("http://google.com", self.text), 0)

    def test_parse(self):
        # Setup
        parser = self.plugin.get_importer(DummyImporter)()
        parser.soup = BeautifulSoup.BeautifulSoup(self.text,
                            convertEntities=BeautifulSoup.BeautifulStoneSoup.XHTML_ENTITIES,
                        )
        # Do the parsing
        parser.preparse()
        # Pick apart results
        result = parser.preparsed_elements

        ingredients = [r for r in result if r[1] == "ingredients"]
        name = [r for r in result if r[1] == "recipe"][0][0].text
        instructions = [r for r in result if r[1] == "instructions"][0][0].text
        modifications = [r for r in result if r[1] == "modifications"][0][0].text
        preptime = [r for r in result if r[1] == "preptime"][0][0].text
        cooktime = [r for r in result if r[1] == "cooktime"][0][0].text
        yields = [r for r in result if r[1] == "yields"][0][0].text

        # Check results
        self.assertEqual(len(ingredients), 9)
        self.assertTrue('5mins' in preptime)
        self.assertTrue('10mins' in cooktime)
        self.assertEqual(yields, '4 servings')

        self.assertEqual(name, 'Asian Beef with Snow Peas')
        self.assertTrue('Stir-fried beef in a light gingery sauce. Serve over steamed rice or hot egg noodles.' in modifications)
        self.assertTrue('In a small bowl, combine the soy sauce, rice wine, brown sugar and cornstarch. Set aside.' in instructions)
        self.assertTrue('Heat oil in a wok or skillet over medium high heat. Stir-fry ginger and garlic for 30 seconds. Add the steak and stir-fry for 2 minutes or until evenly browned. Add the snow peas and stir-fry for an additional 3 minutes. Add the soy sauce mixture, bring to a boil, stirring constantly. Lower heat and simmer until the sauce is thick and smooth. Serve immediately.' in instructions)

if __name__ == '__main__':
    unittest.main()
