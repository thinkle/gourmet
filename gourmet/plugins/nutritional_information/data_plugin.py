import sqlalchemy, sqlalchemy.orm
from sqlalchemy import Integer, Binary, String, Float, Boolean, Numeric, Table, Column, ForeignKey, Text
from sqlalchemy.sql import and_, or_
import gourmet.backends.db
from gourmet.plugin import DatabasePlugin
import parser_data

from gourmet.models import meta
from gourmet.models import PluginInfo

class NutritionDataPlugin (DatabasePlugin):

    name = 'nutritondata'
    version = 4

    def setup_usda_weights_table (self):
        class UsdaWeight (object):
            __tablename__ = 'usda_weights'

            id = Column(Integer,primary_key=True)
            ndbno = Column(Integer)
            seq = Column(Float)
            amount = Column(Float)
            unit = Column(String(80))
            gramwt = Column(Float)
            ndata = Column(Integer)
            stdev = Column(Float)

        self.db.usda_weights_table = UsdaWeight.__table__

    def setup_nutritionconversions_table (self):
        class NutritionConversion(gourmet.backends.db.Base):
            __tablename__ = 'nutritionconversions'

            id = Column(Integer, primary_key=True)
            ingkey = Column(String(length=255))
            unit = Column(String(length=255))
            factor = Column(Float)
            # Factor is the amount we multiply from unit to get 100 grams

        self.db.nutritionconversions_table = NutritionConversion.__table__

    def setup_nutritionaliases_table (self):
        class NutritionAlias(gourmet.backends.db.Base):
            __tablename__ = 'nutritionaliases'

            id = Column(Integer, primary_key=True)
            ingkey = Column(Text)
            ndbno = Column(Integer,ForeignKey('nutrition.ndbno'))
            density_equivalent = Column(Text(length=20))

        self.db.nutritionaliases_table = NutritionAlias.__table__

    def do_add_nutrition (self, d):
        return self.db.do_add_and_return_item(self.db.nutrition_table,d,id_prop='ndbno')

    def create_tables (self, *args):
        #print 'nutritional_information.data_plugin.create_tables()'

        class Nutrition (meta.Base):
            __tablename__ = 'nutrition'

            ndbno = Column(Integer, primary_key=True)
            desc = Column(String(100))
            water = Column(Float)
            kcal = Column(Float)
            protein = Column(Float)
            lipid = Column(Float)
            ash = Column(Float)
            carb = Column(Float)
            fiber = Column(Float)
            sugar = Column(Float)
            calcium = Column(Float)
            iron = Column(Float)
            magnesium = Column(Float)
            phosphorus = Column(Float)
            potassium = Column(Float)
            sodium = Column(Float)
            zinc = Column(Float)
            copper = Column(Float)
            manganese = Column(Float)
            selenium = Column(Float)
            vitaminc = Column(Float)
            thiamin = Column(Float)
            riboflavin = Column(Float)
            niacin = Column(Float)
            pantoacid = Column(Float)
            vitaminb6 = Column(Float)
            folatetotal = Column(Float)
            folateacid = Column(Float)
            foodfolate = Column(Float)
            folatedfe = Column(Float)
            choline = Column(Float)
            vitb12 = Column(Float)
            vitaiu = Column(Float)
            vitarae = Column(Float)
            retinol = Column(Float)
            alphac = Column(Float)
            betac = Column(Float)
            betacrypt = Column(Float)
            lypocene = Column(Float)
            lutzea = Column(Float)
            vite = Column(Float)
            vitk = Column(Float)
            fasat = Column(Float)
            famono = Column(Float)
            fapoly = Column(Float)
            cholestrl = Column(Float)
            gramwt1 = Column(Float)
            gramdsc1 = Column(String(100))
            gramwt2 = Column(Float)
            gramdsc2 = Column(String(100))
            refusepct = Column(Float)
            foodgroup = Column(Text)

        self.db.nutrition_table = Nutrition.__table__
        
        self.setup_usda_weights_table()
        self.setup_nutritionconversions_table()
        self.setup_nutritionaliases_table()

        meta.Base.metadata.create_all(meta.engine)
        self.db.do_add_nutrition = self.do_add_nutrition

    def update_version (self, stored_plugin_version, current_plugin_version):
        if (stored_plugin_version < PluginInfo(0, 14, 0))
            or
            (stored_plugin_version.plugin_version < 1)):
            print 'RECREATE USDA WEIGHTS TABLE'
            self.db.alter_table('usda_weights',self.setup_usda_weights_table,{},
                             [name for lname,name,typ in parser_data.WEIGHT_FIELDS])
            self.db.alter_table('nutritionconversions',self.setup_nutritionconversions_table,{},
                             ['ingkey','unit','factor'])
        if stored_plugin_version.plugin_version == '1':
            # Add choline
            self.db.add_column_to_table(self.db.nutrition_table,
                                        ('choline',
                                         gourmet.backends.db.map_type_to_sqlalchemy('float'),
                                         {})
                                        )
        if stored_plugin_version.plugin_version in ['1','2']:
            # Add a primary key Integer column named id.
            self.db.alter_table('nutritionaliases',self.setup_nutritionaliases_table,
                 {},['ingkey','ndbno','density_equivalent'])

        if stored_plugin_version.plugin_version in ['1','2','3']:
            # Set the length parameter of the ingkey and unit Strings to 255.
            self.db.alter_table('nutritionconversions',self.setup_nutritionconversions_table,
                 {},['id','factor'])
