from sqlalchemy import Integer, Column, Text, ForeignKey

from gourmet.models import meta

class NutritionAlias(meta.Base):
    __tablename__ = 'nutritionaliases'

    id = Column(Integer, primary_key=True)
    ingkey = Column(Text)
    ndbno = Column(Integer,ForeignKey('nutrition.ndbno'))
    density_equivalent = Column(Text(length=20))