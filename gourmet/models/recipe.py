from sqlalchemy import Column, Integer, String, Text, Float, LargeBinary, Boolean, inspect
from sqlalchemy.event import listen
from sqlalchemy.orm import deferred, relationship, composite
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from meta import Base

from gourmet.recipeIdentifier import hash_recipe
from gourmet.util.yields import Yield

from time import time
from copy import copy, deepcopy

class Recipe (Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True)
    title = Column(Text, info={'label': _('Title'), 'widget': 'Entry', 'order': 0})
    instructions = Column(Text)
    modifications = Column(Text)
    cuisine = Column(Text, info={'label': _('Cuisine'), 'widget': 'Combo', 'order': 5})
    rating = Column(Integer, info={'label': _('Rating'), 'widget': 'Entry', 'order': 6})
    description = Column(Text)
    source = Column(Text, info={'label': _('Source'), 'widget': 'Combo', 'order': 7})
    preptime = Column(Integer, info={'label': _('Preparation Time'), 'widget': 'Entry', 'order': 3})
    cooktime = Column(Integer, info={'label': _('Cooking Time'), 'widget': 'Entry', 'order': 2})
    # Note: we're leaving servings
    # around as a legacy column... it is
    # replaced by yields/yield_unit, but
    # update is much easier if it's
    # here, and it doesn't do much harm
    # to have it around.
    servings = Column(Float)
    yields = Column(Float, info={'label': _('Yield'), 'widget': 'Entry', 'order': 1})
    yield_unit = Column(String(32), info={'label': _('Yield Unit'), 'widget': 'Combo'})
    image = deferred(Column(LargeBinary))
    thumb = deferred(Column(LargeBinary))
    deleted = Column(Boolean)
    # A hash for uniquely identifying a recipe (based on title etc)
    recipe_hash = Column(String(32))
    # A hash for uniquely identifying a recipe (based on ingredients)
    ingredient_hash = Column(String(32))
    link = Column(Text, info={'label': _('Website'), 'widget': 'Entry', 'order': 8}) # A field for a URL -- we ought to know about URLs
    last_modified = Column(Integer)

    _categories = relationship("Category", order_by="Category.category",
                              backref="recipe",
                              cascade="all, delete, delete-orphan")

    categories = association_proxy('_categories', 'category')

    ingredients = relationship("Ingredient", order_by="Ingredient.position",
                              backref="recipe", foreign_keys="Ingredient.recipe_id",
                              cascade="all, delete, delete-orphan")

    the_yield = composite(Yield, yields, yield_unit)

    @hybrid_property
    def category(self):
        return ', '.join(c for c in self.categories)

    @category.setter
    def category(self, catstr):
        self.categories = catstr.split(', ')

    category.name='category'
    category.info={'label': _('Category'), 'widget': 'Combo', 'order': 4}

    @hybrid_property
    def stars(self):
        if self.rating:
            return "%g/5 %s"%(self.rating/2.0,_('stars'))

    @staticmethod
    def update_last_modified_and_hashes(mapper, connection, target):
        target.last_modified = time()
        target.recipe_hash, target.ingredient_hash = hash_recipe(target)

    @classmethod
    def __declare_last__(cls):
        # get called after mappings are completed
        # http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html#declare-last
        listen(cls, 'before_insert', cls.update_last_modified_and_hashes)
        listen(cls, 'before_update', cls.update_last_modified_and_hashes)

#    If we converted our last_modified column type to DateTime, we could use
#    SQL instead of python to produce the timestamp:
#    last_modified =  Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

    def __repr__(self):
        return "<Recipe(title='%s')>" % self.title

    def __str__(self):
        return self.title

    def __imul__(self, other):
        if self.the_yield:
            self.the_yield *= other

        for ing in self.ingredients:
            ing *= other

        return self

    def __mul__(self, other):
        result = deepcopy(self)
        return result.__imul__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

REC_ATTRS = [(c.name, c.info['label'], c.info['widget'])
             for c in inspect(Recipe).all_orm_descriptors \
             if (hasattr(c, 'info') and 'label' in c.info and 'widget' in c.info)]

TEXT_ATTR_DIC = {'instructions':_('Instructions'),
                 'modifications':_('Notes'),
                 }
INT_REC_ATTRS = ['rating','preptime','cooktime']
FLOAT_REC_ATTRS = ['yields']
IMAGE_ATTRS = ['image','thumb']
ALL_ATTRS = [r[0] for r in REC_ATTRS] + TEXT_ATTR_DIC.keys() + IMAGE_ATTRS

DEFAULT_ATTR_ORDER = sorted((c.name for c in inspect(Recipe).all_orm_descriptors \
                      if (hasattr(c, 'info') and 'order' in c.info)),
                      key=lambda c: getattr(inspect(Recipe).all_orm_descriptors[c], 'info')['order'])

REC_ATTR_DIC={}
NAME_TO_ATTR = {_('Instructions'):'instructions',
                _('Notes'):'modifications',
                _('Modifications'):'modifications',
                }

DEFAULT_TEXT_ATTR_ORDER = ['instructions',
                           'modifications',]

def build_rec_attr_dic ():
    for attr, name, widget in REC_ATTRS:
        REC_ATTR_DIC[attr]=name
        NAME_TO_ATTR[name]=attr

build_rec_attr_dic()

DEFAULT_OUTPUT_ATTR_ORDER = copy(DEFAULT_ATTR_ORDER)
yield_index = DEFAULT_OUTPUT_ATTR_ORDER.index('yields')
DEFAULT_OUTPUT_ATTR_ORDER[yield_index] = 'the_yield'
rating_index = DEFAULT_OUTPUT_ATTR_ORDER.index('rating')
DEFAULT_OUTPUT_ATTR_ORDER[rating_index] = 'stars'

def diff_recipes (recs):
    diffs = {}
    for attr in ALL_ATTRS:
        vals = [getattr(r,attr) for r in recs]
        # If all our values are identical, there is no
        # difference. Also, if all of our values are bool->False, we
        # don't care (i.e. we don't care about the difference between
        # None and "" or between None and 0).
        if vals != [vals[0]] * len(vals) and True in [bool(v) for v in vals]:
            #if TEXT_ATTR_DIC.has_key(attr):
            #    val1,val2 =
            diffs[attr]=vals
    return diffs