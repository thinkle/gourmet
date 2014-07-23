from sqlalchemy import Integer, String, Float, Column

from gourmet.models import meta

class UsdaWeight (meta.Base):
    __tablename__ = 'usda_weights'

    id = Column(Integer,primary_key=True)
    ndbno = Column(Integer, info={'label': "Nutrient Databank Number"})
    seq = Column(Float, info={'label': "Sequence Number"})
    amount = Column(Float, info={'label': "Amount"})
    unit = Column(String(80), info={'label': 'Measure Description'})
    gramwt = Column(Float, info={'label': 'Gram Weight'})
    ndata = Column(Integer, info={'label': 'Data points'})
    stdev = Column(Float, info={'label': 'Standard Deviation'})