import sqlalchemy, sqlalchemy.orm
from sqlalchemy import Integer, Binary, String, Float, Boolean, Numeric, Table, Column, ForeignKey, Text
from sqlalchemy.sql import and_, or_
import gourmet.backends.db
from gourmet.plugin import DatabasePlugin
import parser_data

class NutritionDataPlugin (DatabasePlugin):

    name = 'nutritondata'
    version = 4

    def setup_usda_weights_table (self):
        self.db.usda_weights_table = Table('usda_weights',gourmet.backends.db.Base.metadata,
                                        Column('id',Integer(),primary_key=True),
                                        *[Column(name,gourmet.backends.db.map_type_to_sqlalchemy(typ),**{})
                                          for lname,name,typ in parser_data.WEIGHT_FIELDS]
                                        )
        class UsdaWeight (object):
            pass
        self.db._setup_object_for_table(self.db.usda_weights_table, UsdaWeight)

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
        cols = [Column(name,gourmet.backends.db.map_type_to_sqlalchemy(typ),**(name=='ndbno' and {'primary_key':True} or {}))
                 for lname,name,typ in parser_data.NUTRITION_FIELDS
                 ] + [Column('foodgroup',Text(),**{})]
        #print 'nutrition cols:',cols
        self.db.nutrition_table = Table('nutrition',gourmet.backends.db.Base.metadata,
                                     *cols
                                     )
        class Nutrition (object):
            pass
        self.db._setup_object_for_table(self.db.nutrition_table, Nutrition)
        
        self.setup_usda_weights_table()
        self.setup_nutritionconversions_table()
        self.setup_nutritionaliases_table()

        #gourmet.backends.db.Base.metadata.create_all(rd.db)
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
