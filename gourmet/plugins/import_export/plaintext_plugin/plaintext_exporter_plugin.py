from __future__ import print_function

from gourmet.plugin import ExporterPlugin
import gourmet.exporters.exporter as exporter
from gettext import gettext as _

TXT = _('Plain Text file')

class PlainTextExporterPlugin (ExporterPlugin):

    label = _('Text Export')
    sublabel = _('Exporting recipes to text file %(file)s.')
    single_completed_string = _('Recipe saved as plain text file %(file)s')
    filetype_desc = TXT
    saveas_filters = [TXT,['text/plain'],['*.txt','*.TXT']]
    saveas_single_filters = [TXT,['text/plain'],['*.txt','*.TXT','']]

    def get_multiple_exporter (self, args):
        return exporter.ExporterMultirec(
            args['rd'],
            args['rv'],
            args['file'],
            one_file=True,
            ext='txt',
            )

    def do_single_export (self, args)    :
        e = exporter.exporter_mult(args['rd'],
                                   args['rec'],
                                   args['out'],
                                   mult=args['mult'],
                                   change_units=args['change_units'],
                                   )
        e.run()

    def run_extra_prefs_dialog (self):
        pass
