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

from plugin_loader import get_master_loader

class Test (unittest.TestCase):

    def testDefaultPlugins (self):
        ml = get_master_loader()
        ml.load_active_plugins()
        print 'active:',ml.active_plugins
        print 'instantiated:',ml.instantiated_plugins
        assert(not ml.errors)

    def testAvailablePlugins (self):
        ml = get_master_loader()
        for st in ml.available_plugin_sets:
            if st not in ml.active_plugins:
                ml.activate_plugin_set(st)

if __name__ == '__main__':
    unittest.main()
