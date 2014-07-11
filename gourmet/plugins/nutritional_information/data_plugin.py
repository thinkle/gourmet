import sqlalchemy, sqlalchemy.orm
from sqlalchemy import Integer, Binary, String, Float, Boolean, Numeric, Table, Column, ForeignKey, Text
from sqlalchemy.sql import and_, or_
import gourmet.backends.db
from gourmet.plugin import DatabasePlugin
import parser_data

from gourmet.models import meta
from gourmet.models import PluginInfo

from models import Nutrition, NutritionAlias, NutritionConversion, UsdaWeight

class NutritionDataPlugin (DatabasePlugin):

    name = 'nutritondata'
    version = 4

    def setup_usda_weights_table (self):
        self.db.usda_weights_table = UsdaWeight.__table__

    def setup_nutritionconversions_table (self):
        self.db.nutritionconversions_table = NutritionConversion.__table__

    def setup_nutritionaliases_table (self):
        self.db.nutritionaliases_table = NutritionAlias.__table__

    def do_add_nutrition (self, d):
        return self.db.do_add_and_return_item(self.db.nutrition_table,d,id_prop='ndbno')

    def create_tables (self, *args):
        #print 'nutritional_information.data_plugin.create_tables()'

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
