from sqlalchemy import Column, Integer, Text

from gourmet.models import Base

# shopcatsorder - Keep track of the order of shopping categories
class ShopCatOrder (Base):
    __tablename__ = 'shopcatsorder'

    id = Column(Integer, primary_key=True)
    shopcategory = Column(Text(32))
    position = Column(Integer)