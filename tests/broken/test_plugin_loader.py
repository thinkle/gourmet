import os
import shutil
import tempfile
import unittest

from gourmet import gglobals


class Test (unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # preserve the current gourmet working directory
        cls.original_gourmetdir = gglobals.gourmetdir

        # create a temporary test directory
        cls.tmp_dir = tempfile.mkdtemp()
        gglobals.gourmetdir = cls.tmp_dir

        # Continue to import with 'gourmetdir' set to 'tmp_dir',
        # Tests need to setup their own test workspace, otherwise 'gourmetdir' is set to '~/.gourmet' which could
        # result in the user gourmet database and other files being corrupted.
        # This attempt at isolation only really works if you're running this test module alone, not after others.
        from gourmet.plugin_loader import get_master_loader  # noqa: E402 import not at top of file

        cls.ml = get_master_loader()

    @classmethod
    def tearDownClass(cls):
        # restore the original gourmet working directory location
        gglobals.gourmetdir = cls.original_gourmetdir

        # delete temporary test directory
        shutil.rmtree(cls.tmp_dir)

    def testDefaultPlugins (self):
        self.ml.load_active_plugins()
        print('active:',self.ml.active_plugins)
        print('instantiated:',self.ml.instantiated_plugins)
        self.assertEqual(len(self.ml.errors), 0)  # there should be 0 plugin errors

    def testAvailablePlugins (self):
        # search module directories for available plugins
        for module_name, plugin_set in self.ml.available_plugin_sets.items():
            if module_name not in self.ml.active_plugin_sets:
                self.ml.activate_plugin_set(plugin_set)
        self.ml.save_active_plugins()
        assert os.path.exists(self.ml.active_plugin_filename)
        self.assertEqual(len(self.ml.errors), 0)  # there should be 0 plugin errors

if __name__ == '__main__':
    unittest.main()
