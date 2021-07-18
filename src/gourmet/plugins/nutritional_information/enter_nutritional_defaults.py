from gi.repository import Gtk

import gourmet.convert
from gourmet.defaults import lang as defaults
from gourmet.recipeManager import RecipeManager, dbargs

from . import nutritionGrabberGui
from .nutrition import NutritionData
from .nutritionDruid import NutritionInfoDruid

ingredients_to_check = list(defaults.keydic.keys())

# This is intended to be run as a simple script to get nutritional
# equivalents which can then be copied into DEFAULTS for your locale.

rd = RecipeManager(**dbargs)


try:
    nutritionGrabberGui.check_for_db(rd)
except nutritionGrabberGui.Terminated:
    pass

c = gourmet.convert.get_converter()
nd = NutritionData(rd,c)
nid = NutritionInfoDruid(nd,{})
nid.add_ingredients([(k,[(1,'')]) for k in ingredients_to_check])
def quit (*args):
        rd.save()
        nid.ui.get_object('window1').hide()
        Gtk.main_quit()
nid.ui.get_object('window1').connect('delete-event',quit)
nid.connect('finish',quit)
nid.show()
Gtk.main()

rd.changed=True
rd.save()

ofi = '/tmp/locale_specific_nutritional_info.txt'
print('Writing data to ',ofi)
with open(ofi,'w') as outfi:
    outfi.write('{')
    for k in ingredients_to_check:
        ndbno = nd.get_ndbno(k)
        if ndbno:
            outfi.write('"%s":(%s,['%(k,ndbno))
            for conv in nd.db.nutritionconversions_table.select(ingkey=k):
                outfi.write('("%s",%s),'%(conv.unit,conv.factor))
            outfi.write(']),\n')
        else:
            print('No information for ',k)
    outfi.write('}')
