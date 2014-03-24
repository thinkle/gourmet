from sqlalchemy import Column, Integer, Text

from meta import Base

# shopcats - Keep track of which shoppin category ingredients are in...
class ShopCat (Base):
    __tablename__ = 'shopcats'

    id = Column(Integer, primary_key=True)
    ingkey = Column(Text(32))
    shopcategory = Column(Text)
    position = Column(Integer)