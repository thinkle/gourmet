import recipeManager
import gglobals, gtk, tempfile

rd = recipeManager.RecipeManager(**recipeManager.dbargs)
recipeManager.dbargs['file']=tempfile.mktemp('.db')
db = recipeManager.RecipeManager(**recipeManager.dbargs)
print 'rd has our default db (loaded from ~/.gourmet/)'
print 'db has an empty db'
print '(no, there\'s no logic to the names)'

# rec = rd.fetch_one(rd.rview,title='Banana Bread')

# w = gtk.Window()
# vb = gtk.VBox()

# ings = rd.get_ings(rec)

# if not ings: print 'Darn'

# for g,ings in rd.order_ings(ings):

#     if g: print g
#     for i in ings:
#         print i.amount,i.unit,i.item,i.ingkey
