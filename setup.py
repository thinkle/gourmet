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
from DistUtilsExtra.command import build_extra, build_i18n, build_icons

# grab the version from our "version" module
# first we have to extend our path to include gourmet/
srcpath = os.path.split(__file__)[0]
sys.path.append(os.path.join(srcpath, 'gourmet'))
import version

class build_py(_build_py):
    """build_py command
    
    This specific build_py command will modify module 'build_config' so that it
    contains information on installation prefixes afterwards.
    """

    def build_module (self, module, module_file, package):
        _build_py.build_module(self, module, module_file, package)

        if type(package) is StringType:
            package = string.split(package, '.')
        elif type(package) not in (ListType, TupleType):
            raise TypeError, \
                  "'package' must be a string (dot-separated), list, or tuple"

        if ( module == 'settings' and len(package) == 1
             and package[0] == 'gourmet'
             and 'install' in self.distribution.command_obj):
            outfile = self.get_module_outfile(self.build_lib, package, module)

            iobj = self.distribution.command_obj['install']
            lib_dir = iobj.install_lib
            base = iobj.install_data
            if (iobj.root):
                lib_dir = lib_dir[len(iobj.root):]
                base = base[len(iobj.root):]
            base = os.path.join(base, 'share')
            data_dir = os.path.join(base, 'gourmet')

            # abuse fileinput to replace two lines in bin/gourmet
            for line in fileinput.input(outfile, inplace = 1):
                if "base_dir = " in line:
                    line = "base_dir = '%s'\n" % base
                elif "lib_dir = " in line:
                    line = "lib_dir = '%s'\n" % lib_dir
                elif "data_dir = " in line:
                    line = "data_dir = '%s'\n" % data_dir
                elif "doc_base = " in line:
                    line = "doc_base = '%s'\n" % \
                        os.path.join(base, 'doc', 'gourmet')
                elif "icon_base = " in line:
                    line = "icon_base = '%s'\n" % \
                        os.path.join(base, 'icons', 'hicolor')
                elif "locale_base = " in line:
                    line = "locale_base = '%s'\n" % \
                        os.path.join(base, 'locale')
                elif "plugin_base = " in line:
                    line = "plugin_base = data_dir\n"

                print line,

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

if 'py2exe' in sys.argv:
    import py2exe

    kwargs = dict(console=[{'script': os.path.join(srcpath, 'windows','GourmetDebug.pyw'),
                            'dest_base': "Gourmet_debug"}],
                  windows=[{'script': os.path.join(srcpath, 'bin','gourmet'),
                            'dest_base': 'Gourmet'}],
                  options={'py2exe': dict(packages=['gourmet',
                                                    'sqlalchemy',
                                                    'reportlab',
                                                    'reportlab.graphics',
                                                    'reportlab.lib',
                                                    'reportlab.pdfbase',
                                                    'reportlab.pdfgen',
                                                    'reportlab.platypus'],
                                          includes=['cairo', 'gio', 'pango', 'pangocairo', 'atk', 'PIL.ImageDraw', 'BeautifulSoup'],
                                          optimize=2,
                                          compressed=1,
                                          # see http://stackoverflow.com/questions/1979486/py2exe-win32api-pyc-importerror-dll-load-failed
                                          dll_excludes=["mswsock.dll","powrprof.dll"])
                           }
                  )
else:
    kwargs = dict(scripts=[os.path.join('bin','gourmet')])

if 'py2exe' in sys.argv:
    #gtk file inclusion
    import gtk
    # The runtime dir is in the same directory as the module:
    GTK_RUNTIME_DIR = os.path.join(
        os.path.split(os.path.dirname(gtk.__file__))[0], "runtime")

    assert os.path.exists(GTK_RUNTIME_DIR), "Cannot find GTK runtime data"

    GTK_THEME_DEFAULT = os.path.join("share", "themes", "Default")
    GTK_THEME_WINDOWS = os.path.join("share", "themes", "MS-Windows")
    GTK_GTKRC_DIR = os.path.join("etc", "gtk-2.0")
    GTK_GTKRC = "gtkrc"
    GTK_WIMP_DIR = os.path.join("lib", "gtk-2.0", "2.10.0", "engines")
    GTK_WIMP_DLL = "libwimp.dll"

    #If you want the Tango icons:
    GTK_ICONS = os.path.join("share", "icons")

    #There is also localisation data (which I omit, but you might not want to):
    GTK_LOCALE_DATA = os.path.join("share", "locale")

def generate_data_files(prefix, tree, file_filter=None):
    """
    Walk the filesystem starting at "prefix" + "tree", producing a list of files
    suitable for the data_files option to setup(). The prefix will be omitted
    from the path given to setup(). For example, if you have

        C:\Python26\Lib\site-packages\gtk-2.0\runtime\etc\...

    ...and you want your "dist\" dir to contain "etc\..." as a subdirectory,
    invoke the function as

        generate_data_files(
            r"C:\Python26\Lib\site-packages\gtk-2.0\runtime",
            r"etc")

    If, instead, you want it to contain "runtime\etc\..." use:

        generate_data_files(
            r"C:\Python26\Lib\site-packages\gtk-2.0",
            r"runtime\etc")

    Empty directories are omitted.

    file_filter(root, fl) is an optional function called with a containing
    directory and filename of each file. If it returns False, the file is
    omitted from the results.
    """
    data_files = []
    for root, dirs, files in os.walk(os.path.join(prefix, tree)):
        to_dir = os.path.relpath(root, prefix)

        if file_filter is not None:
            file_iter = (fl for fl in files if file_filter(root, fl))
        else:
            file_iter = files

        data_files.append((to_dir, [os.path.join(root, fl) for fl in file_iter]))

    non_empties = [(to, fro) for (to, fro) in data_files if fro]

    return non_empties

def data_files():
    '''Build list of data files to be installed'''
    data_files = []

    for root, dirs, files in os.walk('data'):
        if files:
            files = [os.path.join(root, f) for f in files]
            data_files.append((os.path.join('share','gourmet', root[len('data')+1:]), files))

    # files in /usr/share/X/ (not gourmet)
    files = []
    base = os.path.join('share','gourmet')

    files.extend(data_files)
    files.extend([(os.path.join(base,'ui'), glob.glob(os.path.join('ui','*.ui')))])
    files.extend([(os.path.join('share','doc','gourmet'), ['FAQ', 'LICENSE'])])
    #print 'DATA FILES:',files

    if 'py2exe' in sys.argv:
        files.extend(
            generate_data_files(GTK_RUNTIME_DIR, GTK_THEME_DEFAULT) +
            generate_data_files(GTK_RUNTIME_DIR, GTK_THEME_WINDOWS) +
            generate_data_files(GTK_RUNTIME_DIR, GTK_ICONS) +

            # ...or include single files manually
            [
                (GTK_GTKRC_DIR, [
                    os.path.join(GTK_RUNTIME_DIR,
                        GTK_GTKRC_DIR,
                        GTK_GTKRC)
                ]),

                (GTK_WIMP_DIR, [
                    os.path.join(
                        GTK_RUNTIME_DIR,
                        GTK_WIMP_DIR,
                        GTK_WIMP_DLL)
                ])
            ]
                     )

    return files

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
    description = version.description,
    author = version.author,
    author_email = version.author_email,
    url = version.website,
    license = version.license,
    data_files = data_files(),
    packages = ['gourmet',
                'gourmet.backends',
                'gourmet.defaults',
                'gourmet.gtk_extras',
                'gourmet.importers',
                'gourmet.exporters',
                'gourmet.plugins',
                ] + plugins,
    package_data = {'gourmet': ['plugins/*/*.ui', 'plugins/*/images/*.png','plugins/*/*/images/*.png']},
    cmdclass={'build' : build_extra.build_extra,
              'build_i18n' :  build_i18n.build_i18n,
              'build_icons' :  build_icons.build_icons,
              'build_py' : build_py,
              'build_scripts' : build_scripts,
             },
    **kwargs
    )

