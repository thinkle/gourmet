from gourmet.defaults import lang as defaults
import gtk
ingredients_to_check = defaults.keydic.keys()
from nutritionDruid import NutritionInfoDruid
from nutrition import NutritionData
import gourmet.convert
from gourmet.recipeManager import RecipeManager,dbargs

# This is intended to be run as a simple script to get nutritional
# equivalents which can then be copied into DEFAULTS for your locale.

rd = RecipeManager(**dbargs)

import nutritionGrabberGui

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
        nid.glade.get_widget('window1').hide()
        gtk.main_quit()
nid.glade.get_widget('window1').connect('delete-event',quit)
nid.connect('finish',quit)
nid.show()
gtk.main()

rd.changed=True
rd.save()

ofi = '/tmp/locale_specific_nutritional_info.txt'
print 'Writing data to ',ofi
outfi = file(ofi,'w')
outfi.write('{')
for k in ingredients_to_check:
    ndbno = nd.get_ndbno(k)
    if ndbno:
        outfi.write('"%s":(%s,['%(k,ndbno))
        for conv in nd.db.nutritionconversions_table.select(ingkey=k):
            outfi.write('("%s",%s),'%(conv.unit,conv.factor))
        outfi.write(']),\n')
    else:
        print 'No information for ',k
outfi.write('}')
outfi.close()

