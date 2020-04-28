import sys
import glob
import os.path
import os
import fileinput

from distutils.command.build_py import build_py as _build_py
from distutils.command.build_scripts import build_scripts as _build_scripts
from distutils.util import convert_path
# XXX: DistUtilsExtra is not available via `pip3`, use `apt` or whatever your OS provides
from DistUtilsExtra.command import build_extra, build_i18n, build_icons

# grab the version from our "version" module
# first we have to extend our path to include gourmet/
srcpath = os.path.split(__file__)[0]
sys.path.append(os.path.join(srcpath, 'gourmet'))
from gourmet import version

class build_py(_build_py):
    """build_py command

    This specific build_py command will modify module 'build_config' so that it
    contains information on installation prefixes afterwards.
    """

    def build_module (self, module, module_file, package):
        _build_py.build_module(self, module, module_file, package)

        if type(package) is str:
            package = package.split('.')
        elif type(package) not in (list, tuple):
            raise(TypeError, "'package' must be a string (dot-separated), list, or tuple")

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

                print(line),

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

                print(line),

if sys.platform == "win32":
    #gtk file inclusion
    from gi.repository import Gtk
    # The runtime dir is in the same directory as the module:
    GTK_RUNTIME_DIR = os.path.join(
        os.path.split(os.path.dirname(Gtk.__file__))[0], "runtime")

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

    return files

if sys.platform == "win32":
    from cx_Freeze import setup, Executable, build as build_cxf
    import msilib

    class build(build_extra.build_extra, build_cxf):
        def __init__(self, dist):
            build_extra.build_extra.__init__(self, dist)
            build_cxf.__init__(self, dist)

        def get_sub_comands(self):
            build_cxf.sub_commands(self)

        def initialize_options(self):
            build_extra.build_extra.initialize_options(self)
            build_cxf.initialize_options(self)

        def finalize_options(self):
            build_extra.build_extra.finalize_options(self)
            build_cxf.finalize_options(self)

    include_files = []
    for i in data_files():
        for j in i[1]:
            include_files.append((j, i[0]))

    icon_table = [
        ('GourmetIco', msilib.Binary('data/icons/gourmet.ico'))
        ]

    property_table = [
        ('ARPPRODUCTICON', 'GourmetIco'),
        ]

    msi_data = {
        'Icon': icon_table,
        'Property': property_table,
        }

    kwargs = dict(name="Gourmet Recipe Manager",
                  executables=[Executable(
                                          os.path.join(srcpath, 'bin','gourmet'),
                                          base="Win32GUI",
                                          icon="data/icons/gourmet.ico",
                                          shortcutName="Gourmet Recipe Manager",
                                          shortcutDir="ProgramMenuFolder"
                                          )
                               ],
                  options={
                           'build_exe':
                            {
                             'packages': [
                                       'gourmet',
                                       'sqlalchemy',
                                       'reportlab',
                                       'reportlab.graphics',
                                       'reportlab.lib',
                                       'reportlab.pdfbase',
                                       'reportlab.pdfgen',
                                       'reportlab.platypus',
                                       'xml.dom',
                                       'lxml.etree',
                                       'lxml._elementpath'
                                      ],
                             'includes': [
                                      'cairo',
                                      'gio',
                                      'pango',
                                      'pangocairo',
                                      'atk',
                                      'BeautifulSoup'
                                      ],
                            'include_files': [
                                              ('data', '.'),
                                              ('ui', 'ui'),
                                              ('LICENSE', os.path.join('doc', 'LICENSE')),
                                              ('FAQ', os.path.join('doc', 'FAQ')),
                                              (os.path.join(GTK_RUNTIME_DIR, GTK_THEME_DEFAULT), GTK_THEME_DEFAULT),
                                              (os.path.join(GTK_RUNTIME_DIR, GTK_THEME_WINDOWS), GTK_THEME_WINDOWS),
                                              #(os.path.join(GTK_RUNTIME_DIR, GTK_ICONS), GTK_ICONS),
                                              (os.path.join(GTK_RUNTIME_DIR, GTK_GTKRC_DIR, GTK_GTKRC), os.path.join(GTK_GTKRC_DIR, GTK_GTKRC)),
                                              (os.path.join(GTK_RUNTIME_DIR, GTK_WIMP_DIR, GTK_WIMP_DLL), os.path.join(GTK_WIMP_DIR, GTK_WIMP_DLL)),
                                              (os.path.join('build', 'mo'), 'locale'),
                                              (os.path.join("build", "share", "gourmet"), '.'),
                                              (os.path.join("gourmet", 'plugins'), 'plugins')
                                              ],
                             # We're excluding the plugins module from being added to library.zip
                             # and add it via include_files instead in order to faciliate
                             # handling *.gourmet-plugin and extra files (such as *.ui files
                             # and images).
                            'excludes': ['plugins','Tkinter','wx'],
                            'optimize': 2,
                            'compressed':1,
                            'include_msvcr': True,
                            # see http://stackoverflow.com/questions/1979486/py2exe-win32api-pyc-importerror-dll-load-failed
                            # libgcc_s_dw2-1.dll, if present, would crash Gourmet
                            'bin_excludes': ["mswsock.dll", "powrprof.dll","libgcc_s_dw2-1.dll"],
                            },
                           'bdist_msi':
                           {
                            'upgrade_code': '{D19B9EC6-DF39-4C83-BF87-A67776D087FA}',
                            'data': msi_data
                            }
                           }
                  )
else:
    from distutils.core import setup
    build = build_extra.build_extra
    kwargs = dict(
                  name=version.name,
                  data_files=data_files(),
                  scripts=[os.path.join('bin','gourmet')]
                  )

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
    version=version.version,
    description=version.description,
    author=version.author,
    author_email=version.author_email,
    url=version.website,
    license=version.license,
    packages=['gourmet',
              'gourmet.backends',
              'gourmet.util',
              'gourmet.defaults',
              'gourmet.gtk_extras',
              'gourmet.importers',
              'gourmet.exporters',
              'gourmet.plugins',
              ] + plugins,
    package_data={'gourmet': ['plugins/*/*.ui', 'plugins/*/images/*.png', 'plugins/*/*/images/*.png']},
    cmdclass={'build': build,
              'build_i18n': build_i18n.build_i18n,
              'build_icons': build_icons.build_icons,
              'build_py': build_py,
              'build_scripts': build_scripts,
              },
    **kwargs
)
