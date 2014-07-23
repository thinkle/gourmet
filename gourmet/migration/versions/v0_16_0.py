version = '0.16.0'
down_version = '0.14.8'

from sqlalchemy.sql import and_
from sqlalchemy.sql.expression import func

from gourmet.models import Convtable, CrossUnit, Density, Pantry, ShopCat, \
                           ShopCatOrder, Unitdict

def upgrade(db):
    # We need to unpickle Booleans that have erroneously remained
    # pickled during previous Metakit -> SQLite -> SQLAlchemy
    # database migrations.
    db.pantry_table.update().where(db.pantry_table.c.pantry
                                     =='I01\n.'
                                     ).values(pantry=True).execute()
    db.pantry_table.update().where(db.pantry_table.c.pantry
                                     =='I00\n.'
                                     ).values(pantry=False).execute()
    # Unpickling strings with SQLAlchemy is clearly more complicated:
    db.shopcats_table.update().where(
        and_(db.shopcats_table.c.shopcategory.startswith("S'"),
             db.shopcats_table.c.shopcategory.endswith("'\np0\n."))
        ).values({db.shopcats_table.c.shopcategory:
                  func.substr(db.shopcats_table.c.shopcategory,
                              3,
                              func.char_length(
                                db.shopcats_table.c.shopcategory
                              )-8)
                 }).execute()

    # The following tables had Text columns as primary keys,
    # which, when used with MySQL, requires an extra parameter
    # specifying the length of the substring that MySQL is
    # supposed to use for the key. Thus, we're adding columns
    # named id of type Integer and make them the new primary keys
    # instead.
    db.alter_table(ShopCat.__table__, {},['ingkey','shopcategory','position'])
    db.alter_table(ShopCatOrder.__table__, {},['shopcategory','position'])
    db.alter_table(Pantry.__table__, {},['ingkey','pantry'])
    db.alter_table(Density.__table__, {},['dkey','value'])
    db.alter_table(CrossUnit.__table__, {},['cukey','value'])
    db.alter_table(Unitdict.__table__, {},['ukey','value'])
    db.alter_table(Convtable.__table__, {},['ckey','value'])
