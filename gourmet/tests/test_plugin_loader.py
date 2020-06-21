import unittest
import tempfile
import os

import gourmet.gglobals

# clear out Gourmet's DB
tmpdir = tempfile.mktemp()
os.makedirs(tmpdir)
gourmet.gglobals.gourmetdir = tmpdir

import gourmet.GourmetRecipeManager
import gourmet.backends.db

gourmet.backends.db.RecData.__single = None
gourmet.GourmetRecipeManager.GourmetApplication.__single = None
# end clearing out code

from gourmet.plugin_loader import get_master_loader

class Test (unittest.TestCase):

    def testDefaultPlugins (self):
        ml = get_master_loader()
        ml.load_active_plugins()
        print('active:',ml.active_plugins)
        print('instantiated:',ml.instantiated_plugins)
        assert(not ml.errors)

    def testAvailablePlugins (self):
        ml = get_master_loader()
        for module_name, plugin_set in ml.available_plugin_sets.items():
            if module_name not in ml.active_plugin_sets:
                ml.activate_plugin_set(plugin_set)

if __name__ == '__main__':
    unittest.main()
