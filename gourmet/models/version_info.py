from sqlalchemy import Column, Integer

from meta import Base

class VersionInfo (Base):
    __tablename__ = 'info'

    version_super = Column(Integer) # three part version numbers 2.1.10, etc. 1.0.0
    version_major = Column(Integer)
    version_minor = Column(Integer)
    last_access = Column(Integer)
    rowid = Column(Integer, primary_key=True)

    def __init__(self, version_super, version_major, version_minor,
                 last_access=None, rowid=None):
        self.version_super = version_super
        self.version_major = version_major
        self.version_minor = version_minor
        self.last_access = last_access
        self.rowid = rowid

    def __repr__(self):
        return "<VersionInfo(version='%s, %s, %s', last_access='%s', rowid='%s')>" % \
                 (self.version_super,
                  self.version_major,
                  self.version_minor,
                  self.last_access,
                  self.rowid)

    def __str__(self):
        return "%s.%s.%s" % (self.version_super,
                             self.version_major,
                             self.version_minor)

    def __cmp__(self, other):
        return 100*100*(self.version_super - other.version_super) + \
                   100*(self.version_major - other.version_major) + \
                       (self.version_minor - other.version_minor)
