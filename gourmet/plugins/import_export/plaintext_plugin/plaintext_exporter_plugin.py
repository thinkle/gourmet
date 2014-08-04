from gourmet.plugin import ExporterPlugin
from plaintext_exporter import PlainTextExporter, PlainTextExporterMultirec

TXT = _('Plain Text file')

class PlainTextExporterPlugin (ExporterPlugin):

    label = _('Text Export')
    sublabel = _('Exporting recipes to text file %(file)s.')
    single_completed_string = _('Recipe saved as plain text file %(file)s')
    filetype_desc = TXT
    saveas_filters = [TXT,['text/plain'],['*.txt','*.TXT']]
    saveas_single_filters = [TXT,['text/plain'],['*.txt','*.TXT','']]

    def get_multiple_exporter (self, args):
        return PlainTextExporterMultirec(
            args['rv'],
            args['file']
            )

    def do_single_export (self, args):
        e = PlainTextExporter(args['rec'],
                              args['out'],
                              change_units=args['change_units'],
                              )
        e.run()

    def run_extra_prefs_dialog (self):
        pass
