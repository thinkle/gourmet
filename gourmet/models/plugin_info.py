from sqlalchemy import Column, Integer, String, Text

from gourmet.models import Base

class PluginInfo (Base):
    __tablename__ = 'plugin_info'

    plugin = Column(Text)
    # three part version numbers
    # 2.1.10, etc. 1.0.0 -- these
    # contain the Gourmet version
    # at the last time of
    # plugging-in
    id = Column(Integer, primary_key=True)
    version_super = Column(Integer)
    version_major = Column(Integer)
    version_minor = Column(Integer)
    # Stores the last time the plugin was used...
    plugin_version = Column(String(32))

    def __init__(self, plugin,
                 version_super, version_major, version_minor,
                 plugin_version=None, id=None):
        self.plugin = plugin
        self.id = id
        self.version_super = version_super
        self.version_major = version_major
        self.version_minor = version_minor
        self.plugin_version = plugin_version

    def __repr__(self):
        return "<PluginInfo(plugin='%s', id='%s', version='%s, %s, %s', plugin_version='%s')>" % \
                (self.plugin,
                 self.id,
                 self.version_super,
                 self.version_major,
                 self.version_minor,
                 self.plugin_version)

    def __str__(self):
        return "%s.%s.%s - %s v%s" % (self.version_super,
                                      self.version_major,
                                      self.version_minor,
                                      self.plugin,
                                      self.plugin_version)

    def __cmp__(self, other):
        return 100*100*(self.version_super - other.version_super) + \
                   100*(self.version_major - other.version_major) + \
                       (self.version_minor - other.version_minor)
