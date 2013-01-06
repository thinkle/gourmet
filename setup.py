#!/bin/env python
#
# setup.py for Gourmet

import sys
import glob
import os.path
import os
import fileinput
import string
from types import StringType, ListType, TupleType

from distutils.core import setup
from distutils.command.build_py import build_py as _build_py
from distutils.command.build_scripts import build_scripts as _build_scripts
from distutils.util import convert_path
from DistUtilsExtra.command import *

class build_py(_build_py):
    """build_py command
    
    This specific build_py command will modify module 'build_config' so that it
    contains information on installation prefixes afterwards.
    """

    def build_module (self, module, module_file, package):
        if type(package) is StringType:
            package = string.split(package, '.')
        elif type(package) not in (ListType, TupleType):
            raise TypeError, \
                  "'package' must be a string (dot-separated), list, or tuple"

        if ( module == 'settings' and len(package) == 1
             and package[0] == 'gourmet'
             and 'install' in self.distribution.command_obj):
            iobj = self.distribution.command_obj['install']
            data_dir = iobj.install_data
            if (iobj.root):
                data_dir = data_dir[len(iobj.root):]
            data_dir = os.path.join(data_dir, 'share')

            # abuse fileinput to replace two lines in bin/gourmet
            for line in fileinput.input(module_file, inplace = 1):
                if "data_dir = " in line:
                    line = "data_dir = '%s'\n" % data_dir
                elif "icon_base = " in line:
                    line = "icon_base = '%s'\n" % \
                        os.path.join(data_dir, 'icons', 'hicolor')

                print line,

        _build_py.build_module(self, module, module_file, package)

class build_scripts(_build_scripts):
    """build_scripts command

    This specific build_scripts command will modify the bin/gourmet script
    so that it contains information on installation prefixes afterwards.
    """

    def copy_scripts(self):
        _build_scripts.copy_scripts(self)

        if "install" in self.distribution.command_obj:
            iobj = self.distribution.command_obj["install"]
            lib_dir = iobj.install_lib
            data_dir = iobj.install_data

            if iobj.root:
                lib_dir = lib_dir[len(iobj.root):]
                data_dir = data_dir[len(iobj.root):]

            script = convert_path("bin/gourmet")
            outfile = os.path.join(self.build_dir, os.path.basename(script))

            # abuse fileinput to replace two lines in bin/gourmet
            for line in fileinput.input(outfile, inplace = 1):
                if "lib_dir = '.'" in line:
                    line = "lib_dir = '%s'\n" % lib_dir
                elif "data_dir = '.'" in line:
                    line = "data_dir = '%s'\n" % data_dir

                print line,

# grab the version from our "version" module
# first we have to extend our path to include gourmet/
sys.path.append(os.path.join(os.path.split(__file__)[0],'gourmet'))

import version

if sys.version < '2.2':
    sys.exit('Error: Python-2.2 or newer is required. Current version:\n %s'
             % sys.version)

def modules_check():
    '''Check if necessary modules is installed.
    The function is executed by distutils (by the install command).'''
    try:
        try:
            import gtk
        except RuntimeError:
            print 'Error importing GTK - is there no windowing environment available?'
            print "We're going to ignore this error and live dangerously. Please make"
            print 'sure you have pygtk > 2.3.93 available!'
    except ImportError:
        raise
    mod_list = [#'metakit',
        'Image',
        'reportlab',
        ('pysqlite2','sqlite3')
        ]
    ok = 1
    for m in mod_list:
        if type(m)==tuple:
            have_mod = False
            for mod in m:
                try:
                    exec('import %s'%mod)
                except ImportError:
                    pass
                else:
                    have_mod = True
            if not have_mod:
                ok = False
                print 'Error: %s is Python module is required to install %s'%(
                    ' or '.join(m), name.title()
                    )
        else:
            try:
                exec('import %s' % m)
            except ImportError:
                ok = False
                print 'Error: %s Python module is required to install %s' \
                  % (m, name.title())
    recommended_mod_list = ['PyRTF']
    for m in recommended_mod_list:
        try:
            exec('import %s' % m)
        except ImportError:
            print '%s Python module is recommended for use with %s' \
                  % (m, name.title())
    if not ok:
        sys.exit(1)

def data_files():
    '''Build list of data files to be installed'''
    data_files = []

    ddirs = [
        'data',
        'images',
        'sound',
        'style',
        'ui',
        ]
    for d in ddirs:
        for root, dirs, files in os.walk(d):
            if files:
                files = [os.path.join(root, f) for f in files]
                data_files.append((os.path.join('share','gourmet', root), files))

    # files in /usr/share/X/ (not gourmet)
    files = []
    base = os.path.join('share','gourmet')

    files.extend(data_files)
    files.extend([(os.path.join(base,'ui'), glob.glob(os.path.join('ui','*.ui')))])
    files.extend([(base, ['FAQ', 'LICENSE'])])
    #print 'DATA FILES:',files
    return files

if os.name == 'nt':
    script = [os.path.join('windows','Gourmet.pyw'),
              os.path.join('windows','GourmetDebug.pyw')]
else:
    script = [os.path.join('bin','gourmet')]
    # Run upgrade pre script
    # Importing runs the actual script...
    #import tools.upgrade_pre_script
    #tools.upgrade_pre_script.dump_old_data()

plugins = []

def crawl (base, basename):
    bdir = base
    subdirs = filter(lambda x: os.path.isdir(os.path.join(bdir,x)), os.listdir(bdir))
    for subd in subdirs:
        name = basename + '.' + subd
        plugins.append(name)
        crawl(os.path.join(bdir,subd),name)

crawl('gourmet/plugins', 'gourmet.plugins')

result = setup(
    name = version.name,
    version = version.version,
    #windows = [ {'script':os.path.join('bin','gourmet'),
    #             }],
    description = version.description,
    author = version.author,
    url = version.website,
    license = version.license,
    data_files = data_files(),
    packages = ['gourmet',
                'gourmet.backends',
                'gourmet.defaults',
                'gourmet.gtk_extras',
                'gourmet.importers',
                'gourmet.exporters',
                'gourmet.legacy_db',
                'gourmet.legacy_db.db_085',
                'gourmet.legacy_db.db_09',
                'gourmet.plugins',
                ] + plugins,
    package_data = {'gourmet': ['plugins/*/*.ui', 'plugins/*/images/*.png','plugins/*/*/images/*.png']},
    scripts = script,
    cmdclass={'build' : build_extra.build_extra,
              'build_i18n' :  build_i18n.build_i18n,
              'build_icons' :  build_icons.build_icons,
              'build_py' : build_py,
              'build_scripts' : build_scripts,
             },
    )

