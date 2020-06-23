import unittest
import tempfile
import os
import shutil

from gourmet import gglobals


class Test (unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a temporary test directory
        cls.tmp_dir = tempfile.mkdtemp(".pl")
        gglobals.gourmetdir = cls.tmp_dir

        # continue to import with 'gourmetdir' set to 'tmp_dir', otherwise 'gourmetdir' is set to '~/.gourmet'
        from gourmet.plugin_loader import get_master_loader  # noqa: E402 import not at top of file

        cls.ml = get_master_loader()

    @classmethod
    def tearDownClass(cls):
        # delete temporary test directory
        try:
            shutil.rmtree(cls.tmp_dir)
        except OSError as e:
            print("Error: {} : {}").format(cls.tmp_dir, e.strerror)

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
        self.assertTrue(os.path.exists(self.ml.active_plugin_filename))
        self.assertEqual(len(self.ml.errors), 0)  # there should be 0 plugin errors

if __name__ == '__main__':
    unittest.main()
