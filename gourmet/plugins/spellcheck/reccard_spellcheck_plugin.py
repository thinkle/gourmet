import gtk

try:
    import gtkspell
except:
    import gtkspellcheck

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
                try:
                    gtkspell.Spell(tv)
                except:
                    gtkspellcheck.spellcheck.SpellChecker(tv)

def harvest_textviews (widget):
    if isinstance(widget,gtk.TextView):
        return [widget]
    else:
        tvs = []
        if hasattr(widget,'get_children'):
            for child in widget.get_children():
                tvs.extend(harvest_textviews(child))
        elif hasattr(widget,'get_child'):
            tvs.extend(harvest_textviews(widget.get_child()))
        return tvs


        
