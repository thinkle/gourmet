version = '0.14.8'
down_version = '0.14.0'

from sqlalchemy import Float, String

# Change from servings to yields! ( we use the plural to avoid a headache with keywords)
def upgrade(db):
    # Don't change the table defs here without changing them
    # above as well (for new users) - sorry for the stupid
    # repetition of code.
    db.add_column_to_table(db.recipe_table,('yields',Float()))
    db.add_column_to_table(db.recipe_table,('yield_unit',String(length=32)))
    #db.db.execute('''UPDATE recipes SET yield = servings, yield_unit = "servings" WHERE EXISTS servings''')
    db.recipe_table.update(whereclause=db.recipe_table.c.servings
                           ).values({
            db.recipe_table.c.yield_unit:'servings',
            db.recipe_table.c.yields:db.recipe_table.c.servings
            }
                                    ).execute()
