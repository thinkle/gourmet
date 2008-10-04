import sqlalchemy, sqlalchemy.orm
from sqlalchemy import Integer, Binary, String, Float, Boolean, Numeric, Table, Column, ForeignKey
from sqlalchemy.sql import and_, or_
import gourmet.backends.db
from gourmet.plugin import DatabasePlugin
import parser_data

class NutritionDataPlugin (DatabasePlugin):

    name = 'nutritondata'
    version = 1

    def setup_usda_weights_table (self):
        self.db.usda_weights_table = Table('usda_weights',self.db.metadata,
                                        Column('id',Integer(),primary_key=True),
                                        *[Column(name,gourmet.backends.db.map_type_to_sqlalchemy(typ),**{})
                                          for lname,name,typ in parser_data.WEIGHT_FIELDS]
                                        )
        class UsdaWeight (object):
            pass
        self.db._setup_object_for_table(self.db.usda_weights_table, UsdaWeight)
    
    def setup_nutrition_conversions_table (self):
        self.db.nutritionconversions_table = Table('nutritionconversions',self.db.metadata,
                                                Column('id',Integer(),primary_key=True),
                                                Column('ingkey',String(length=None),**{}),
                                                Column('unit',String(length=None),**{}), 
                                                Column('factor',Float(),**{}), # Factor is the amount we multiply
                                                # from unit to get 100 grams
                                                ) # NUTRITION_CONVERSIONS
        class NutritionConversion (object): pass
        self.db._setup_object_for_table(self.db.nutritionconversions_table, NutritionConversion)

    def create_tables (self, *args):
        print 'nutritional_information.data_plugin.create_tables()'
        cols = [Column(name,gourmet.backends.db.map_type_to_sqlalchemy(typ),**(name=='ndbno' and {'primary_key':True} or {}))
                 for lname,name,typ in parser_data.NUTRITION_FIELDS
                 ] + [Column('foodgroup',String(length=None),**{})]
        #print 'nutrition cols:',cols
        self.db.nutrition_table = Table('nutrition',self.db.metadata,
                                     *cols
                                     )
        class Nutrition (object):
            pass
        self.db._setup_object_for_table(self.db.nutrition_table, Nutrition)
        
        self.setup_usda_weights_table()

        self.db.nutritionaliases_table = Table('nutritionaliases',self.db.metadata,
                                            Column('ingkey',String(length=None),**{'primary_key':True}),
                                            Column('ndbno',Integer,ForeignKey('nutrition.ndbno'),**{}),
                                            Column('density_equivalent',String(length=20),**{}),)
        class NutritionAlias (object): pass
        self.db._setup_object_for_table(self.db.nutritionaliases_table, NutritionAlias)

        self.setup_nutrition_conversions_table()
        
    def update_version (self, gourmet_stored, plugin_stored, gourmet_current, plugin_current):
        if ((gourmet_stored[0] == 0 and gourmet_stored[1] < 14)
            or
            (plugin_stored < 1)):
            print 'RECREATE USDA WEIGHTS TABLE'
            self.db.alter_table('usda_weights',self.setup_usda_weights_table,{},
                             [name for lname,name,typ in parser_data.WEIGHT_FIELDS])
            self.db.alter_table('nutritionconversions',self.setup_nutrition_conversions_table,{},
                             ['ingkey','unit','factor'])
