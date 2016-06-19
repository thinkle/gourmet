from __future__ import print_function

from gourmet.plugin import ExporterPlugin
import gourmet.exporters.exporter as exporter
import mealmaster_exporter
from gettext import gettext as _

MMF = _('MealMaster file')

class MealmasterExporterPlugin (ExporterPlugin):

    label = _('MealMaster Export')
    sublabel = _('Exporting recipes to MealMaster file %(file)s.')
    single_completed_string = _('Recipe saved as MealMaster file %(file)s')
    filetype_desc = MMF
    saveas_filters = [MMF,['text/mmf','text/plain'],['*.mmf','*.MMF']]
    saveas_single_filters = saveas_filters

    def get_multiple_exporter (self, args):
        return exporter.ExporterMultirec(
            args['rd'],
            args['rv'],
            args['file'],
            one_file=True,
            ext='mmf',
            exporter=mealmaster_exporter.mealmaster_exporter)

    def do_single_export (self, args)    :
        e = mealmaster_exporter.mealmaster_exporter(args['rd'],
                                                       args['rec'],
                                                       args['out'],
                                                       mult=args['mult'],
                                                       change_units=args['change_units'],
                                                       conv=args['conv'])
        e.run()

    def run_extra_prefs_dialog (self):
        pass
