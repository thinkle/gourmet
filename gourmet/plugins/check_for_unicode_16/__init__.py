from gourmet.plugin import ToolPlugin
from gourmet.prefs import get_prefs

class EnableUTF16Plugin (ToolPlugin):
    ui = ''

    def activate (self, pluggable):
        get_prefs()['utf-16'] = True

    def remove (self):
        get_prefs()['utf-16'] = False
    
plugins = [EnableUTF16Plugin]
