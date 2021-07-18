from gi.repository import Gtk
from gtkspellcheck import SpellChecker

from gourmet.plugin import RecEditorPlugin, UIPlugin


class SpellPlugin (RecEditorPlugin, UIPlugin):

    main = None

    ui_string = '''
    '''

    def activate (self, recEditor):
        UIPlugin.activate(self,recEditor)
        for module in self.pluggable.modules:
            tvs = harvest_textviews(module.main)
            for tv in tvs:
                SpellChecker(tv)

def harvest_textviews (widget):
    if isinstance(widget,Gtk.TextView):
        return [widget]
    else:
        tvs = []
        if hasattr(widget,'get_children'):
            for child in widget.get_children():
                tvs.extend(harvest_textviews(child))
        elif hasattr(widget,'get_child'):
            tvs.extend(harvest_textviews(widget.get_child()))
        return tvs
