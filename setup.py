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


class build_i18n(distutils.cmd.Command):

    description = "integrate the gettext framework"

    user_options = [('desktop-files=', None, '.desktop.in files that '
                                             'should be merged'),
                    ('xml-files=', None, '.xml.in files that should be '
                                         'merged'),
                    ('schemas-files=', None, '.schemas.in files that '
                                             'should be merged'),
                    ('ba-files=', None, 'bonobo-activation files that '
                                        'should be merged'),
                    ('rfc822deb-files=', None, 'RFC822 files that should '
                                               'be merged'),
                    ('key-files=', None, '.key.in files that should be '
                                         'merged'),
                    ('domain=', 'd', 'gettext domain'),
                    ('merge-po', 'm', 'merge po files against template'),
                    ('po-dir=', 'p', 'directory that holds the i18n files'),
                    ('bug-contact=', None, 'contact address for msgid bugs')]

    boolean_options = ['merge-po']

    def initialize_options(self):
        self.desktop_files = []
        self.xml_files = []
        self.key_files = []
        self.schemas_files = []
        self.ba_files = []
        self.rfc822deb_files = []
        self.domain = None
        self.merge_po = False
        self.bug_contact = None
        self.po_dir = None

    def finalize_options(self):
        if self.domain is None:
            self.domain = self.distribution.metadata.name
        if self.po_dir is None:
            self.po_dir = "po"

    def run(self):
        """
        Update the language files, generate mo files and add them
        to the to be installed files
        """
        if not os.path.isdir(self.po_dir):
            return

        data_files = self.distribution.data_files
        if data_files is None:
            # in case not data_files are defined in setup.py
            self.distribution.data_files = data_files = []

        if self.bug_contact is not None:
            os.environ["XGETTEXT_ARGS"] = "--msgid-bugs-address=%s " % \
                                          self.bug_contact

        # Print a warning if there is a Makefile that would overwrite our
        # values
        if os.path.exists("%s/Makefile" % self.po_dir):
            self.announce("""
WARNING: Intltool will use the values specified from the
         existing po/Makefile in favor of the vaules
         from setup.cfg.
         Remove the Makefile to avoid problems.""")

        # If there is a po/LINGUAS file, or the LINGUAS environment variable
        # is set, only compile the languages listed there.
        selected_languages = None
        linguas_file = os.path.join(self.po_dir, "LINGUAS")
        if os.path.isfile(linguas_file):
            selected_languages = open(linguas_file).read().split()
        if "LINGUAS" in os.environ:
            selected_languages = os.environ["LINGUAS"].split()

        # Update po(t) files and print a report
        # We have to change the working dir to the po dir for intltool
        cmd = ["intltool-update", (self.merge_po and "-r" or "-p"), "-g", self.domain]
        wd = os.getcwd()
        os.chdir(self.po_dir)
        self.spawn(cmd)
        os.chdir(wd)
        max_po_mtime = 0
        for po_file in glob.glob("%s/*.po" % self.po_dir):
            lang = os.path.basename(po_file[:-3])
            if selected_languages and not lang in selected_languages:
                continue
            mo_dir =  os.path.join("build", "mo", lang, "LC_MESSAGES")
            mo_file = os.path.join(mo_dir, "%s.mo" % self.domain)
            if not os.path.exists(mo_dir):
                os.makedirs(mo_dir)
            cmd = ["msgfmt", po_file, "-o", mo_file]
            po_mtime = os.path.getmtime(po_file)
            mo_mtime = os.path.exists(mo_file) and os.path.getmtime(mo_file) or 0
            if po_mtime > max_po_mtime:
                max_po_mtime = po_mtime
            if po_mtime > mo_mtime:
                self.spawn(cmd)

            targetpath = os.path.join("share/locale", lang, "LC_MESSAGES")
            data_files.append((targetpath, (mo_file,)))

        # merge .in with translation
        for (option, switch) in ((self.xml_files, "-x"),
                                 (self.desktop_files, "-d"),
                                 (self.schemas_files, "-s"),
                                 (self.rfc822deb_files, "-r"),
                                 (self.ba_files, "-b"),
                                 (self.key_files, "-k"),):
            try:
                file_set = eval(option)
            except:
                continue
            for (target, files) in file_set:
                build_target = os.path.join("build", target)
                if not os.path.exists(build_target):
                    os.makedirs(build_target)
                files_merged = []
                for file in files:
                    if file.endswith(".in"):
                        file_merged = os.path.basename(file[:-3])
                    else:
                        file_merged = os.path.basename(file)
                    file_merged = os.path.join(build_target, file_merged)
                    cmd = ["intltool-merge", switch, self.po_dir, file,
                           file_merged]
                    mtime_merged = os.path.exists(file_merged) and \
                                   os.path.getmtime(file_merged) or 0
                    mtime_file = os.path.getmtime(file)
                    if mtime_merged < max_po_mtime or mtime_merged < mtime_file:
                        # Only build if output is older than input (.po,.in)
                        self.spawn(cmd)
                    files_merged.append(file_merged)
                data_files.append((target, files_merged))


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
