import glob
import os
import os.path as op
import sys

import distutils.command
import distutils.command.build
import distutils.command.build_py
import distutils.command.build_scripts
import distutils.core
import setuptools


from gourmet import version


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
            self.po_dir = os.path.join("gourmet", "po")

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


distutils.command.build.build.sub_commands.append(("build_i18n", None))


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


plugins = []


def crawl_plugins(base, basename):
    bdir = base
    subdirs = filter(lambda x: op.isdir(op.join(bdir, x)),
                     os.listdir(bdir))
    for subd in subdirs:
        name = basename + '.' + subd
        plugins.append(name)
        crawl_plugins(op.join(bdir, subd), name)


crawl_plugins(op.join('gourmet', 'plugins'), 'gourmet.plugins')


setuptools.setup(
    name=version.name,
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
                              'plugins/*/*/images/*.png',
                              'ui/*.ui',
                              'ui/catalog/*',
                              'data/recipe.dtd',
                              'data/WEIGHT.txt',
                              'data/FOOD_DES.txt',
                              'data/ABBREV.txt',
                              'data/nutritional_data_sr_version',
                              'data/images/no_star.png',
                              'data/images/splash.png',
                              'data/images/splash.svg',
                              'data/images/reccard_edit.png',
                              'data/images/AddToShoppingList.png',
                              'data/images/half_gold_star.png',
                              'data/images/gold_star.png',
                              'data/images/reccard.png',
                              'data/sound/phone.wav',
                              'data/sound/warning.wav',
                              'data/sound/error.wav',
                              'data/icons/gourmet.ico',
                              'data/icons/scalable/apps/gourmet.svg',
                              'data/icons/48x48/apps/gourmet.png',
                              'data/style/epubdefault.css',
                              'data/style/default.css',
                              ]
                  },
    include_package_data=True,
    cmdclass={'build': build_extra,
              'build_i18n': build_i18n,
              },
    entry_points={
        "console_scripts": [
            "gourmet = gourmet.GourmetRecipeManager:startGUI",
        ]}
)
