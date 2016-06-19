from __future__ import print_function

import tempfile, os, os.path, time

import unittest
import gourmet.gglobals

tmpdir = tempfile.mktemp()
os.makedirs(tmpdir)
gourmet.gglobals.gourmetdir = tmpdir

import gourmet.GourmetRecipeManager
import gourmet.backends.db

gourmet.backends.db.RecData.__single = None
gourmet.GourmetRecipeManager.GourmetApplication.__single = None

import importManager

class TestImports (unittest.TestCase):
    def setUp (self):
        self.im = importManager.get_import_manager()

    def testPlugins (self):
        for pi in self.im.importer_plugins:
            print('I wonder, is there a test for ', pi)
            if hasattr(pi,'get_import_tests'):
                for fn,test in pi.get_import_tests():
                    print('Testing ', test, fn)
                    self.__runImporterTest(fn,test)


    def done_callback (self,*args):
        print('done!')
        self.done = True

    def __runImporterTest (self, fn, test):
        self.done = False
        importer = self.im.import_filenames([fn])[0]
        assert importer, 'import_filenames did not return an object'
        while not importer.done:
            time.sleep(0.2)
        print('Done!')
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
