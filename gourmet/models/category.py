from sqlalchemy import Column, Integer, Text, ForeignKey

from meta import Base


class Category (Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))  # recipe ID
    category = Column(Text)  # Category ID
 
    def __init__(self, category):
        self.category = category
 
    def __repr__(self):
        return "<Category(category='%s')>" % self.category

    def __str__(self):
        return self.category
