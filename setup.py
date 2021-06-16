import os
import re
from distutils.core import Command
from distutils.log import INFO
from pathlib import Path
from typing import Union

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


def refresh_metadata(cmd: Command) -> None:
    # distutils remembers what commands are run during a build so that
    # subsequent calls to the command are skipped. This means that metadata is
    # normally only created once even if multiple builds are being done (e.g.,
    # 'python setup.py sdist bdist_wheel'). Since package data is dynamically
    # built depending on the type of build, we need to ensure that any stale
    # metadata is refreshed.
    if cmd.distribution.have_run.get('egg_info', 0):
        cmd.distribution.reinitialize_command('egg_info')
        cmd.run_command('egg_info')


def rmfile(filepath: Union[Path, str]) -> None:
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass


class BuildI18n(Command):
    description = "Build localized message catalogs"
    user_options = []

    def initialize_options(self):
        # Command subclasses must implement this "abstract" method
        pass

    def finalize_options(self):
        # Command subclasses must implement this "abstract" method
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

            os.system(f"{cmd} {flag} {infile} {outfile}")

        rmfile(cachefile)
        rmfile(f'{cachefile}.lock')


class BuildSource(sdist):

    def run(self):
        # Exclude localization files that are created at build time
        # NOTE: We can't use MANIFEST.in for this because these files will then
        # also be excluded from built distributions
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
                # these files aren't moved after they're built
                pass
            elif 'gourmet-plugin' in extension:
                outfile = PACKAGEDIR / outfile.relative_to(DATADIR)
            else:
                assert False, f'Unknown file type: {infile}'

            rmfile(outfile)

        refresh_metadata(self)
        super().run()


class BuildWheel(bdist_wheel):

    def run(self):
        self.run_command('build_i18n')
        refresh_metadata(self)
        super().run()


class Develop(develop):

    def run(self):
        self.run_command('build_i18n')
        super().run()


class UpdateI18n(Command):
    description = "Create/update po/pot translation files"
    user_options = []

    def initialize_options(self):
        # Command subclasses must implement this "abstract" method
        pass

    def finalize_options(self):
        # Command subclasses must implement this "abstract" method
        pass

    def run(self):
        self.announce("Creating POT file", INFO)
        cmd = f"cd {PODIR}; intltool-update --pot --gettext-package={PACKAGE}"
        os.system(cmd)

        for lang in LANGS:
            self.announce(f"Updating {lang}.po", INFO)
            os.system(
                f"cd {PODIR};"
                f"intltool-update --dist --gettext-package={PACKAGE} {lang}")


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
        'beautifulsoup4==4.9.3',
        'lxml==4.6.3',
        'pillow>=7.0.0',
        'pygobject==3.40.1',
        'requests==2.25.1',
        'sqlalchemy==1.3.22',
        'toml==0.10.2',
    ],
    extras_require={
        'epub-export': ['ebooklib==0.17.1'],
        'pdf-export': ['reportlab==3.5.67'],
        'spellcheck': ['pyenchant',
                       'pygtkspellcheck'],
        'web-import': ['keyring==21.0.0',
                       'scrape-schema-recipe==0.1.3',
                       'selenium==3.141.0'],
    },
    cmdclass={
        'bdist_wheel': BuildWheel,
        'build_i18n': BuildI18n,
        'develop': Develop,
        'sdist': BuildSource,
        'update_i18n': UpdateI18n,
    },
    entry_points={
        "gui_scripts": [
            "gourmet = gourmet.GourmetRecipeManager:launch_app",
        ]}
)
