import os
from pathlib import Path

from distutils.core import Command
from setuptools import find_packages
from setuptools import setup


package = 'gourmet'
podir = Path('po')
langs = sorted(f.name[:-3] for f in podir.glob('*.po'))


def modir(lang):
    mobase = Path("build")
    return mobase / "mo" / lang


def mkmo(lang):
    outpath = modir(lang)
    os.makedirs(outpath, exist_ok=True)

    inpath = podir / (lang + ".po")

    cmd = f"msgfmt {inpath} -o {outpath}/{package}.mo"
    os.system(cmd)


def merge_i18n():
    cmd = "LC_ALL=C intltool-merge -u -c ./po/.intltool-merge-cache ./po"

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
            print(f"Processing {infile} to {outfile}")
            os.system(f"{cmd} {flag} {infile} {outfile}")


def polist():
    dst_tmpl = "share/locale/%s/LC_MESSAGES/"
    polist = [(dst_tmpl % x, ["%s/%s.mo" % (modir(x), package)])
              for x in langs]

    return polist


class build_i18n(Command):
    description = "Create/update po/pot translation files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating POT file")
        cmd = f"cd po; intltool-update --pot --gettext-package={package}"
        os.system(cmd)

        for lang in langs:
            print(f"Updating {lang} PO file")
            cmd = ("cd po; intltool-update --dist"
                   f"--gettext-package={package} {lang} >/dev/null 2>&1")
            os.system(cmd)
            mkmo(lang)

        merge_i18n()


# TODO: Single-source this metadata with version.py?
# https://packaging.python.org/guides/single-sourcing-package-version/ provides
# some recommendations, however as noted under item 6, we do not want to import
# our own package from setup.py as it may cause installation to fail
setup(
    name='gourmet',
    version='0.17.5',
    description='Recipe Organizer and Shopping List Generator',
    author='Thomas Mills Hinkle',
    author_email='Thomas_Hinkle@alumni.brown.edu',
    url='http://thinkle.github.io/gourmet/',
    license='GPL',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        'argcomplete', # argument completion when parsing arguments
        'beautifulsoup4', # converting pango to html
        'pillow', # image processing
        'pygobject', # gobject bindings (for GTK, etc.)
        'requests', # retrieving remote images
        'sqlalchemy', # database driver
        'toml', # parsing preferences file(s)
    ],
    extras_require={
        'epub-export': ['ebooklib'],
        'mycookbook': ['lxml'],
        'pdf-export': ['reportlab'],
        'spellcheck': ['pyenchant', 'pygtkspellcheck'],
        'web-import': ['beautifulsoup4', 'keyring', 'scrape-schema-recipe', 'selenium'],
    },
    cmdclass={'build_i18n': build_i18n},
    entry_points={
        "console_scripts": [
            "gourmet = gourmet.GourmetRecipeManager:launch_app",
        ]}
)
