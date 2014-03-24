from sqlalchemy import Column, Integer, String, Text, Float, LargeBinary, Boolean
from sqlalchemy.event import listen
from sqlalchemy.orm import deferred, relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from meta import Base

from time import time

class Recipe (Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    instructions = Column(Text)
    modifications = Column(Text)
    cuisine = Column(Text)
    rating = Column(Integer)
    description = Column(Text)
    source = Column(Text)
    preptime = Column(Integer)
    cooktime = Column(Integer)
    # Note: we're leaving servings
    # around as a legacy column... it is
    # replaced by yields/yield_unit, but
    # update is much easier if it's
    # here, and it doesn't do much harm
    # to have it around.
    servings = Column(Float)
    yields = Column(Float)
    yield_unit = Column(String(32))
    image = deferred(Column(LargeBinary))
    thumb = Column(LargeBinary)
    deleted = Column(Boolean)
    # A hash for uniquely identifying a recipe (based on title etc)
    recipe_hash = Column(String(32))
    # A hash for uniquely identifying a recipe (based on ingredients)
    ingredient_hash = Column(String(32))
    link = Column(Text) # A field for a URL -- we ought to know about URLs
    last_modified = Column(Integer)

    categories = relationship("Category", order_by="Category.category",
                              backref="recipe",
                              cascade="all, delete, delete-orphan")

    ingredients = relationship("Ingredient", order_by="Ingredient.position",
                              backref="recipe", foreign_keys="Ingredient.recipe_id",
                              cascade="all, delete, delete-orphan")

    @hybrid_property
    def categories_string(self):
        return ', '.join(str(c) for c in self.categories)

    @staticmethod
    def update_last_modified(mapper, connection, target):
        target.last_modified = time()

    @classmethod
    def __declare_last__(cls):
        # get called after mappings are completed
        # http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html#declare-last
        listen(cls, 'before_insert', cls.update_last_modified)
        listen(cls, 'before_update', cls.update_last_modified)

#    If we converted our last_modified column type to DateTime, we could use
#    SQL instead of python to produce the timestamp:
#    last_modified =  Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

    def __repr__(self):
        return "<Recipe(title='%s')>" % self.title

    def __str__(self):
        return self.title
