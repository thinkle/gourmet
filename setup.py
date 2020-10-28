import os
from pathlib import Path

from distutils.core import Command
import setuptools

from gourmet import version


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


def crawl_plugins(base, basename):
    plugins = []
    subdirs = filter(lambda x: os.path.isdir(os.path.join(base, x)),
                     os.listdir(base))
    for subd in subdirs:
        name = basename + '.' + subd
        plugins.append(name)
        plugins.extend(crawl_plugins(os.path.join(base, subd), name))
    return plugins


plugins = crawl_plugins(os.path.join('gourmet', 'plugins'), 'gourmet.plugins')

package_data = [
    'backends/default.db',
    'plugins/*.gourmet-plugin',
    'plugins/*/*.gourmet-plugin',
    'data/recipe.dtd',
    'data/WEIGHT.txt',
    'data/FOOD_DES.txt',
    'data/ABBREV.txt',
    'data/nutritional_data_sr_version',
    'data/images/no_star.png',
    'data/images/reccard_edit.png',
    'data/images/AddToShoppingList.png',
    'data/images/half_gold_star.png',
    'data/images/half_blue_star.png',
    'data/images/gold_star.png',
    'data/images/blue_star.png',
    'data/images/reccard.png',
    'data/sound/phone.wav',
    'data/sound/warning.wav',
    'data/sound/error.wav',
    'data/icons/gourmet.ico',
    'data/icons/scalable/apps/gourmet.svg',
    'data/icons/48x48/apps/gourmet.png',
    'data/style/epubdefault.css',
    'data/style/default.css',
    'plugins/*/*.ui',
    'plugins/*/images/*.png',
    'plugins/*/*/images/*.png',
    'ui/*.ui',
    'ui/catalog/*',
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
              'gourmet.defaults',
              'gourmet.gtk_extras',
              'gourmet.importers',
              'gourmet.exporters',
              'gourmet.plugins',
              ] + plugins,
    package_data={'gourmet': package_data},
    cmdclass={'build_i18n': build_i18n},
    entry_points={
        "console_scripts": [
            "gourmet = gourmet.GourmetRecipeManager:launch_app",
        ]}
)
