from sqlalchemy import Column, Integer, String

from meta import Base

# Keep track of the density of items...
class Density (Base):
    __tablename__ = 'density'

    id = Column(Integer, primary_key=True)
    dkey = Column(String(150))
    value = Column(String(150))