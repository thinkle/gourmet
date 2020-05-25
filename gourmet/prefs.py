import os, os.path, pickle
from gourmet import gglobals

class Prefs:

    __single = None

    @classmethod
    def instance(cls):
        if Prefs.__single is None:
            Prefs.__single = cls()

        return Prefs.__single

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
        if key not in self.config:
            # Except for dictionaries, because, well, we rely on some
            # of the stupid behavior. If our preference is a
            # modifiable object -- i.e. a dictionary or a list -- it
            # is likely the program relies on a modified default being
            # saved... 12/13/06
            if isinstance(default, (dict, list)):
                self.config[key]=default
            return default
        else: return self.config[key]

    def has_key (self, k):
        return k in self.config

    def __contains__(self, k):
        return k in self.config

    def __setitem__ (self, k, v):
        self.config[k]=v
        for hook in self.set_hooks: hook(k,v)

    def __getitem__ (self, k):
        print("~~~", k, self.config)
        return self.config[k]

    def keys (self): return list(self.config.keys())
    def values (self): return list(self.config.values())
    def items (self): return list(self.config.items())

    def save (self):
        if not os.path.exists(os.path.split(self.file)[0]):
            os.makedirs(os.path.split(self.file)[0])
        ofi=open(self.file,'wb')
        pickle.dump(self.config,ofi)

    def load (self):
        if os.path.isfile(self.file):
            ifi=open(self.file,'rb')
            try:
                self.config=pickle.load(ifi)
            except:
                import traceback
                print('ERROR LOADING CONFIGURATION FILE')
                print('Saving a copy of broken configuration file saved as')
                print('%s.broken'%self.file)
                ifi.seek(0)
                ofi = open(self.file+'.broken','w')
                ofi.write(ifi.read())
                ofi.close()
                print(traceback.print_exc())
            else:
                return True
        return False

def get_prefs ():
    return Prefs.instance()

if __name__ == '__main__':
    p = Prefs()
