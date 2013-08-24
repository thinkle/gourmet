from sqlalchemy import Column, Integer, String, Text, Float, LargeBinary, Boolean, DateTime
from sqlalchemy.orm import validates
from sqlalchemy.event import listen

from gourmet.models import Base

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
    image = Column(LargeBinary)
    thumb = Column(LargeBinary)
    deleted = Column(Boolean)
    # A hash for uniquely identifying a recipe (based on title etc)
    recipe_hash = Column(String(32))
    # A hash for uniquely identifying a recipe (based on ingredients)
    ingredient_hash = Column(String(32))
    link = Column(Text) # A field for a URL -- we ought to know about URLs
    last_modified =  Column(Integer)

