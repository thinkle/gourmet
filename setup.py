import os
import re
from distutils.core import Command
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.sdist import sdist
from wheel.bdist_wheel import bdist_wheel


PACKAGE = 'gourmet'
PACKAGEDIR = Path('src') / PACKAGE
DATADIR = Path('data')
PODIR = Path('po')
LANGS = sorted(f.stem for f in PODIR.glob('*.po'))
LOCALEDIR = PACKAGEDIR / 'data' / 'locale'


def get_info(prop: str) -> str:
    with open(PACKAGEDIR / 'version.py') as versfile:
        content = versfile.read()
    match = re.search(r'^{} = "(.+)"'.format(prop), content, re.M)
    if match is not None:
        return match.group(1)
    raise RuntimeError(f"Unable to find {prop} string")


def rmfile(filepath):
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass


class BuildI18n(Command):
    description = "Build localized message catalogs"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # compile message catalogs to binary format
        for lang in LANGS:
            pofile = PODIR / f'{lang}.po'

            mofile = LOCALEDIR / lang / 'LC_MESSAGES'
            mofile.mkdir(parents=True, exist_ok=True)
            mofile /= f'{PACKAGE}.mo'

            cmd = f'msgfmt {pofile} -o {mofile}'
            os.system(cmd)

        # merge translated strings into various file types
        cachefile = PODIR / '.intltool-merge-cache'
        cmd = f"LC_ALL=C intltool-merge -u -c {cachefile} {PODIR}"

        for infile in DATADIR.rglob('*.in'):
            # trim '.in' extension
            outfile = infile.with_suffix('')
            extension = outfile.suffix

            if 'desktop' in extension:
                flag = '-d'
            # TODO: is '.schema' used?
            elif 'schema' in extension:
                flag = '-s'
            elif 'xml' in extension:
                flag = '-x'
            elif 'gourmet-plugin' in extension:
                flag = '-k'
                outfile = PACKAGEDIR / outfile.relative_to(DATADIR)
            else:
                assert False, f'Unknown file type: {infile}'

            if flag:
                os.system(f"{cmd} {flag} {infile} {outfile}")

        rmfile(cachefile)
        rmfile(f'{cachefile}.lock')


class BuildWheel(bdist_wheel):

    def run(self):
        self.run_command('build_i18n')
        # refresh metadata, if necessary
        if self.distribution.have_run.get('egg_info', 0):
            self.distribution.reinitialize_command('egg_info')
            self.run_command('egg_info')
        super().run()


class Develop(develop):

    def run(self):
        self.run_command('build_i18n')
        super().run()


class SDist(sdist):

    def run(self):
        # Exclude built message catalogs and localized files
        # NOTE: We can't just include these in MANIFEST.in as this excludes
        # them from built distributions, which we don't want
        for lang in LANGS:
            mofile = LOCALEDIR / lang / 'LC_MESSAGES' / f'{PACKAGE}.mo'
            rmfile(mofile)

        for infile in DATADIR.rglob('*.in'):
            # trim '.in' extension
            outfile = infile.with_suffix('')
            extension = outfile.suffix
            if ('desktop' in extension
                    or 'xml' in extension
                    # TODO: is '.schema' used?
                    or 'schema' in extension):
                pass
            elif 'gourmet-plugin' in extension:
                outfile = PACKAGEDIR / outfile.relative_to(DATADIR)
            else:
                assert False, f'Unknown file type: {infile}'

            if outfile:
                rmfile(outfile)

        # refresh metadata, if necessary
        if self.distribution.have_run.get('egg_info', 0):
            self.distribution.reinitialize_command('egg_info')
            self.run_command('egg_info')
        super().run()


class UpdateI18n(Command):
    description = "Create/update po/pot translation files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce("Creating POT file")
        cmd = f"cd {PODIR}; intltool-update --pot --gettext-package={PACKAGE}"
        os.system(cmd)

        for lang in LANGS:
            self.announce(f"Updating {lang} PO file")
            cmd = (f"cd {PODIR}; intltool-update --dist"
                   f"--gettext-package={PACKAGE} {lang} >/dev/null 2>&1")
            os.system(cmd)


setup(
    name=PACKAGE,
    version=get_info('version'),
    description=get_info('description'),
    author=get_info('author'),
    author_email=get_info('author_email'),
    maintainer=get_info('maintainer'),
    maintainer_email=get_info('maintainer_email'),
    url=get_info('url'),
    license=get_info('license'),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        'argcomplete',  # argument completion when parsing arguments
        'beautifulsoup4',  # converting pango to html
        'pillow>=7.0.0',  # image processing
        'pygobject',  # gobject bindings (for GTK, etc.)
        'requests',  # retrieving remote images
        'sqlalchemy',  # database driver
        'toml',  # parsing preferences file(s)
    ],
    extras_require={
        'epub-export': ['ebooklib'],
        'mycookbook': ['lxml'],
        'pdf-export': ['reportlab'],
        'spellcheck': ['pyenchant', 'pygtkspellcheck'],
        'web-import': ['beautifulsoup4', 'keyring',
                       'scrape-schema-recipe', 'selenium'],
    },
    cmdclass={
        'bdist_wheel': BuildWheel,
        'build_i18n': BuildI18n,
        'develop': Develop,
        'sdist': SDist,
        'update_i18n': UpdateI18n,
    },
    entry_points={
        "console_scripts": [
            "gourmet = gourmet.GourmetRecipeManager:launch_app",
        ]}
)
