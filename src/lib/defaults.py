import locale
deflang = 'en'
locale.setlocale(locale.LC_ALL,'')
loc, enc = locale.getlocale()
lang = None
if loc:
    try:
        lang = __import__('defaults_%s'%loc,globals(),locals())
    except ImportError:
        try:
            lang = __import__('defaults_%s'%loc[0:2],globals(),locals())
        except ImportError:
            lang = __import__('defaults_%s'%deflang,globals(),locals())

if not lang: lang = __import__('defaults_%s'%deflang,globals(),locals())

# The next item is used to allow us to know some things about handling the language
try:
    langProperties=lang.LANG_PROPERTIES
except:
    lang.LANG_PROPERTIES=langProperties={'hasAccents':False, 'capitalisedNouns':False, 'useFractions':True} 
    # 'hasAccents' includes accents, umlauts etc, that might not be correctly handled
    # by eg lower()
    # 'capitalisedNouns' means that you don't want to use lower() anyway, cos it's
    #  ungramatical e.g. in the german Language, Nouns are written with Capital-Letters.

#from lang.__name__ import *

# NOW WE DO AUTOMATED STUFF
def add_itm (kd, k, v):
    if kd.has_key(k):
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

for amb,lst in lang.AMBIGUOUS.items():
    if lang.keydic.has_key(amb):
        lang.keydic[amb] += lst
    else:
        lang.keydic[amb] = lst

for row in lang.INGREDIENT_DATA:
    name,key,shop=row
    add_itm(lang.keydic,key,name)
    lang.shopdic[key]=shop

lang.unit_group_lookup = {}

for group,v in lang.UNIT_GROUPS.items():
    n = 0
    for u,rng in v:
        lang.unit_group_lookup[u] = group,n
        n += 1
