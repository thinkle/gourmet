import locale
import os
import sys
from collections import defaultdict
from typing import Optional

from .abstractLang import AbstractLanguage

deflang = 'en'
lang: AbstractLanguage

if os.name == 'posix':
    try:
        locale.setlocale(locale.LC_ALL,'')
    except:
        loc,enc = locale.getdefaultlocale()
    else:
        loc, enc = locale.getlocale()

# Windows locales are named differently, e.g. German_Austria instead of de_AT
# Fortunately, we can find the POSIX-like type using a different method.
# sys.platform is the correct check per mypy convention (https://mypy.readthedocs.io/en/stable/common_issues.html?highlight=platform#python-version-and-system-platform-checks)
elif sys.platform == "win32":
    from ctypes import windll
    locid = windll.kernel32.GetUserDefaultLangID()
    loc = locale.windows_locale[locid]

importLang: Optional[AbstractLanguage] = None
if loc:
    try:
        importLang = __import__('defaults_%s'%loc,globals(),locals(), level=1).Language
    except ImportError:
        try:
            importLang = __import__('defaults_%s'%loc[0:2],globals(),locals(), level=1).Language
        except ImportError:
            importLang = __import__('defaults_%s'%deflang,globals(),locals(), level=1).Language

if not importLang:
    lang = __import__('defaults_%s'%deflang,globals(),locals()).Language
else:
    lang = importLang

# The next item is used to allow us to know some things about handling the language
try:
    langProperties=lang.LANG_PROPERTIES
except:
    lang.LANG_PROPERTIES=langProperties={'hasAccents':False, 'capitalisedNouns':False, 'useFractions':True}
    # 'hasAccents' includes accents, umlauts etc, that might not be correctly handled
    # by eg lower()
    # 'capitalisedNouns' means that you don't want to use lower() anyway, cos it's
    #  ungramatical e.g. in the german Language, Nouns are written with Capital-Letters.

## now we set up our dictionaries
lang.keydic = defaultdict(list)
for variants in lang.SYNONYMS:
    preferred = variants[0]
    lang.keydic[preferred].extend(variants)

for preferred, alternatives in lang.AMBIGUOUS.items():
    lang.keydic[preferred].extend(alternatives)

for itemname, key, _ in lang.INGREDIENT_DATA:
    lang.keydic[key].append(itemname)

lang.shopdic = {key: shoppingCategory for (_, key, shoppingCategory) in lang.INGREDIENT_DATA}

lang.unit_group_lookup = {}

unit_rounding_guide = {
    'ml':1,
    'l':0.001,
    'mg':1,
    'g':1,
    'tsp.':0.075,
    'Tbs.':0.02,
    'c.':0.125,
    }

if hasattr(lang,'unit_rounding_guide') and lang.unit_rounding_guide:
    unit_rounding_guide.update(lang.unit_rounding_guide)

lang.unit_rounding_guide = unit_rounding_guide


for groupname, magnitudes in lang.UNIT_GROUPS.items():
    for no, (unit, _) in enumerate(magnitudes):
        lang.unit_group_lookup[unit] = groupname, no

WORD_TO_SING_PLUR_PAIR = {}
if hasattr(lang,'PLURALS'):
    for forms in lang.PLURALS:
        for f in forms:
            WORD_TO_SING_PLUR_PAIR[f] = forms

def get_pluralized_form (word, n):
    from gettext import ngettext
    if not word:
        return ''
    lword=word.lower()
    if lword in WORD_TO_SING_PLUR_PAIR:
        forms = list(WORD_TO_SING_PLUR_PAIR[lword])
        forms += [n]
        return ngettext(*forms)
    elif lang.guess_singulars(lword):
        # Arbitrarily use the first item in the list returned by
        # lang.guess_singulars().
        forms = lang.guess_singulars(lword)[0:1]
        forms += [lword]
        forms += [n]
        return ngettext(*forms)
    else:
        return word
