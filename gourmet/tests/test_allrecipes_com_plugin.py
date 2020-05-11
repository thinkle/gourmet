import os.path
import unittest
import urllib.request

from bs4 import BeautifulSoup

from gourmet.plugins.import_export.website_import_plugins import allrecipes_plugin


class DummyImporter(object):

    class WebParser(object):
        pass


class TestAllRecipesPlugin(unittest.TestCase):

    url = "https://allrecipes.com/recipe/asian-beef-with-snow-peas/"

    def _read_html(self, download=True):
        if download:
            with urllib.request.urlopen(self.url) as response:
                self.text = response.read().decode("utf8")
            return

        filename = os.path.join(os.path.dirname(__file__),
                                "recipe_files",
                                "allrecipes_com.html")
        with open(filename, encoding="utf8") as f:
            data = f.read()
        return data

    def setUp(self):
        self.text = self._read_html(False)
        self.plugin = allrecipes_plugin.AllRecipesPlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), 5)
        self.assertEqual(self.plugin.test_url("https://www.allrecipes.com/recipe", self.text), 5)
        self.assertEqual(self.plugin.test_url("https://allrecipes.com/recipe", self.text), 5)
        self.assertEqual(self.plugin.test_url("https://allrecipes.net/", self.text), 0)
        self.assertEqual(self.plugin.test_url("https://google.com", self.text), 0)

    def test_parse(self):
        # Setup
        parser = self.plugin.get_importer(DummyImporter)()
        parser.text = self.text
        parser.soup = BeautifulSoup(self.text, "lxml")
        # Do the parsing
        parser.preparse()
        # Pick apart results
        result = parser.preparsed_elements

        # Result is a list of tuples (text, keyword) and we are searching for the current
        # keyword. On success we retrieve the text itself and add it to the list.
        # For the name we create a list, but have only one text which we retrieve.
        ingredients = [r[0] for r in result if r[1] == "ingredients"]
        name = [r for r in result if r[1] == "title"][0][0]
        instructions = [r[0]["text"] for r in result if r[1] == "recipe"]
        modifications = [r[0] for r in result if r[1] == "modifications"]
        preptime = [r for r in result if r[1] == "preptime"][0][0]
        cooktime = [r for r in result if r[1] == "cooktime"][0][0]
        yields = [r for r in result if r[1] == "yields"][0][0]

        # Check results
        self.assertEqual(len(ingredients), 9)
        self.assertEqual(preptime, "5 min")
        self.assertTrue(cooktime, "10 min")
        self.assertEqual(yields, "4 servings")

        self.assertEqual(name, "Asian Beef with Snow Peas")
        self.assertTrue(
            "Stir-fried beef in a light gingery sauce. Serve over steamed rice or hot egg noodles." in modifications)
        self.assertTrue(
            'In a small bowl, combine the soy sauce, rice wine, brown sugar and cornstarch. Set aside.' in instructions)
        self.assertTrue(
            'Heat oil in a wok or skillet over medium high heat. Stir-fry ginger and garlic for 30 seconds. Add the steak and stir-fry for 2 minutes or until evenly browned. Add the snow peas and stir-fry for an additional 3 minutes. Add the soy sauce mixture, bring to a boil, stirring constantly. Lower heat and simmer until the sauce is thick and smooth. Serve immediately.' in instructions)


if __name__ == '__main__':
    unittest.main()
