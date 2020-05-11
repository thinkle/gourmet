import os.path
import unittest
from bs4 import BeautifulSoup

from gourmet.plugins.import_export.website_import_plugins import nytimes_plugin
from gourmet.plugins.import_export.website_import_plugins.state import WebsiteTestState


class DummyImporter(object):

    class WebParser(object):

        def preparse(dummy):
            pass


class TestNytimesPlugin(unittest.TestCase):

    url = "https://cooking.nytimes.com/recipes/1020912-egg-curry"

    @staticmethod
    def _read_html(download=True):
        if download:
            with urllib.request.urlopen(self.url) as response:
                data = response.read().decode("utf8")
            return data

        filename = os.path.join(os.path.dirname(__file__),
                                "recipe_files",
                                "nytimes.html")
        with open(filename, encoding="utf8") as f:
            data = f.read()
        return data

    def setUp(self):
        self.text = TestNytimesPlugin._read_html(False)
        self.plugin = nytimes_plugin.NYTPlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), WebsiteTestState.SUCCESS)
        self.assertEqual(self.plugin.test_url("https://cooking.nytimes.com/recipes", self.text), WebsiteTestState.SUCCESS)
        self.assertEqual(self.plugin.test_url("http://cooking.nytimes.com", self.text), WebsiteTestState.SUCCESS)
        self.assertEqual(self.plugin.test_url("http://cooking.nytimes.net", self.text), WebsiteTestState.FAILED)
        self.assertEqual(self.plugin.test_url("http://google.com", self.text), WebsiteTestState.FAILED)

    def test_parse(self):
        # Setup
        parser = self.plugin.get_importer(DummyImporter)()
        parser.soup = BeautifulSoup(self.text, "lxml")
        parser.text = self.text
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
        cooktime = [r for r in result if r[1] == "cooktime"][0][0]
        yields = [r for r in result if r[1] == "yields"][0][0]
        cuisine = [r for r in result if r[1] == "cuisine"][0][0]

        # Check results
        self.assertEqual(len(ingredients), 14)
        self.assertEqual(cooktime, "1 h")
        self.assertEqual(yields, "4 servings")

        self.assertEqual(name, "Egg Curry")
        self.assertEqual(cuisine, "indian")

        self.assertIn(
            "Add the tomatoes, salt and 1 cup water. Cook, stirring occasionally, until the mixture thickens and the fat rises to the top, about 15 minutes. Stir in the garam masala and lower the heat. If the sauce isn’t runny, stir in 1/2 cup water.", instructions)


if __name__ == '__main__':
    unittest.main()
