#!/usr/bin/env python
import os, os.path, pickle, gglobals

class Prefs:
    def __init__ (self, file=os.path.join(gglobals.gourmetdir,'guiprefs')):
        self.file=file
        self.config = {}
        self.load()

    def get (self, key, default=None):
        if not self.config.has_key(key):
            self.config[key]=default
        return self.config[key]

    def has_key (self, k):
        return self.config.has_key(k)

    def __setitem__ (self, k, v):
        self.config[k]=v

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
