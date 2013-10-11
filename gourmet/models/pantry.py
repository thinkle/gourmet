from sqlalchemy import Column, Integer, Text, Boolean

from gourmet.models import Base

# pantry table -- which items are in the "pantry" (i.e. not to
# be added to the shopping list)
class Pantry (Base):
    __tablename__ = 'pantry'

    id = Column(Integer, primary_key=True)
    ingkey = Column(Text(32))
    pantry = Column(Boolean)