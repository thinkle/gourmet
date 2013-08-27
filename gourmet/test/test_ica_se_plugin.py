# encoding: utf-8
import os.path
import unittest
import BeautifulSoup

from gourmet.plugins.import_export.website_import_plugins import ica_se_plugin

class DummyImporter(object):
    class WebParser(object):
        pass


class TestIcaPlugin(unittest.TestCase):
    def test_excluder(self):
        url = "/src/doc/"
        excluder = ica_se_plugin.Excluder(url)

        self.assertTrue(excluder.search(url+"index.html"))
        self.assertTrue(excluder.search("index.html"))
        self.assertFalse(excluder.search(url))
        self.assertFalse(excluder.search("http://ica.se/"+url))


    url = "http://www.ica.se/recept/grillad-kyckling-med-melon-712641/"

    def _read_html(self):
        filename = os.path.join(os.path.dirname(__file__),
                                'recipe_files',
                                (os.path.splitext(os.path.basename(__file__))[0])[5:-7]+".html")
        return (open(filename).read())

    def setUp(self):
        self.text = self._read_html()
        self.plugin = ica_se_plugin.IcaSePlugin()

    def test_url(self):
        self.assertEqual(self.plugin.test_url(self.url, self.text), 5)
        self.assertEqual(self.plugin.test_url("http://www.ica.se/rec", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://ica.se/rec", self.text), 5)
        self.assertEqual(self.plugin.test_url("http://ica.com/", self.text), 0)
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
        cooktime = [r for r in result if r[1] == "cooktime"][0][0].text

        # Check results
        self.assertEqual(len(ingredients), 9)

        self.assertTrue('Grillad kyckling med melon' in name)
        self.assertTrue('Tid: Under 45 min' in cooktime)

        print type(instructions)
        self.assertTrue('Dela varje kycklinglårfilé i 2 bitar.' in instructions,
                instructions)
        self.assertTrue('Ta upp dem och skölj ur pannan.' in instructions)
        self.assertTrue('Fri från gluten, laktos, mjölkprotein och ägg.' in instructions)


if __name__ == '__main__':
    unittest.main()
