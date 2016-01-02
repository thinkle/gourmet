from gourmet.plugin import ExporterPlugin
import epub_exporter
from gettext import gettext as _

EPUBFILE = _('Epub File')

class EpubExporterPlugin (ExporterPlugin):
    label = _('Exporting epub')
    sublabel = _('Exporting recipes an epub file in directory %(file)s')
    single_completed_string = _('Recipe saved as epub file %(file)s')
    filetype_desc = EPUBFILE
    saveas_filters = [EPUBFILE,['application/epub+zip'],['*.epub']]
    saveas_single_filters = [EPUBFILE,['application/epub+zip'],['*.epub']]

    def get_multiple_exporter (self, args):
        return epub_exporter.website_exporter(
            args['rd'], 
            args['rv'],
            args['file'],
            #args['conv'],
            )

    def do_single_export (self, args)    :
        print "Single export not supported!"

    def run_extra_prefs_dialog (self):
        pass
