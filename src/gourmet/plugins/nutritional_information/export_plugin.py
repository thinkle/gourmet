from xml.sax.saxutils import escape

from gourmet.defaults.defaults import get_pluralized_form
from gourmet.i18n import _
from gourmet.plugin import BaseExporterPlugin
from gourmet.prefs import Prefs
from gourmet.recipeManager import default_rec_manager

from .nutritionLabel import MAIN_NUT_LAYOUT, MAJOR, SEP


class NutritionBaseExporterPlugin (BaseExporterPlugin):

    def __init__ (self):
        BaseExporterPlugin.__init__(self)
        if Prefs.instance().get('include_nutritional_info_in_export',True):
            self.add_field('Nutritional Information',
                           self.get_nutritional_info_as_text_blob,
                           self.TEXT)

    def get_nutritional_info_as_text_blob (self, rec):
        if not Prefs.instance().get('include_nutritional_info_in_export',True): return None
        txt = ''
        footnotes = ''
        rd = default_rec_manager()
        nd = rd.nd
        nutinfo = nd.get_nutinfo_for_inglist(rd.get_ings(rec),rd)
        ings = rd.get_ings(rec)
        vapor = nutinfo._get_vapor()
        if len(vapor)==len(ings): return None
        if len(vapor) >= 1 and not Prefs.instance().get('include_partial_nutritional_info',False):
            return None
        if rec.yields and rec.yield_unit:
            singular_unit = get_pluralized_form(rec.yield_unit, 1)
            txt += '<i>%s</i>'%((rec.yields and _('Nutritional information reflects amount per %s.'%singular_unit))
                                or
                                _('Nutritional information reflects amounts for entire recipe'))

        if vapor:
            txt = txt + '*'
            footnotes = '\n*' + _('Nutritional information is missing for %s ingredients: %s')%(
                len(vapor),
                ', '.join([escape(nv.__ingobject__.item) for nv in vapor])
                )
        for itm in MAIN_NUT_LAYOUT:
            if itm == SEP:
                # We don't have any nice way of outputting separator
                # lines in our export
                continue
            else:
                label,typ,name,properties,show_percent,unit = itm
                if typ==MAJOR:
                    itm_text = '<b>'+label+'</b>'
                else:
                    itm_text = label
                if unit:
                    itm_text += ' (%s)'%unit
                if isinstance(properties, list):
                    amts = [getattr(nutinfo,att) for att in properties]
                    amt = sum(amts)
                else:
                    amt = getattr(nutinfo,properties)
                if rec.yields:
                    amt = amt/rec.yields
                itm_text += ' %d'%round(amt)
            txt += '\n'+itm_text
        return '\n'.join([txt,footnotes])
