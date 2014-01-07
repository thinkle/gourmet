version = '0.11.4'
down_version = None

def upgrade(db):
    print 'Fixing broken ingredient-key view from earlier versions.'
    # Drop keylookup_table table, which wasn't being properly kept up
    # to date...
    db.delete_by_criteria(db.keylookup_table,{}) 
    # And update it in accord with current ingredients (less
    # than an ideal decision, alas)
    for ingredient in db.fetch_all(db.ingredients_table,deleted=False):
        db.add_ing_to_keydic(ingredient.item,ingredient.ingkey)
