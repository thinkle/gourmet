"""SQLAlchemy Metadata and Session object"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Session = None
engine = None
metadata = None
new_db = False