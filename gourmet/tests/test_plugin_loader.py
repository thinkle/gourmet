import unittest
import tempfile
import os

from gourmet import gglobals

# clear out Gourmet's DB
tmpdir = tempfile.mktemp()  # TODO: replace deprecated mktemp()
os.makedirs(tmpdir)
gglobals.gourmetdir = tmpdir

from gourmet.GourmetRecipeManager import GourmetApplication
from gourmet.backends import db

db.RecData.__single = None
GourmetApplication.__single = None
# end clearing out code

from gourmet.plugin_loader import get_master_loader

class TestPluginLoader(unittest.TestCase):

    def testDefaultPlugins (self):
        ml = get_master_loader()
        ml.load_active_plugins()
        self.assertEqual(len(ml.errors), 0)  # there should be 0 plugin errors

    def testAvailablePlugins (self):
        ml = get_master_loader()
        # search plugin directories for available plugins
        for st in ml.available_plugin_sets:
            # activate available plugins if not active
            if st not in ml.active_plugins:
                ml.activate_plugin_set(st)
        self.assertEqual(len(ml.errors), 0)  # there should be 0 plugin errors

if __name__ == '__main__':
    unittest.main()
