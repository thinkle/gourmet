import tempfile
import os
import os.path
import time

import unittest
from gourmet import gglobals

# create a temporary directory for tests
tmp_dir = tempfile.mktemp(".im")  # TODO: replace deprecated mktmp()
os.makedirs(tmp_dir)
gglobals.gourmetdir = tmp_dir

# continue to import with gourmetdir location set to tmp_dir
from gourmet.GourmetRecipeManager import GourmetApplication
from gourmet.backends import db

db.RecData.__single = None
GourmetApplication.__single = None

from gourmet.importers import importManager

class TestImports (unittest.TestCase):
    def setUp (self):
        self.im = importManager.get_import_manager()

    def testPlugins (self):
        for pi in self.im.importer_plugins:
            print 'I wonder, is there a test for ', pi
            if hasattr(pi, 'get_import_tests'):
                test_dir = os.path.split(__file__)[0]
                test_dir = os.path.join(test_dir, 'recipe_files')
                for fn, test in pi.get_import_tests():
                    print 'Testing ', test, fn
                    test_fn = os.path.join(test_dir, fn)
                    self.__runImporterTest(test_fn, test)


    def done_callback (self,*args):
        print 'done!'
        self.done = True

    def __runImporterTest (self, fn, test):
        self.done = False
        importer = self.im.import_filenames([fn])[0]
        assert importer, 'import_filenames did not return an object'
        while not importer.done:
            time.sleep(0.2)
        print 'Done!'
        assert importer.added_recs,'Importer did not have any added_recs (%s,%s)'%(fn,test)
        try:
            test(importer.added_recs,fn)
        except:
            import traceback
            self.assertEqual(1,2,'Importer test for %s raised error %s'%(
                (fn, test),
                traceback.format_exc()
                )
                             )

if __name__ == '__main__':
    unittest.main()
