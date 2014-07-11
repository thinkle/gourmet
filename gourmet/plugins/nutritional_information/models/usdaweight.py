from sqlalchemy import Integer, String, Float, Column

from gourmet.models import meta

class UsdaWeight (meta.Base):
    __tablename__ = 'usda_weights'

    id = Column(Integer,primary_key=True)
    ndbno = Column(Integer)
    seq = Column(Float)
    amount = Column(Float)
    unit = Column(String(80))
    gramwt = Column(Float)
    ndata = Column(Integer)
    stdev = Column(Float)