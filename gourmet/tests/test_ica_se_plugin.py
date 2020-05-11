import html
import os.path
import unittest
from bs4 import BeautifulSoup, BeautifulStoneSoup

from gourmet.plugins.import_export.website_import_plugins import ica_se_plugin

class DummyImporter(object):

    class WebParser(object):
        pass


class TestIcaPlugin(unittest.TestCase):

    url = "http://www.ica.se/recept/grillad-kyckling-med-melon-712641/"

    def _read_html(self, download=True):
        if download:
            with urllib.request.urlopen(self.url) as response:
                self.text = response.read().decode("utf8")
            return

        filename = os.path.join(os.path.dirname(__file__),
                                "recipe_files",
                                "ica_se.html")
        with open(filename, encoding="utf8") as f:
            data = f.read()
        return data

    def setUp(self):
        self.text = self._read_html(False)
        self.plugin = ica_se_plugin.IcaSePlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), 5)
        self.assertEqual(self.plugin.test_url("https://www.ica.se/rec", self.text), 5)
        self.assertEqual(self.plugin.test_url("https://ica.se/rec", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://ica.com/", self.text), 0)
        self.assertEqual(self.plugin.test_url("http://google.com", self.text), 0)

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

        self.assertTrue(name, "Grillad kyckling med melon")
        self.assertTrue("Huvudrätt" in category)
        self.assertTrue(cooktime, "45 min")
        self.assertEqual(yields, "6 Serving")

        self.assertTrue(
            "Dela varje kycklinglårfilé i 2 bitar. Blanda chilipulver och soja i en skål. Lägg ner kycklingen och blanda runt. Låt stå i kylen 30 minuter." in instructions)
        self.assertTrue(
            "Rätten passar bra till en buffé. Portionerna är beräknade för att passa buffébordet." in modifications)


if __name__ == '__main__':
    unittest.main()
