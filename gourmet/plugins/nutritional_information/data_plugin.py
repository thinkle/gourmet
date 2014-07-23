import sqlalchemy, sqlalchemy.orm
from sqlalchemy import Integer, Binary, String, Float, Boolean, Numeric, Table, Column, ForeignKey, Text
from sqlalchemy.sql import and_, or_
from gourmet.backends.db import map_type_to_sqlalchemy
from gourmet.plugin import DatabasePlugin
import parser_data

from gourmet.models import meta
from gourmet.models import PluginInfo

from models import Nutrition, NutritionAlias, NutritionConversion, UsdaWeight

class NutritionDataPlugin (DatabasePlugin):

    name = 'nutritondata'
    version = 4

    def do_add_nutrition (self, d):
        return self.db.do_add_and_return_item(Nutrition.__table__,d,id_prop='ndbno')

    def create_tables (self, *args):
        meta.Base.metadata.create_all(meta.engine)
        self.db.do_add_nutrition = self.do_add_nutrition

    def update_version (self, stored_plugin_version, current_plugin_version):
        if ((stored_plugin_version < PluginInfo(0, 14, 0))
            or
            (stored_plugin_version.plugin_version < 1)):
            print 'RECREATE USDA WEIGHTS TABLE'
            self.db.alter_table(UsdaWeight.__table__,{},
                             [c.name for c in UsdaWeight.__table__.columns[1:]])
            self.db.alter_table(NutritionConversion.__table__,{},
                             ['ingkey','unit','factor'])
        if stored_plugin_version.plugin_version == '1':
            # Add choline
            self.db.add_column_to_table(Nutrition.__table__,
                                        ('choline',
                                         map_type_to_sqlalchemy('float'),
                                         {})
                                        )
        if stored_plugin_version.plugin_version in ['1','2']:
            # Add a primary key Integer column named id.
            self.db.alter_table(NutritionAlias.__table__, {},
                 ['ingkey','ndbno','density_equivalent'])

        if stored_plugin_version.plugin_version in ['1','2','3']:
            # Set the length parameter of the ingkey and unit Strings to 255.
            self.db.alter_table(NutritionConversion.__table__, {},
                 ['id','factor'])
