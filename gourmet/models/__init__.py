from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from recipe import Recipe
from ingredient import Ingredient