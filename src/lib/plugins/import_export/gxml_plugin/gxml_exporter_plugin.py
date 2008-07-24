from gourmet.plugin import ExporterPlugin
import gxml2_exporter

GXML = _('Gourmet XML File')

class GourmetExporterPlugin (ExporterPlugin):

    label = _('Gourmet XML Export')
    sublabel = _('Exporting recipes to Gourmet XML file %(file)s.')
    single_completed_string = _('Recipe saved in Gourmet XML file %(file)s.'),
    filetype_desc = GXML
    saveas_filters = [GXML,['text/xml'],['*.grmt','*.xml','*.XML']]
    saveas_single_filters =     saveas_filters

    def get_multiple_exporter (self, args):
        return gxml2_exporter.recipe_table_to_xml(
            args['rd'],
            args['rv'],
            args['file'],
            progress_func=args['prog'])

    def do_single_export (self, args)    :
        gxml2_exporter.recipe_table_to_xml(args['rd'],
                                           [args['rec']],
                                           args['out'],
                                           change_units=args['change_units'],
                                           mult=args['mult']
                                           ).run()

    def run_extra_prefs_dialog (self):
        pass
