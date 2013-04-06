from gourmet.plugin import ExporterPlugin
import gourmet.plugins.import_export.pdf_plugin.pdf_exporter as pdf_exporter
import print_plugin
from gettext import gettext as _
from gtk import PRINT_OPERATION_ACTION_EXPORT

PDF = _('PDF (Portable Document Format)')

class CairoPdfExporterPlugin (ExporterPlugin):

    label = _('PDF Export')
    sublabel = _('Exporting recipes to PDF %(file)s.')
    single_completed_string = _('Recipe saved as PDF %(file)s')
    filetype_desc = PDF
    saveas_filters = [PDF,['application/pdf'],['*.pdf']]
    saveas_single_filters = [PDF,['application/pdf'],['*.pdf']]
    mode = 'wb'

    def get_multiple_exporter (self, args):
        return print_plugin.PdfExporterMultiDoc(args['rd'],
                                                args['rv'],
                                                args['file'],
                                                pdf_args=args['extra_prefs'],
                                                )
    def do_single_export (self, args):
        # We don't need an open file, just the filename!
        f = args['out']
        filename = f.name
        f.close()
        print_plugin.GtkPrintOperationWriter(args['rd'],
                                       [args['rec']],
                                       mult=args['mult'],
                                       change_units=args['change_units'],
                                       filename=filename,
                                       pdf_args=args['extra_prefs'],
                                       action=PRINT_OPERATION_ACTION_EXPORT,
                                 )

    def run_extra_prefs_dialog (self):
        return pdf_exporter.get_pdf_prefs()

    def get_default_prefs (self):
        return pdf_exporter.DEFAULT_PDF_ARGS
