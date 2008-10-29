import re

from sqlalchemy import *
from gettext import gettext as _

from gourmet import converter

class Entity(object):
    insert_hooks = []
    update_hooks = []
    delete_hooks = []

    def refresh (self):
        session = object_session(self)
        session.refresh(self)

    def merge (self, instance):
        session = object_session(self)
        session.merge(instance)

    def delete (self):
        session = object_session(self)
        self.deleted = True
        session.flush()
        for hook in self.delete_hooks: hook(self)

    def undelete (self):
        session = object_session(self)
        self.deleted = False
        session.flush()
        for hook in self.delete_hooks: hook(self)
        
    def purge (self):
        session = object_session(self)
        session.delete(self)
        session.flush()
        
class EntityExtension(orm.MapperExtension):
    def after_insert (self, mapper, connection, instance):
        for hook in instance.insert_hooks: hook(instance)
        
    def after_update (self, mapper, connection, instance):
        for hook in instance.update_hooks: hook(instance)

class Recipe(Entity):
    def __init__ (self, title):
        self.title = title
    
    def __repr__ (self):
        return "<Recipe('%s')>" % self.title
        
class RecipeExtension(EntityExtension):
    pass

class Ingredient(Entity):
    pass

class Item(Entity):
    def __init__ (self, name=None):
        self.name = name
        
    def __repr__ (self):
        return "<Item('%s')>" % self.name

class Category(Entity):
    def __init__ (self, name):
        self.name = name
        
    def __repr__ (self):
        return "<Category('%s')>" % self.name

class Cuisine(Entity):
    def __init__ (self, name):
        self.name = name
        
    def __repr__ (self):
        return "<Cuisine('%s')>" % self.name
        
class Database(object):

    def __init__ (self, file=None):
        self.engine = create_engine('sqlite:///' + file, echo=False)
        metadata = MetaData()
        
        recipes_table = Table('recipes', metadata,
            Column('id', Integer, primary_key=True),
            Column('title', String(200)),
            Column('cuisine', String),
            Column('servings', Float),
            Column('rating', Integer),
            Column('preptime', Integer),
            Column('cooktime', Integer),
            Column('source', String),
            Column('link', String),
            Column('instructions', String),
            Column('modifications', String),
            Column('notes', String),
            Column('deleted', Boolean, default=False)
        )
        
        items_table = Table('items', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(200)),
        )
        
        categories_table = Table('categories', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(200)),
        )
        
        cuisines_table = Table('cuisines', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(200)),
        )
        
        ingredients_table = Table('ingredients', metadata,
            Column('id', Integer, primary_key=True),
            Column('recipe_id', Integer, ForeignKey('recipes.id')),
            Column('item_id', Integer, ForeignKey('items.id')),
            Column('position', Integer),
            Column('amount', Float),
            Column('range_amount', Float),
            Column('unit', String(20)),
            Column('optional', Boolean)
        )
        
        recs_cats_table = Table('recipes_categories', metadata,
            Column('recipe_id', Integer, ForeignKey('recipes.id')),
            Column('category_id', Integer, ForeignKey('categories.id'))
        )

        mapper(Recipe, recipes_table, 
            properties={
                'ingredients':relation(Ingredient, backref='recipe', order_by=ingredients_table.c.position),
                'categories':relation(Category, backref='recipes', secondary=recs_cats_table)
            },
            extension=RecipeExtension()
        )
        mapper(Ingredient, ingredients_table, properties={
            'item':relation(Item)
        })
        mapper(Item, items_table)
        mapper(Category, categories_table)
        mapper(Cuisine, cuisines_table)

        metadata.create_all(self.engine)
        session = self.Session(bind=self.engine)        
        self.recipes = session.query(Recipe)
    
    def Session (self, bind=None):
        return create_session(bind=bind)        
        
