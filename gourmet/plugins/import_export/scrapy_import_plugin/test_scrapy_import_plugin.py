import unittest
import md5
import requests
from scrapy.selector import Selector
import json
import os

from gourmet.plugins.import_export.scrapy_import_plugin.essenUndTrinken_plugin import EssenUndTrinkenPlugin

class TestScrapyImporters(unittest.TestCase):
    def _downloadItem(self, url):
        r = requests.get(url)
        self.assertEqual(r.status_code, 200, "Problem downloading page")
        return r.content
        
    def _testPlugin(self, url, plugin):
        """ This is a generic testing method which will load the url from
        remote and pass it to the parser. Finally the received recipe structure
        will be compared against reference data inside testData.
        """
        urlHash = md5.new(url).hexdigest()
        print "Testing Url: %s hash: %s" %(url,urlHash)
                
        data = self._downloadItem( url )
        
        self.assertGreaterEqual(plugin.test_url( url, data ), 1 )

        parser = plugin.get_parser()
        recipe = parser.parse( Selector(text=data) )

        # Load test data ...
        testOk = True
        testDataDir = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'testData' )
        refFileName = os.path.join(testDataDir,urlHash+".json")
        try:
            with open(refFileName) as infile:    
                recipeReference = json.load(infile)

            if recipe != recipeReference:
                print "parsed recipe and reference differs"
                testOk = False
        except IOError:
            print "No reference found."
            testOk = False

        if not testOk:
            storeFileName = refFileName + ".loaded"
            print "Reference saved to %s; check it for validity" % storeFileName
            with open(storeFileName, 'w') as outfile:
                json.dump(recipe, outfile, sort_keys=True,
                          indent=4, separators=(',', ': '))
            
        self.assert_(testOk, "Failed to get reference data or data is not equal.")
    
    def test_essenUndTrinken(self):
        urls=[
              # This url has multiple ingredient groups
              "http://www.essen-und-trinken.de/rezept/116692/doradenfilets-mit-tomaten-kartoffelpueree.html",
              # Here no ingredient groups
              "http://www.essen-und-trinken.de/rezept/3297/tomaten-kartoffeln.html"
              ]
        
        for url in urls:
            self._testPlugin( url, EssenUndTrinkenPlugin() )
        pass

if __name__ == '__main__':
    unittest.main()
    # Run script from gourmet top directory with:
    # export PYTHONPATH="$(pwd)";  python gourmet/plugins/import_export/scrapy_import_plugin/test_scrapy_import_plugin.py
    