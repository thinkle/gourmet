#!/usr/bin/python
# -*- coding: utf-8 -*-
#
## we set up default information.
## first, easy to maintain lists which can eventually be moved to
## files.

# TRANSLATOR WARNING: DO NOT TRANSLATE THE FIELD NAMES: ONLY THE VALUES!!!

CREDITS = "Leandro Guimarães Faria Corcete Dutra"

# only translate the items in the list [..] (and feel free to create categories
# that make sense for your locale -- no need to translate these ones). DO NOT
# translate 'cuisine','rating','source' or 'category'
fields={'cuisine': ['Estadunidense','Italiana','Mexicana',
                    'Sudoeste dos Estados Unidos','Tailandesa','Vietnamita',
                    'Chinesa','Japonesa','Mineira','Nordestina','Portuguesa','Brasileira'],
        'rating' : ['Excelente','Ótima','Boa','Razoável','Fraca'],
        'source' : [],
        'category' : ['Sobremesa','Entrada','Salada','Sopa',
                      'Café da manhã'],
                  }

# In English, there are a heck of a lot of synonyms. This is a list
# for those synonyms.  ["preferred word","alternate word","alternate word"]
# If there are none of these that you can think of in your language, just
# set this to:
# SYNONYMS=[]
SYNONYMS=[
    # the first item of each list is the default
    ]

# a dictionary key=ambiguous word, value=list of possible non-ambiguous terms
AMBIGUOUS = {}


# triplicates ITEM, KEY, SHOPPING CATEGORY
# These will be defaults. They should include whatever foods might be
# standard for your locale, with whatever sensible default categories
# you can think of (again, thinking of your locale, not simply translating
# what I've done).
INGREDIENT_DATA = [
                   # fruits, from wikipedia list
                   ## seafood, from wikipedia list
                   ## meats (garnered from wikipedia lists)
                   ## my old list
                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
CONVERTER_TABLE = {
    ("c.", "tbs."):16,
    ("lb.", "oz."):16,
    ("tbs.", "tsp."):3,
    ("pt.", "c."):2,
    ("qt.", "c."):4,
    ("gallon", "qt."):4,
    ("l.", "qt."):1.057,
    ("l.", "ml."):1000,
    ("l.", "cl."):100,
    ("l.", "dl."):10,
    ("oz.", "g."):28.35,
    ("kg.", "g."):1000,
    ("g.", "mg."):1000,
    ("tsp.", "drop"):76,
    ("oz.", "dram"):16,
    ("dram", "grains"):27.34375,
    ("peck", "gallon"):2,
    ("bucket", "peck"):2,
    ("bushel", "bucket"):2,
    ("lb.", "grains"):7000}

# DENSITIES of common foods. This allows us to convert between mass and volume.
DENSITY_TABLE={
    "água":1,
    "suco, uva":1.03,
    "caldo de vegetais":1,
    "caldo, vegetais":1,
    "caldo, galinha":1,
    "leite":1.029,
    "leite, integral":1.029,
    "leite, desnatado":1.033,
    "leite, 2%":1.031,
    "leite, 1%":1.03,
    "leite de coco":0.875,
    "mel":1.420,
    "açúcar, branco":1.550,
    "sal":2.165,
    "manteiga":0.911,
    "óleo, vegetal":0.88,
    "azeite":0.88,
    "óleo, milho":0.88,
    "óleo, gergelim":0.88,
    "farinha, branca": 0.6,
    "farinha, integral": 0.6,
    "açúcar, refinado": 0.6,
    "açúcar, cristal": 0.6
            }

# Stand unit names and alternate unit names that might appear.
# For example: "c." is our standard for cup. "cup","c." or "cups" might appear
# in a recipe we are importing.
# Each item of this list looks like this:
#
# ["standard", ["alternate1","alternate2","alternate3",...]]

UNITS = [["caixa" , ["cx", "cx."]],
         ["gota", ["gota"]],
         ["pitada", ["pitada"]],
         ["colher de café", ["Colher de café"]],
         ["colher de chá", ["Colher de chá"]],
         ["colher de sobremesa", ["Colher de sobremesa"]],
         ["colher de sopa", ["Colher de sopa"]],
         ["kg", ["quilograma"]],
         ["xícara de chá", ["Xícara de chá"]],
         ["xícara de café", ["Xícara de café"]],
         ["ml", ["mililitro"]],
         ["cl", ["centilitro"]],
         ["dl", ["decilitro"]],
         ["l", ["litro"]],
         ["g", ["grama"]],
         ["mg", ["miligrama"]],
         ["kg", ["quilograma"]]
         ]

# The following sets up unit groups. Users will be able to turn
# these on or off (American users, for example, would likely turn
# off metric units, since we don't use them).
METRIC_RANGE = (1,999)

UNIT_GROUPS = {
    'metric mass':[('mg',METRIC_RANGE),
                   ('g',METRIC_RANGE),
                   ('kg',(1,None))],
    'metric volume':[('ml',METRIC_RANGE),
                     ('cl',(1,99)),
                     ('dl',(1,9)),
                     ('l',(1,None)),],
    }

# The units here need to correspond to the standard unit names defined
# above in UNITS
CROSS_UNIT_TABLE = {
    ## This if for units that require an additional
    ## bit of information -- i.e. to convert between
    ## volume and mass you need the density of an
    ## item.  In these cases, the additional factor
    ## will be provided as an 'item' that is then looked
    ## up in the dictionary referenced here (i.e. the density_table)
    ## currently, 'density' is the only keyword used
    ("ml", "g"):['density',1]}

# The units here need to correspond to the standard unit names defined
# in UNITS
VOL_TO_MASS_TABLE = {
    ("ml", "g") : 1,
    ("ml", "mg") : 1000,
    ("ml", "kg"): 0.001,
    ("cl", "kg"): 0.01,
    ("cl", "g") : 10,
    ("dl", "kg") : 0.1,
    ("dl", "g") : 100,    
    ("l", "kg") : 1}
    


# These functions are rather important! Our goal is simply to
# facilitate look ups -- if the user types in "tomatoes", we want to
# find "tomato." Note that the strings these functions produce will
# _never_ be shown to the user, so it's fine to generate nonsense
# words as well as correct answers -- our goal is to generate a list
# of possible hits rather than to get the plural/singular form "right".

def guess_singulars (s):
    """I don't really know portuguese, but I'm going to guess it's
    like English and Spanish with regard to plurals and try some basic
    rules here.
    """
    if len(s)<3: return []
    ret = []
    if s[-1]=='s':
        ret.append(s[0:-1]) # try chopping off the s
        if s[-2]=='e':
            ret.append(s[0:-2]) # try chopping off 'es'
    return ret

def guess_plurals (s): return [s+'s',s+'es']

IGNORE=[]

NUMBERS = {
    }
