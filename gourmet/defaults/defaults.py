import locale, os, sys
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

# NOW WE DO AUTOMATED STUFF
def add_itm (kd, k, v):
    if k in kd:
        kd[k].append(v)
    else:
        kd[k]=[v]

## now we set up our dictionaries
lang.keydic = {}
lang.shopdic = {}
for lst in lang.SYNONYMS:
    k = lst[0]
    for i in lst:
        add_itm(lang.keydic,k,i)

for amb,lst in list(lang.AMBIGUOUS.items()):
    if amb in lang.keydic:
        lang.keydic[amb] += lst
    else:
        lang.keydic[amb] = lst

for row in lang.INGREDIENT_DATA:
    name,key,shop=row
    add_itm(lang.keydic,key,name)
    lang.shopdic[key]=shop

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


for group,v in list(lang.UNIT_GROUPS.items()):
    n = 0
    for u,rng in v:
        lang.unit_group_lookup[u] = group,n
        n += 1

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
