# A module to make testing other modules more convenient. We provide a
# Fake RecGui class as a work-around to some poorly thought out
# architecture (basically, we have controllers and views mixed up here
# -- anything that needs to be put into FakeRecGui here is a
# Controller which should be independent of the GUI stuff in an ideal
# world...)

# Force our paths...
import gglobals
gglobals.gladebase = '/usr/share/gourmet/'
gglobals.imagedir = '/usr/share/gourmet/'
gglobals.datad = '/usr/share/gourmet/'

import nutrition.nutritionGrabberGui,nutrition.nutrition
import convert
from convertGui import UnitModel
import shopgui

from reccard import IngInfo

class FakeRecGui:

    prefs = {}
    conf = []
    
    def __init__ (self, rd):
        self.inginfo = IngInfo(rd)
        self.conv = convert.converter()
        nutrition.nutritionGrabberGui.check_for_db(rd)
        self.nd = nutrition.nutrition.NutritionData(rd,self.conv)
        self.rd = rd
        self.umodel = UnitModel(self.conv)
        self.sl = shopgui.ShopGui(self,conv=self.conv)

