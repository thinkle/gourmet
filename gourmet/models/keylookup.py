from sqlalchemy import Column, Integer, Text

from gourmet.models import Base

# Keylookup table - for speedy keylookup
class KeyLookup (Base):
    __tablename__ = 'keylookup'

    id = Column(Integer, primary_key=True)
    word = Column(Text)
    item = Column(Text)
    ingkey = Column(Text)
    count = Column(Integer)