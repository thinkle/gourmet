import toml
from gourmet.gglobals import gourmetdir


class Prefs(dict):
    """A singleton dictionary for handling preferences.
    set_hooks allow us to watch our settings from elsewhere --
    they will be called each time a preference is changed and
    handed the key and value as arguments: hook(key,value).
    """

    __single = None

    @classmethod
    def instance(cls):
        if Prefs.__single is None:
            Prefs.__single = cls()

        return Prefs.__single

    def __init__(self, filename='guiprefs.toml'):
        super().__init__()
        self.filename = gourmetdir / filename
        self.set_hooks = []
        self.load()

    def save(self):
        self.filename.parent.mkdir(exist_ok=True)
        with open(self.filename, 'w') as fout:
            toml.dump(self, fout)

    def load(self) -> bool:
        if self.filename.is_file():
            with open(self.filename) as fin:
                for k, v in toml.load(fin).items():
                    self.__setitem__(k, v)
            return True
        return False

    def __str__(self):
        return toml.dumps(dict(self.items()))