import fileinput
import glob
import os
import os.path as op
import sys

import distutils.command
import distutils.command.build
import distutils.command.build_py
import distutils.command.build_scripts
import distutils.core
from distutils.util import convert_path

# grab the version from our "version" module
# first we have to extend our path to include gourmet/
srcpath = op.split(__file__)[0]
sys.path.append(op.join(srcpath, 'gourmet'))

from gourmet import version  # noqa: import not a top of file


class build_extra(distutils.command.build.build):
    """Adds the extra commands to the build target. This class should be used
       with the core distutils"""
    def __init__(self, dist):
        distutils.command.build.build.__init__(self, dist)

        self.user_options.extend([("i18n", None, "use the localisation"),
                                  ("icons", None, "use icons"),
                                  ("kdeui", None, "use kdeui"),
                                  ("help", None, "use help system")])

    def initialize_options(self):
        distutils.command.build.build.initialize_options(self)
        self.i18n = False
        self.icons = False
        self.help = False
        self.kdeui = False

    def finalize_options(self):
        def has_help(command):
            return self.help == "True" or \
                   ("build_help" in self.distribution.cmdclass and not
                    self.help == "False")

        def has_icons(command):
            return self.icons == "True" or \
                   ("build_icons" in self.distribution.cmdclass and not
                    self.help == "False")

        def has_i18n(command):
            return self.i18n == "True" or \
                   ("build_i18n" in self.distribution.cmdclass and not
                    self.i18n == "False")

        def has_kdeui(command):
            return self.kdeui == "True" or \
                   ("build_kdeui" in self.distribution.cmdclass and not
                    self.kdeui == "False")

        distutils.command.build.build.finalize_options(self)
        self.sub_commands.append(("build_i18n", has_i18n))
        self.sub_commands.append(("build_icons", has_icons))
        self.sub_commands.append(("build_help", has_help))

        # must be run before build_py
        self.sub_commands.insert(0, ("build_kdeui", has_kdeui))


class build_i18n(distutils.core.Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not distutils.spawn.find_executable('msgfmt'):
            raise Exception('Gettext msgfmt not fount! '
                            'It is required to compile po files.')

        for filename in os.listdir('po'):
            if not filename.endswith('.po'):
                continue

            # Filenames are LANGUAGE.po
            lang = filename[:-3]

            po = op.join('po', filename)
            directory = op.join('build', 'mo', lang, 'LC_MESSAGES')
            self.mkpath(directory)
            mo = op.join(directory, f'{self.distribution.metadata.name}.mo')

            if distutils.dep_util.newer(po, mo):
                distutils.log.info(f'Compile {po} -> {mo}')
                self.spawn(['msgfmt', '-o', mo, po])

            targetpath = op.join('share', 'locale', lang, 'LC_MESSAGES')
            self.distribution.data_files.append((targetpath, (mo,)))


class build_icons(distutils.cmd.Command):

    description = "select all icons for installation"

    user_options = [('icon-dir=', 'i', 'icon directory of the source tree')]

    def initialize_options(self):
        self.icon_dir = None

    def finalize_options(self):
        if self.icon_dir is None:
            self.icon_dir = os.path.join("data", "icons")

    def run(self):
        data_files = self.distribution.data_files

        for size in glob.glob(os.path.join(self.icon_dir, "*")):
            for category in glob.glob(os.path.join(size, "*")):
                icons = []
                for icon in glob.glob(os.path.join(category, "*")):
                    if not os.path.islink(icon):
                        icons.append(icon)
                if icons:
                    data_files.append(("share/icons/hicolor/%s/%s" %
                                       (os.path.basename(size),
                                        os.path.basename(category)),
                                       icons))


distutils.command.build.build.sub_commands.append(("build_i18n", None))
distutils.command.build.build.sub_commands.append(("build_icons", None))


class build_py(distutils.command.build_py.build_py):
    """build_py command

    This specific build_py command will modify module 'build_config' so that it
    contains information on installation prefixes afterwards.
    """

    def build_module(self, module, module_file, package):
        distutils.command.build_py.build_py.build_module(self, module,
                                                         module_file, package)

        if type(package) is str:
            package = package.split('.')
        elif type(package) not in (list, tuple):
            msg = "'package' must be a string (dot-separated), list, or tuple"
            raise TypeError(msg)

        if (module == 'settings' and len(package) == 1
                and package[0] == 'gourmet'
                and 'install' in self.distribution.command_obj):
            outfile = self.get_module_outfile(self.build_lib, package, module)

            iobj = self.distribution.command_obj['install']
            lib_dir = iobj.install_lib
            base = iobj.install_data
            if (iobj.root):
                lib_dir = lib_dir[len(iobj.root):]
                base = base[len(iobj.root):]
            base = op.join(base, 'share')
            data_dir = op.join(base, 'gourmet')

            # abuse fileinput to replace two lines in bin/gourmet
            for line in fileinput.input(outfile, inplace=1):
                if "base_dir = " in line:
                    line = "base_dir = '%s'\n" % base
                elif "lib_dir = " in line:
                    line = "lib_dir = '%s'\n" % lib_dir
                elif "data_dir = " in line:
                    line = "data_dir = '%s'\n" % data_dir
                elif "doc_base = " in line:
                    line = "doc_base = '%s'\n" % \
                        op.join(base, 'doc', 'gourmet')
                elif "icon_base = " in line:
                    line = "icon_base = '%s'\n" % \
                        op.join(base, 'icons', 'hicolor')
                elif "locale_base = " in line:
                    line = "locale_base = '%s'\n" % \
                        op.join(base, 'locale')
                elif "plugin_base = " in line:
                    line = "plugin_base = data_dir\n"

                print(line),


class build_scripts(distutils.command.build_scripts.build_scripts):
    """build_scripts command

    This specific build_scripts command will modify the bin/gourmet script
    so that it contains information on installation prefixes afterwards.
    """

    def copy_scripts(self):
        distutils.command.build_scripts.build_scripts.copy_scripts(self)

        if "install" in self.distribution.command_obj:
            iobj = self.distribution.command_obj["install"]
            lib_dir = iobj.install_lib
            data_dir = iobj.install_data

            if iobj.root:
                lib_dir = lib_dir[len(iobj.root):]
                data_dir = data_dir[len(iobj.root):]

            script = convert_path("bin/gourmet")
            outfile = op.join(self.build_dir, op.basename(script))

            # abuse fileinput to replace two lines in bin/gourmet
            for line in fileinput.input(outfile, inplace=1):
                if "lib_dir = '.'" in line:
                    line = "lib_dir = '%s'\n" % lib_dir
                elif "data_dir = '.'" in line:
                    line = "data_dir = '%s'\n" % data_dir

                print(line),


if sys.platform == "win32":
    # GTK file inclusion
    from gi.repository import Gtk
    # The runtime dir is in the same directory as the module:
    GTK_RUNTIME_DIR = op.join(
        op.split(op.dirname(Gtk.__file__))[0], "runtime")

    assert op.exists(GTK_RUNTIME_DIR), "Cannot find GTK runtime data"

    GTK_THEME_DEFAULT = op.join("share", "themes", "Default")
    GTK_THEME_WINDOWS = op.join("share", "themes", "MS-Windows")
    GTK_GTKRC_DIR = op.join("etc", "gtk-2.0")
    GTK_GTKRC = "gtkrc"
    GTK_WIMP_DIR = op.join("lib", "gtk-2.0", "2.10.0", "engines")
    GTK_WIMP_DLL = "libwimp.dll"

    # Enable Tango icons:
    GTK_ICONS = op.join("share", "icons")

    # Localisation data path (which I omit, but you might not want to):
    # TODO: clarify what the above comment refers to
    GTK_LOCALE_DATA = op.join("share", "locale")


def data_files():
    """Build list of data files to be installed"""
    data_files = []

    for root, _, files in os.walk('data'):
        if files:
            files = [op.join(root, f) for f in files]
            data_files.append((op.join('share',
                                       'gourmet',
                                       root[len('data')+1:]),
                               files))

    # files in /usr/share/X/ (not gourmet)
    files = []
    base = op.join('share', 'gourmet')

    files.extend(data_files)
    files.extend([(op.join(base, 'ui'), glob.glob(op.join('ui', '*.ui')))])
    files.extend([(op.join('share', 'doc', 'gourmet'), ['FAQ', 'LICENSE'])])

    return files


if sys.platform == "win32":
    from cx_Freeze import setup, Executable, build as build_cxf
    import msilib

    class build(build_extra, build_cxf):
        def __init__(self, dist):
            build_extra.__init__(self, dist)
            build_cxf.__init__(self, dist)

        def get_sub_comands(self):
            build_cxf.sub_commands(self)

        def initialize_options(self):
            build_extra.initialize_options(self)
            build_cxf.initialize_options(self)

        def finalize_options(self):
            build_extra.finalize_options(self)
            build_cxf.finalize_options(self)

    include_files = []
    for i in data_files():
        for j in i[1]:
            include_files.append((j, i[0]))

    icon_table = [('GourmetIco', msilib.Binary('data/icons/gourmet.ico'))]

    property_table = [('ARPPRODUCTICON', 'GourmetIco'),]  # noqa: comma forces array

    msi_data = {'Icon': icon_table, 'Property': property_table}

    kwargs = dict(name="Gourmet Recipe Manager",
                  executables=[Executable(
                                op.join(srcpath, 'bin', 'gourmet'),
                                base="Win32GUI",
                                icon="data/icons/gourmet.ico",
                                shortcutName="Gourmet Recipe Manager",
                                shortcutDir="ProgramMenuFolder")
                               ],
                  options={
                           'build_exe': {
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
                                    ('LICENSE', op.join('doc', 'LICENSE')),
                                    ('FAQ', op.join('doc', 'FAQ')),
                                    (op.join(GTK_RUNTIME_DIR,
                                             GTK_THEME_DEFAULT),
                                     GTK_THEME_DEFAULT),
                                    (op.join(GTK_RUNTIME_DIR,
                                             GTK_THEME_WINDOWS),
                                     GTK_THEME_WINDOWS),
                                    # (op.join(GTK_RUNTIME_DIR, GTK_ICONS),
                                    #  GTK_ICONS),
                                    (op.join(GTK_RUNTIME_DIR, GTK_GTKRC_DIR,
                                             GTK_GTKRC),
                                     op.join(GTK_GTKRC_DIR, GTK_GTKRC)),
                                    (op.join(GTK_RUNTIME_DIR, GTK_WIMP_DIR,
                                             GTK_WIMP_DLL),
                                     op.join(GTK_WIMP_DIR, GTK_WIMP_DLL)),
                                    (op.join('build', 'mo'), 'locale'),
                                    (op.join("build", "share", "gourmet"),
                                     '.'),
                                    (op.join("gourmet", 'plugins'), 'plugins')
                                ],

                                # Exclude the plugins module from being added
                                # to library.zip and add it via include_files
                                # instead,  in order to faciliate the handling
                                # of *.gourmet-plugin and extra files (such as
                                # *.ui and image files).
                                'excludes': ['plugins', 'Tkinter', 'wx'],
                                'optimize': 2,
                                'compressed': 1,
                                'include_msvcr': True,
                                # see
                                # http://stackoverflow.com/questions/1979486/py2exe-win32api-pyc-importerror-dll-load-failed # noqa
                                # libgcc_s_dw2-1.dll would crash Gourmet
                                'bin_excludes': ["mswsock.dll",
                                                 "powrprof.dll",
                                                 "libgcc_s_dw2-1.dll"],
                            },
                           'bdist_msi': {
                            'upgrade_code':
                               '{D19B9EC6-DF39-4C83-BF87-A67776D087FA}',
                            'data':
                                msi_data
                            }
                           }
                  )
else:
    from distutils.core import setup
    build = build_extra
    kwargs = dict(
                  name=version.name,
                  data_files=data_files(),
                  scripts=[op.join('bin', 'gourmet')]
                  )

plugins = []


def crawl(base, basename):
    bdir = base
    subdirs = filter(lambda x: op.isdir(op.join(bdir, x)),
                     os.listdir(bdir))
    for subd in subdirs:
        name = basename + '.' + subd
        plugins.append(name)
        crawl(op.join(bdir, subd), name)


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
    package_data={'gourmet': ['plugins/*/*.ui',
                              'plugins/*/images/*.png',
                              'plugins/*/*/images/*.png']
                  },
    cmdclass={'build': build,
              'build_i18n': build_i18n,
              'build_icons': build_icons,
              'build_py': build_py,
              'build_scripts': build_scripts,
              },
    **kwargs
)
