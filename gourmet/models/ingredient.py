from sqlalchemy import Column, Integer, Text, Float, Boolean, ForeignKey

from gourmet.models import Base

class Ingredient (Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    refid = Column(Integer, ForeignKey('recipe.id'))
    unit = Column(Text)
    amount = Column(Float)
    rangeamount = Column(Float)
    item = Column(Text)
    ingkey = Column(Text)
    optional = Column(Boolean)
    #Integer so we can distinguish unset from False
    shopoptional = Column(Integer)
    inggroup = Column(Text)
    position = Column(Integer)
    deleted = Column(Boolean)

    def __repr__(self):
        return "<Ingredient(amount='%s', unit='%s', item='%s')>" % \
                (self.amount, self.unit, self.item)

    def __str__(self):
        if self.rangeamount:
            return "%s %s %s %s" % (self.amount, self.rangeamount, self.unit,
                                    self.item)
        else:
            return "%s %s %s" % (self.amount, self.unit, self.item)
