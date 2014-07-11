from sqlalchemy import Integer, String, Float, Column

from gourmet.models import meta

class NutritionConversion(meta.Base):
    __tablename__ = 'nutritionconversions'

    id = Column(Integer, primary_key=True)
    ingkey = Column(String(length=255))
    unit = Column(String(length=255))
    factor = Column(Float)
    # Factor is the amount we multiply from unit to get 100 grams