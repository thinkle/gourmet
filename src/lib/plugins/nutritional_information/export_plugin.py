from gourmet.plugin import BaseExporterPlugin
from gourmet.recipeManager import default_rec_manager
import gourmet.defaults
from nutritionLabel import MAIN_NUT_LAYOUT, MAJOR, MINOR, TINY, SEP, SHOW_PERCENT, DONT_SHOW_PERCENT, SEP
from gettext import gettext as _
from xml.sax.saxutils import escape

class NutritionBaseExporterPlugin (BaseExporterPlugin):

    def __init__ (self):
        BaseExporterPlugin.__init__(self)
        self.add_field('Nutritional Information',
                       self.get_nutritional_info_as_text_blob,
                       self.TEXT)

    def get_nutritional_info_as_text_blob (self, rec):
        txt = ''
        footnotes = ''
        rd = default_rec_manager()
        nd = rd.nd
        nutinfo = nd.get_nutinfo_for_inglist(rd.get_ings(rec),rd)
        ings = rd.get_ings(rec)
        vapor = nutinfo._get_vapor()
        if rec.yields and rec.yield_unit:
            singular_unit = gourmet.defaults.get_pluralized_form(rec.yield_unit,1)
            txt += '<i>%s</i>'%((rec.yields and _('Nutritional information reflects amount per %s.'%singular_unit))
                                or
                                _('Nutritional information reflects amounts for entire recipe'))
        if len(vapor)==len(ings): return None
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
                if type(properties) == list:
                    amts = [getattr(nutinfo,att) for att in properties]
                    amt = sum(amts)
                else:
                    amt = getattr(nutinfo,properties)
                if rec.yields:
                    amt = amt/rec.yields
                itm_text += ' %d'%round(amt)
            txt += '\n'+itm_text
        return '\n'.join([txt,footnotes])
