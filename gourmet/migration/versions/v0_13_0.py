version = '0.13.0'
down_version = '0.11.4'

from sqlalchemy import Integer, String, Text
import re

# Add recipe_hash, ingredient_hash and link fields
# (These all get added in 0.13.0)
def upgrade(db):
    # Don't change the table defs here without changing them
    # above as well (for new users) - sorry for the stupid
    # repetition of code.
    db.add_column_to_table(db.recipe_table,('last_modified',Integer()))
    db.add_column_to_table(db.recipe_table,('recipe_hash',String(length=32)))
    db.add_column_to_table(db.recipe_table,('ingredient_hash',String(length=32)))
    # Add a link field...
    db.add_column_to_table(db.recipe_table,('link',Text()))
    #print 'Searching for links in old recipe fields...',sv_text
    URL_SOURCES = ['instructions','source','modifications']
    recs = db.search_recipes(
        [
        {'column':col,
         'operator':'LIKE',
         'search':'%://%',
         'logic':'OR'
         }
        for col in URL_SOURCES
        ])
    for r in recs:
        rec_url = ''
        for src in URL_SOURCES:
            blob = getattr(r,src)
            url = None
            if blob:
                m = re.search('\w+://[^ ]*',blob)
                if m:
                    rec_url = blob[m.start():m.end()]
                    if rec_url[-1] in ['.',')',',',';',':']:
                        # Strip off trailing punctuation on
                        # the assumption this is part of a
                        # sentence -- this will break some
                        # URLs, but hopefully rarely enough it
                        # won't harm (m)any users.
                        rec_url = rec_url[:-1]
                    break
        if rec_url:
            if r.source==rec_url:
                new_source = rec_url.split('://')[1]
                new_source = new_source.split('/')[0]
                db.do_modify_rec(
                    r,
                    {'link':rec_url,
                     'source':new_source,
                     }
                    )
            else:
                db.do_modify_rec(
                    r,
                    {'link':rec_url,}
                    )
    # Add hash values to identify all recipes...
    for r in db.fetch_all(db.recipe_table): db.update_hashes(r)
