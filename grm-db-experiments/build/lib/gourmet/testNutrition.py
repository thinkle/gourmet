import testInteractive
import nutrition.nutritionLabel as nutritionLabel
import nutrition.nutrition as nutrition
from nutrition.nutritionGrabberGui import check_for_db
import convert

db = testInteractive.db
check_for_db(db)

rec = db.add_rec(
    {'title':'Foo','source':'Fake'}
    )
for a,u,i in [(1,'tsp.','sugar'),
              (4,'tbs.','olive oil, extra-virgin'),
              (1,'clove','garlic'),
              (None,None,'parsley'),
              (1,None,'chive')
              ]:
    db.add_ing(
        {'id':rec.id,
         'amount':a,
         'unit':u,
         'ingkey':i,
         'item':i}
        )

nd = nutrition.NutritionData(
    db,convert.converter()
    )

ni = nd.get_nutinfo_for_inglist(db.get_ings(rec))


nl = nutritionLabel.NutritionLabel({},rec)
nl.set_nutinfo(ni)

import gtk

w = gtk.Window()
w.add(nl)
w.show_all()
gtk.main()
    
