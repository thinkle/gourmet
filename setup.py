import os
import re
import sys
from distutils.core import Command
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from wheel.bdist_wheel import bdist_wheel


PODIR = Path('po')
LANGS = sorted(f.name[:-3] for f in PODIR.glob('*.po'))


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
        package = get_info('name')
        for lang in LANGS:
            pofile = PODIR / f'{lang}.po'

            mofile = Path('build') / 'mo' / lang
            mofile.mkdir(parents=True, exist_ok=True)
            mofile /= f'{package}.mo'

            cmd = f'msgfmt {pofile} -o {mofile}'
            os.system(cmd)

        # merge translated strings into various file types
        cachefile = PODIR / '.intltool-merge-cache'
        cmd = f"LC_ALL=C intltool-merge -u -c {cachefile} {PODIR}"

        for infile in Path('.').rglob('*.in'):
            outfile = Path(str(infile)[:-3])
            extension = outfile.suffix

            if 'desktop' in extension:
                flag = '-d'
            elif 'schema' in extension:
                flag = '-s'
            elif 'xml' in extension:
                flag = '-x'
            elif 'gourmet-plugin' in extension:
                flag = '-k'
            else:
                flag = ''

            if flag:
                os.system(f"{cmd} {flag} {infile} {outfile}")

        rmfile(cachefile)
        rmfile(f'{cachefile}.lock')


class BuildWheel(bdist_wheel):

    def run(self):
        self.run_command('build_i18n')
        super().run()


class Develop(develop):

    def run(self):
        self.run_command('build_i18n')
        super().run()


class UpdateI18n(Command):
    description = "Create/update po/pot translation files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        package = get_info('name')

        self.announce("Creating POT file")
        cmd = f"cd {PODIR}; intltool-update --pot --gettext-package={package}"
        os.system(cmd)

        for lang in LANGS:
            self.announce(f"Updating {lang} PO file")
            cmd = (f"cd {PODIR}; intltool-update --dist"
                   f"--gettext-package={package} {lang} >/dev/null 2>&1")
            os.system(cmd)


def get_info(prop: str) -> str:
    setup_py = sys.argv[0]
    dirname = Path(setup_py).absolute().parent
    with open(dirname / 'src' / 'gourmet' / 'version.py') as versfile:
        content = versfile.read()
    match = re.search(r'^{} = "(.+)"'.format(prop), content, re.M)
    if match is not None:
        return match.group(1)
    raise RuntimeError(f"Unable to find {prop} string")


setup(
    name=get_info('name'),
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
        'update_i18n': UpdateI18n,
    },
    entry_points={
        "console_scripts": [
            "gourmet = gourmet.GourmetRecipeManager:launch_app",
        ]}
)
