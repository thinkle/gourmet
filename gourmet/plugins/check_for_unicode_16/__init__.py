from __future__ import print_function

from gourmet.plugin import ToolPlugin
from gourmet.prefs import get_prefs

class EnableUTF16Plugin (ToolPlugin):
    ui_string = ''

    def activate (self, pluggable):
        get_prefs()['utf-16'] = True

    def remove (self):
        get_prefs()['utf-16'] = False
    
plugins = [EnableUTF16Plugin]
