#!/usr/bin/env python
import os
import pickle
import gobject
from gourmet import gglobals

class _Preferences(gobject.GObject):
    """A basic class for handling preferences.

    subclasses could save our preferences in any number of
    ways. We use a rather primitive solution here and simply use
    pickle.

    set_hooks allow us to watch our settings from elsewhere --
    they will be called each time a preference is changed and
    handed the key and value as arguments: hook(key,value).
    """

    __gsignals__ = {
        'changed' : (gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_DETAILED, gobject.TYPE_NONE,())
    }

    def __init__(self, file=os.path.join(gglobals.gourmetdir,'guiprefs')):
        gobject.GObject.__init__(self)
        self.file= file
        self.config = {}
        self.load()

    def get(self, key, default=None):
        """Return a key's value, or default if the key isn't set.
        """
        if not self.config.has_key(key): return default
        else: return self.config[key]

    def has_key(self, k):
        return self.config.has_key(k)

    def __setitem__(self, k, v):
        self.config[k] = v
        self.emit("changed::%s" % k)

    def __getitem__(self, k):
        return self.config[k]

    def keys(self): return self.config.keys()
    def values(self): return self.config.values()
    def items(self): return self.config.items()

    def save(self):
        if not os.path.exists(os.path.split(self.file)[0]):
            os.makedirs(os.path.split(self.file)[0])
        ofi=open(self.file,'w')
        pickle.dump(self.config,ofi)

    def load(self):
        if os.path.isfile(self.file):
            print self.file
            ifi=open(self.file,'r')
            try:
                self.config = pickle.load(ifi)
            except:
                import traceback
                print 'ERROR LOADING CONFIGURATION FILE'
                print 'Saving a copy of broken configuration file saved as'
                print '%s.broken'%self.file
                ifi.seek(0)
                ofi = file(self.file+'.broken','w')
                ofi.write(ifi.read())
                ofi.close()
                print traceback.print_exc()
            else:
                return True
        return False

prefs = _Preferences()

