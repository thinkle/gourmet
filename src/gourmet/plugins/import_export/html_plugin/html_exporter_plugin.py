from gettext import gettext as _

from gourmet.plugin import ExporterPlugin

from . import html_exporter

WEBPAGE = _('HTML Web Page')

class HtmlExporterPlugin (ExporterPlugin):

    label = _('Exporting Webpage')
    sublabel = _('Exporting recipes to HTML files in directory %(file)s')
    single_completed_string = _('Recipe saved as HTML file %(file)s')
    filetype_desc = WEBPAGE
    saveas_filters = [WEBPAGE,['text/html'],['*.html']]
    saveas_single_filters =     [WEBPAGE,['text/html'],['*.html','*.htm','*.HTM','*.HTML']]

    def get_multiple_exporter (self, args):
        return html_exporter.website_exporter(
            args['rd'],
            args['rv'],
            args['file'],
            #args['conv'],
            )

    def do_single_export (self, args)    :
        he = html_exporter.html_exporter(
            args['rd'],
            args['rec'],
            args['out'],
            change_units=args['change_units'],
            mult=args['mult'],
            #conv=args['conv']
            )
        he.run()

    def run_extra_prefs_dialog (self):
        pass
