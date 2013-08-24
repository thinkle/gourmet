# encoding: utf-8
import unittest
import BeautifulSoup

from gourmet.plugins.import_export.website_import_plugins import foodnetwork_plugin

class DummyImporter(object):
    class MenuAndAdStrippingWebParser(object):
        pass


class TestFoodnetworkPlugin(unittest.TestCase):

    url = "http://www.foodnetwork.com/recipes/ask-aida/pan-roasted-chicken-with-oranges-and-rosemary-recipe/index.html"

    def _read_html(self):
        filename = __file__.rsplit(".", 1)[0]+".html"
        return (open(filename).read())

    def setUp(self):
        self.text = self._read_html()
        self.plugin = foodnetwork_plugin.FoodNetworkPlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.foodnetwork.com/rec", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://foodnetwork.com/rec", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.foodnetwork.com", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.foodnetwork.net", self.text), 0)
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

        ingredients = [r for r in result if r[1] == "ingredients"][0][0]
        ingredients = [i for i in ingredients if type(i) == BeautifulSoup.Tag]
        name = [r for r in result if r[1] == "title"][0][0][0].text
        instructions = [r for r in result if r[1] == "recipe"][0][0].text

        # Check results
        self.assertEqual(len(ingredients), 8)

        self.assertTrue('Pan-Roasted Chicken with Oranges and Rosemary' in name)

        self.assertTrue('Heat oven to 450 degrees F and arrange rack in middle.' in instructions)
        self.assertTrue('Let rest 5 minutes before serving.' in instructions)

        self.assertFalse('You must be logged in to review this recipe.' in instructions)



if __name__ == '__main__':
    unittest.main()
