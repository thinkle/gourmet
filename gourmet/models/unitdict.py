from sqlalchemy import Column, Integer, String

from gourmet.models import Base

class Unitdict (Base):
    __tablename__ = 'unitdict'

    id = Column(Integer, primary_key=True)
    ukey = Column(String(150))
    value = Column(String(150))