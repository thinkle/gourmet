import html
import os.path
import unittest

from bs4 import BeautifulSoup, BeautifulStoneSoup

from gourmet.plugins.import_export.website_import_plugins import ica_se_plugin
from gourmet.plugins.import_export.website_import_plugins.state import \
    WebsiteTestState


class DummyImporter(object):

    class WebParser(object):
        pass


class TestIcaPlugin(unittest.TestCase):

    url = "http://www.ica.se/recept/grillad-kyckling-med-melon-712641/"

    @staticmethod
    def _read_html(download=True):
        if download:
            with urllib.request.urlopen(self.url) as response:
                data = response.read().decode("utf8")
            return data

        filename = os.path.join(os.path.dirname(__file__),
                                "recipe_files",
                                "ica_se.html")
        with open(filename, encoding="utf8") as f:
            data = f.read()
        return data

    def setUp(self):
        self.text = TestIcaPlugin._read_html(False)
        self.plugin = ica_se_plugin.IcaSePlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), WebsiteTestState.SUCCESS)
        self.assertEqual(self.plugin.test_url("https://www.ica.se/rec", self.text), WebsiteTestState.SUCCESS)
        self.assertEqual(self.plugin.test_url("https://ica.se/rec", self.text), WebsiteTestState.SUCCESS)
        self.assertEqual(self.plugin.test_url("http://ica.com/", self.text), WebsiteTestState.FAILED)
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
        instructions = [html.unescape(r[0]["text"]) for r in result if r[1] == "recipe"]
        cooktime = [r for r in result if r[1] == "cooktime"][0][0]
        yields = [r for r in result if r[1] == "yields"][0][0]
        category = [r[0] for r in result if r[1] == "category"]
        modifications = [r[0] for r in result if r[1] == "modifications"]

        # Check results
        self.assertEqual(len(ingredients), 9)

        self.assertEqual(name, "Grillad kyckling med melon")
        self.assertIn("Huvudrätt", category)
        self.assertEqual(cooktime, "45 min")
        self.assertEqual(yields, "6 Serving")

        self.assertIn(
            "Dela varje kycklinglårfilé i 2 bitar. Blanda chilipulver och soja i en skål. Lägg ner kycklingen och blanda runt. Låt stå i kylen 30 minuter.", instructions)
        self.assertIn(
            "Rätten passar bra till en buffé. Portionerna är beräknade för att passa buffébordet.", modifications)


if __name__ == '__main__':
    unittest.main()
