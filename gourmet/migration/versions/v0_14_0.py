version = '0.14.0'
down_version = '0.13.0'

from gourmet.models import Category, Ingredient, KeyLookup

from sqlalchemy.exc import OperationalError

def upgrade(db):
    # Name changes to make working with IDs make more sense
    # (i.e. the column named 'id' should always be a unique
    # identifier for a given table -- it should not be used to
    # refer to the IDs from *other* tables
    db.alter_table(Category.__table__, {'id':'recipe_id'},['category'])

    # Testing whether somehow recipe_id already exists
    # (apparently the version info here may be off? Not
    # sure -- this is coming from an odd bug report by a
    # user reported at...
    # https://sourceforge.net/projects/grecipe-manager/forums/forum/371768/topic/3630545?message=8205906
    try:
        db.db.connect().execute('select recipe_id from ingredients')
    except OperationalError:
        db.alter_table(Ingredient.__table__, {'id':'recipe_id'},
                         ['refid', 'unit', 'amount', 'rangeamount',
                          'item', 'ingkey', 'optional', 'shopoptional',
                          'inggroup', 'position', 'deleted'])
    else:
        print 'Odd -- recipe_id seems to already exist'
    db.alter_table(Keylookup.__table__, {}, ['word','item','ingkey','count'])

