import os.path
from gettext import gettext as _

from gourmet.gglobals import add_icon
from gourmet.plugin import MainPlugin

from . import nutrition, nutritionGrabberGui


class NutritionMainPlugin (MainPlugin):

    def activate (self, pluggable):
        """Setup nutritional database stuff."""
        add_icon(os.path.join(os.path.split(__file__)[0],'images','Nutrition.png'),
         'nutritional-info',
         _('Nutritional Information'))
        nutritionGrabberGui.check_for_db(pluggable.rd)
        pluggable.nd = nutrition.NutritionData(pluggable.rd,pluggable.conv)
        pluggable.rd.nd = pluggable.nd
