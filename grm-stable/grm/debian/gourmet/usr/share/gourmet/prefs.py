#!/usr/bin/env python
import os, os.path, pickle, gglobals

class Prefs:
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'guiprefs')):
        """A basic class for handling preferences.

        subclasses could save our preferences in any number of
        ways. We use a rather primitive solution here and simply use
        pickle.

        set_hooks allow us to watch our settings from elsewhere --
        they will be called each time a preference is changed and
        handed the key and value as arguments: hook(key,value).
        """
        self.file=file
        self.config = {}
        self.load()
        self.set_hooks = []

    def get (self, key, default=None):
        """Return a key's value, or default if the key isn't set.
        """
        # note: we no longer set the key to the default value as a side effect,
        # since this behavior was, well, stupid. 5/7/05
        if not self.config.has_key(key): return default
        else: return self.config[key]

    def has_key (self, k):
        return self.config.has_key(k)

    def __setitem__ (self, k, v):
        self.config[k]=v
        for hook in self.set_hooks: hook(k,v)

    def __getitem__ (self, k):
        return self.config[k]

    def keys (self): return self.config.keys()
    def values (self): return self.config.values()
    def items (self): return self.config.items()

    def save (self):
        if not os.path.exists(os.path.split(self.file)[0]):
            os.makedirs(os.path.split(self.file)[0])
        ofi=open(self.file,'w')
        pickle.dump(self.config,ofi)

    def load (self):
        if os.path.isfile(self.file):
            ifi=open(self.file,'r')
            self.config=pickle.load(ifi)
            return True
        else:
            return False
