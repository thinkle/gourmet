from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
import sqlalchemy

import meta
from category import Category
from convtable import Convtable
from crossunit import CrossUnit
from density import Density
from ingredient import Ingredient
from keylookup import KeyLookup
from pantry import Pantry
from plugin_info import PluginInfo
from recipe import Recipe
from shopcat import ShopCat
from shopcatorder import ShopCatOrder
from unitdict import Unitdict
from version_info import VersionInfo

from gourmet.gdebug import debug

import os.path

# Basic setup functions

def initialize_connection(filename, url):
    """Initialize our database connection.

    This should also set new_db accordingly"""
    debug('Initializing DB connection',1)

    if meta.Session is not None:
        return

    meta.Session = sessionmaker()

    def instr(s,subs): return s.lower().find(subs.lower())+1

    # End REGEXP workaround

    # Continue setting up connection...
    if filename:
        meta.new_db = not os.path.exists(filename)
        #print 'Connecting to file ',filename,'new=',new_db
    else:
        meta.new_db = True # ??? How will we do this now?
    #meta.engine = sqlalchemy.create_engine(self.url,strategy='threadlocal')
    #self.base_connection = meta.engine

    if url.startswith('mysql'):
        meta.engine = sqlalchemy.create_engine(url,
                                           connect_args = {'charset':'utf8'})
    else:
        meta.engine = sqlalchemy.create_engine(url)

    if url.startswith('sqlite'):
        # Workaround to create REGEXP function in sqlite
        # New way of adding custom function ensures we create a custom
        # function for every connection created and fixes problems
        # using regexp. Based on code found here:
        # http://stackoverflow.com/questions/8076126/have-an-sqlalchemy-sqlite-create-function-issue-with-datetime-representation
        def regexp(expr, item):
            if item:
                return re.search(expr,item,re.IGNORECASE) is not None
            else:
                return False

        @event.listens_for(meta.engine, 'connect')
        def on_connect (dbapi_con, con_record):
            dbapi_con.create_function('REGEXP',2,regexp)

    base_connection = meta.engine.connect()
    base_connection.begin()
    meta.metadata = sqlalchemy.MetaData(meta.engine)
    # Be noisy... (uncomment for debugging/fiddling)
    # meta.metadata.bind.echo = True
    meta.Session.configure(bind=meta.engine)
    meta.Base.metadata.create_all(meta.engine)
    debug('Done initializing DB connection',1)
