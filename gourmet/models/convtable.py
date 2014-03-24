from sqlalchemy import Column, Integer, String

from meta import Base

class Convtable (Base):
    __tablename__ = 'convtable'

    id = Column(Integer, primary_key=True)
    ckey = Column(String(150))
    value = Column(String(150))