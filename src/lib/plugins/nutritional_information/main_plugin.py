from gourmet.plugin import MainPlugin
import nutritionGrabberGui, nutrition
from gourmet.gglobals import add_icon

class NutritionMainPlugin (MainPlugin):

    def activate (self, pluggable):
        """Setup nutritional database stuff."""
        add_icon('Nutrition.png','nutritional-info',
                 _('Nutritional Information'),0,0)
        nutritionGrabberGui.check_for_db(pluggable.rd)
        pluggable.nd = nutrition.NutritionData(pluggable.rd,pluggable.conv)
        pluggable.rd.nd = pluggable.nd
