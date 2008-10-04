from gourmet.plugin import MainPlugin
import nutritionGrabberGui, nutrition

class NutritionMainPlugin (MainPlugin):

    def activate (self, pluggable):
        """Setup nutritional database stuff."""
        nutritionGrabberGui.check_for_db(pluggable.rd)
        pluggable.nd = nutrition.NutritionData(pluggable.rd,pluggable.conv)
        pluggable.rd.nd = pluggable.nd
