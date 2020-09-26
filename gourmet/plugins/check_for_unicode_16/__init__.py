from gourmet.plugin import ToolPlugin
from gourmet.prefs import Prefs

class EnableUTF16Plugin (ToolPlugin):
    ui_string = ''

    def activate (self, pluggable):
        Prefs.instance()['utf-16'] = True

    def remove (self):
        Prefs.instance()['utf-16'] = False

plugins = [EnableUTF16Plugin]
