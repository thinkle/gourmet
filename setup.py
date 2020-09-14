import glob
import os
import os.path as op

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

        self.user_options.append(("i18n", None, "use the localisation"))

    def initialize_options(self):
        distutils.command.build.build.initialize_options(self)
        self.i18n = False

    def finalize_options(self):

        def has_i18n(command):
            return self.i18n == "True" or \
                   ("build_i18n" in self.distribution.cmdclass and not
                    self.i18n == "False")

        distutils.command.build.build.finalize_options(self)
        self.sub_commands.append(("build_i18n", has_i18n))


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
        self.domain = None
        self.merge_po = False
        self.bug_contact = None
        self.po_dir = None

    def finalize_options(self):
        if self.domain is None:
            self.domain = self.distribution.metadata.name
        if self.po_dir is None:
            self.po_dir = op.join("gourmet", "po")

    def run(self):
        """
        Update the language files, generate mo files and add them
        to the to be installed files
        """
        if not op.isdir(self.po_dir):
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
        if op.exists("%s/Makefile" % self.po_dir):
            self.announce("""
WARNING: Intltool will use the values specified from the
         existing po/Makefile in favor of the vaules
         from setup.cfg.
         Remove the Makefile to avoid problems.""")

        # If there is a po/LINGUAS file, or the LINGUAS environment variable
        # is set, only compile the languages listed there.
        selected_languages = []
        linguas_file = op.join(self.po_dir, "LINGUAS")
        if op.isfile(linguas_file):
            selected_languages = open(linguas_file).read().split()
        if "LINGUAS" in os.environ:
            selected_languages = os.environ["LINGUAS"].split()

        # Update po(t) files and print a report
        # We have to change the working dir to the po dir for intltool
        cmd = ["intltool-update",
               (self.merge_po and "-r" or "-p"),
               "-g",
               self.domain]
        wd = os.getcwd()
        os.chdir(self.po_dir)
        self.spawn(cmd)
        os.chdir(wd)
        max_po_mtime = 0
        for po_file in glob.glob("%s/*.po" % self.po_dir):
            lang = op.basename(po_file[:-3])
            if lang not in selected_languages:
                continue
            mo_dir = op.join("build", "mo", lang, "LC_MESSAGES")
            mo_file = op.join(mo_dir, "%s.mo" % self.domain)
            if not op.exists(mo_dir):
                os.makedirs(mo_dir)
            cmd = ["msgfmt", po_file, "-o", mo_file]
            po_mtime = op.getmtime(po_file)
            mo_mtime = op.getmtime(mo_file) if op.exists(mo_file) else 0
            if po_mtime > max_po_mtime:
                max_po_mtime = po_mtime
            if po_mtime > mo_mtime:
                self.spawn(cmd)

            targetpath = op.join("share/locale", lang, "LC_MESSAGES")
            data_files.append((targetpath, (mo_file,)))

        # merge .in with translation
        for (option, switch) in ((self.xml_files, "-x"),
                                 (self.desktop_files, "-d"),
                                 (self.schemas_files, "-s"),
                                 (self.ba_files, "-b"),
                                 (self.key_files, "-k"),):
            try:
                file_set = eval(option)
            except Exception:
                continue
            for (target, files) in file_set:
                build_target = op.join("build", target)
                if not op.exists(build_target):
                    os.makedirs(build_target)
                files_merged = []
                for file in files:
                    if file.endswith(".in"):
                        file_merged = op.basename(file[:-3])
                    else:
                        file_merged = op.basename(file)
                    file_merged = op.join(build_target, file_merged)
                    cmd = ["intltool-merge", switch, self.po_dir, file,
                           file_merged]
                    mtime_merged = op.exists(file_merged) and \
                        op.getmtime(file_merged) or 0
                    mtime_file = op.getmtime(file)
                    if (mtime_merged < max_po_mtime or
                            mtime_merged < mtime_file):
                        # Only build if output is older than input (.po,.in)
                        self.spawn(cmd)
                    files_merged.append(file_merged)
                data_files.append((target, files_merged))


distutils.command.build.build.sub_commands.append(("build_i18n", None))


def crawl_plugins(base, basename):
    plugins = []
    subdirs = filter(lambda x: op.isdir(op.join(base, x)),
                     os.listdir(base))
    for subd in subdirs:
        name = basename + '.' + subd
        plugins.append(name)
        plugins.extend(crawl_plugins(op.join(base, subd), name))
    return plugins


plugins = crawl_plugins(op.join('gourmet', 'plugins'), 'gourmet.plugins')

package_data = [
    'plugins/*/*.ui',
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
    '../LICENSE',
    '../FAQ',
]


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
    package_data={'gourmet': package_data},
    cmdclass={'build': build_extra,
              'build_i18n': build_i18n,
              },
    entry_points={
        "console_scripts": [
            "gourmet = gourmet.GourmetRecipeManager:startGUI",
        ]}
)
