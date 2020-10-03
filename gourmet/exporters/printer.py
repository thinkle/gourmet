from gettext import gettext as _
import gettext

from gourmet.gtk_extras.dialog_extras import show_message, show_traceback
import gourmet.plugin_loader as plugin_loader
from gourmet.plugin import PrinterPlugin


ERR_NO_PLUGIN_MSG = ("To print, activate a plugin that provides printing, "
                     "such as the 'Printing &amp; PDF export' plugin.")


class NoRecRenderer():

    def __init__(self, *args, **kwargs):
        from gourmet.gtk_extras.dialog_extras import show_message
        show_message(label=_('Unable to print: no print plugins are active!'),
                     sublabel=_(ERR_NO_PLUGIN_MSG))
        raise NotImplementedError


class NoSimpleWriter ():

    def __init__(self, *args, **kwargs):
        from gourmet.gtk_extras.dialog_extras import show_message
        show_message(label=_('Unable to print: no print plugins are active!'),
                     sublabel=_(ERR_NO_PLUGIN_MSG))
        raise NotImplementedError


class PrintManager(plugin_loader.Pluggable):

    __single = None

    @classmethod
    def instance(cls):
        if not PrintManager.__single:
            PrintManager.__single = PrintManager()

        return PrintManager.__single

    def __init__(self):
        self.sws = [(-1, NoSimpleWriter)]
        self.rrs = [(-1, NoRecRenderer)]
        plugin_loader.Pluggable.__init__(self,
                                         [PrinterPlugin]
                                         )

    def register_plugin(self, plugin):
        assert isinstance(plugin.simpleWriterPriority, int)
        assert(plugin.SimpleWriter)
        self.sws.append((plugin.simpleWriterPriority,
                         plugin.SimpleWriter))
        assert isinstance(plugin.recWriterPriority, int)
        assert(plugin.RecWriter)
        self.rrs.append((plugin.recWriterPriority,
                         plugin.RecWriter))

    def unregister_plugin(self, plugin):
        self.sws.remove(plugin.simpleWriterPriority,
                        plugin.SimpleWriter)
        self.rrs.remove(plugin.recWriterPriority,
                        plugin.RecWriter)

    def get_simple_writer(self):
        self.sws.sort()
        return self.sws[-1][1]

    def get_rec_renderer(self):
        self.rrs.sort()
        return self.rrs[-1][1]

    def print_recipes(self, rd, recs,
                      parent=None, change_units=None, **kwargs):
        renderer = self.get_rec_renderer()
        if len(recs) == 1:
            title = f'Print recipe "{recs[0].title}"'
        else:
            title = gettext.ngettext(
                'Print %s recipe',
                'Print %s recipes',
                len(recs)) % len(recs)
        try:
            renderer(rd, recs,
                     dialog_title=title,
                     dialog_parent=parent,
                     change_units=change_units,
                     **kwargs)
        except Exception:
            msg = ('Well this is embarassing.'
                   'Something went wrong printing your recipe.')
            show_traceback(label='Error printing', sublabel=_(msg))

    def show_error(self, *args):
        show_message(sublabel='There was an error printing. Apologies')
