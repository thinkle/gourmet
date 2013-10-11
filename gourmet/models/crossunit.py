from sqlalchemy import Column, Integer, String

from gourmet.models import Base

class CrossUnit (Base):
    __tablename__ = 'crossunitdict'

    id = Column(Integer, primary_key=True)
    cukey = Column(String(150))
    value = Column(String(150))