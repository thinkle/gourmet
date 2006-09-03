#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# we set up default information for our locale.
# Translators should use this file as the basis of their translation.
# Copy this file and rename it for you locale.
#
# For example, Spanish uses:
# defaults_es.py
#
# British English uses:
# defaults_en_GB.py
#
# Please fill in the below fields:

# Language: Swedish
# Translator: jens persson (jens@persson.cx)
# Last-updated: 2006-06-28

# TRANSLATOR WARNING: DO NOT TRANSLATE THE FIELD NAMES: ONLY THE VALUES!!!

# only translate the items in the list [..] (and feel free to create
# categories that make sense for your locale -- no need to translate
# these ones). DO NOT translate 'cuisine','rating','source' or
# 'category'

# The below are Gourmet's standard fields and the default categories for them.
# Do not translate the field names ('cuisine','rating','source,'category').
# Instead, fill in the list with categories that make sense for your locale.
# Feel free to change the number or content of categories to be consistent
# with what users in your locale are likely to be familiar with.

fields={'cuisine': ['Husmanskost','Italienskt','Thai',
                    'Indiskt','Spanskt','Asian/Vietnamese',
                    'Asian/Chinese','Asian/Japanese',],
        'rating' : ['Fantastiskt','Utmärkt','Bra','Hyfsat','Dåligt'],
        'source' : [],
        'category' : ['Efterrätt','Förrätt','Varmrätt',
                      'Sallad','Soppa','Bröd'],
                  }

# In English, there are a heck of a lot of synonyms. This is a list
# for those synonyms.  ["preferred word","alternate word","alternate word"]
# If there are none of these that you can think of in your language, just
# set this to:
# SYNONYMS=[]
SYNONYMS=[
    # the first item of each list is the default
    ["aubergin","äggplanta"],
    ["squash","zucchini"],
    ["stenbit","sjurygg"],
    ["morot","morötter"],
    ["soja","soya"],
    ["kvarg","kesella"],
    ["palsternacka","palsternackor"],
    ["gul lök","gula lökar","lök","lökar"],
    ["gurka","slanggurka"],
    ]

# A DICTIONARY CONTAINING INGREDIENT KEYS AND NDBNO for the USDA
# nutritional database. For these items, we will have nutritional
# information by default.

NUTRITIONAL_INFO = {}

# a dictionary for ambiguous words.
# key=ambiguous word, value=list of possible non-ambiguous terms
#
# Translators: if you have a word that has more than one food meaning
# in your language, you can add an entry as follow

# AMBIGUOUS = {
#              'word':['meaning1','meaning2','meaning3'],
#             }

AMBIGUOUS = {}


# triplicates ITEM, KEY, SHOPPING CATEGORY
# These will be defaults.

# They should include whatever foods might be standard for your
# locale, with whatever sensible default categories you can think of
# (again, thinking of your locale, not simply translating what I've
# done).

# Items provided here will automatically be recognized and go onto the
# given category in a user's shopping list by default.

# Don't feel obligated to translate every item -- especially since not
# all items will be common for all locales. However, the more items
# you can put here, the more the user will get the sense that gourmet
# "knows" about foods that they enter.

# I generated the below list using the wikipedia entry on foods as my
# starting point. You may want to do something similar for your
# locale.  Also, if the syntax of the below is too complicated, you
# can send me a list of category headings and ingredients for your
# locale and I'll do the necessary formatting <Thomas_Hinkle@alumni.brown.edu>

INGREDIENT_DATA = [["ananas","ananas","Frukt och grönt"],
	["anis","anis","Kryddor"],
	["ankbröst","ankbröst","Kött"],
	["apelsin","apelsin","Frukt och grönt"],
	["apelsinjuice","apelsinjuice","Mejeri"],
	["apelsinskal","apelsinskal","Frukt och grönt"],
	["aprikos","aprikos","Frukt och grönt"],
	["aromat","aromat","Kryddor"],
	["aromsalt","aromsalt","Kryddor"],
	["aubergine","aubergine","Frukt och grönt"],
	["avokado","avokado","Frukt och grönt"],
	["bacon","bacon","Kött"],
	["bakpulver","bakpulver","Torrvaror"],
	["banan","banan","Frukt och grönt"],
	["basilika","basilika","Kryddor"],
	["basilikaolja","basilikaolja","Kryddor"],
	["bearnaisesås","bearnaisesås","Djupfryst"],
	["biff","biff","Kött"],
	["bladpersilja","bladpersilja","Frukt och grönt"],
	["blandfärs","blandfärs","Kött"],
	["blomkål","blomkål","Frukt och grönt"],
	["bockhornsklöver","bockhornsklöver","Kryddor"],
	["broccoli","broccoli","Frukt och grönt"],
	["brysselkål","brysselkål","Frukt och grönt"],
	["buljongtärning","buljongtärning","Kryddor"],
	["capsaicin","capsaicin","Kryddor"],
	["carambola","carambola","Frukt och grönt"],
	["cayennepeppar","cayennepeppar","Kryddor"],
	["chilipeppar","chilipeppar","Kryddor"],
	["chilipulver","chilipulver","Kryddor"],
	["chilisås","chilisås","Torrvaror"],
	["citron","citron","Frukt och grönt"],
	["citrongräs","citrongräs","Kryddor"],
	["citronmeliss","citronmeliss","Kryddor"],
	["coctailbär","coctailbär","Torrvaror"],
	["cottage cheese","cottage cheese","Ost"],
	["crème fraiche","crème fraiche","Mejeri"],
	["curry","curry","Kryddor"],
	["dadelpalm","dadelpalm","Frukt och grönt"],
	["dansk körvel","dansk körvel","Kryddor"],
	["dessertost","dessertost","Ost"],
	["dill","dill","Frukt och grönt"],
	["dragon","dragon","Kryddor"],
	["endiv","endiv","Frukt och grönt"],
	["entrecôte","entrecôte","Kött"],
	["falukorv","falukorv","Kött"],
	["fikon","fikon","Frukt och grönt"],
	["filmjölk","filmjölk","Mejeri"],
	["fiskbuljong","fiskbuljong","Kryddor"],
	["flintastek","flintastek","Kött"],
	["florsocker","florsocker","Torrvaror"],
	["flytande margarin","flytande margarin","Mejeri"],
	["fläskfilé","fläskfilé","Kött"],
	["fläsk","fläsk","Kött"],
	["fläskfärs","fläskfärs","Kött"],
	["fransk senap","fransk senap","Torrvaror"],
	["fänkål","fänkål","Frukt och grönt"],
	["färskost","färskost","Ost"],
	["galiamelon","galiamelon","Frukt och grönt"],
	["garam masala","garam masala","Kryddor"],
	["grahamsmjöl","grahamsmjöl","Torrvaror"],
	["granatäpple","granatäpple","Frukt och grönt"],
	["griskött","griskött","Kött"],
	["grynpipig ost","grynpipig ost","Ost"],
	["grädde","grädde","Mejeri"],
	["gräddfil","gräddfil","Mejeri"],
	["gräslök","gräslök","Frukt och grönt"],
	["gröna oliver","gröna oliver","Torrvaror"],
	["grönkål","grönkål","Frukt och grönt"],
	["grönmynta","grönmynta","Kryddor"],
	["grönpeppar","grönpeppar","Kryddor"],
	["grön sparris","grön sparris","Frukt och grönt"],
	["gul lök","gul lök","Frukt och grönt"],
	["gurka","gurka","Frukt och grönt"],
	["gurkmeja","gurkmeja","Kryddor"],
	["gurkört","gurkört","Kryddor"],
	["herbes de provence","herbes de provence","Kryddor"],
	["hjorthornssalt","hjorthornssalt","Kryddor"],
	["honung","honung","Torrvaror"],
	["honungsmelon","honungsmelon","Frukt och grönt"],
	["honungssenap","honungssenap","Torrvaror"],
	["hp sauce","hp sauce","Kryddor"],
	["hårdost","hårdost","Ost"],
	["ingefära","ingefära","Frukt och grönt"],
	["ingefära","ingefära","Kryddor"],
	["isop","isop","Kryddor"],
	["johannesört","johannesört","Kryddor"],
	["jordnötter","jordnötter","Torrvaror"],
	["julskinka","julskinka","Kött"],
	["jäst","jäst","Torrvaror"],
	["kaffegrädde","kaffegrädde","Mejeri"],
	["kakao","kakao","Torrvaror"],
	["kalvkött","kalvkött","Kött"],
	["kamomill","kamomill","Kryddor"],
	["kanel","kanel","Kryddor"],
	["kapris","kapris","Kryddor"],
	["kardemumma","kardemumma","Kryddor"],
	["kassler","kassler","Kött"],
	["kesella gourmet","kesella gourmet","Mejeri"],
	["kikärter","kikärter","Torrvaror"],
	["kinakål","kinakål","Frukt och grönt"],
	["kinesisk gräslök","kinesisk gräslök","Kryddor"],
	["kinesisk soja","kinesisk soja","Kryddor"],
	["kiwi","kiwi","Frukt och grönt"],
	["kokosnöt","kokosnöt","Frukt och grönt"],
	["koriander","koriander","Kryddor"],
	["krasse","krasse","Frukt och grönt"],
	["kronärtskocka","kronärtskocka","Frukt och grönt"],
	["krossat vete","krossat vete","Torrvaror"],
	["krydda","krydda","Kryddor"],
	["kryddnejlika","kryddnejlika","Kryddor"],
	["kryddost","kryddost","Ost"],
	["kryddpeppar","kryddpeppar","Kryddor"],
	["kryddsalvia","kryddsalvia","Kryddor"],
	["kryddtimjan","kryddtimjan","Kryddor"],
	["kummin","kummin","Kryddor"],
	["kvanne","kvanne","Kryddor"],
	["kvitten","kvitten","Frukt och grönt"],
	["kycklingfilé","kycklingfilé","Kött"],
	["kyckling","kyckling","Kött"],
	["kål","kål","Frukt och grönt"],
	["körsbär","körsbär","Frukt och grönt"],
	["köttfärs","köttfärs","Kött"],
	["lagerblad","lagerblad","Kryddor"],
	["lammkött","lammkött","Kött"],
	["lantvetemjöl","lantvetemjöl","Torrvaror"],
	["lavendel","lavendel","Kryddor"],
	["lax","lax","Fisk"],
	["leverpastej","leverpastej","Pålägg"],
	["libbsticka","libbsticka","Kryddor"],
	["ljus sirap","ljus sirap","Torrvaror"],
	["lökar","lökar","Frukt och grönt"],
	["lök","lök","Frukt och grönt"],
	["löpe","löpe","Ost"],
	["lövbiff","lövbiff","Kött"],
	["maizena","maizena","Torrvaror"],
	["maizenamjöl","maizenamjöl","Torrvaror"],
	["maizenaredning","maizenaredning","Torrvaror"],
	["majonnäs","majonnäs","Torrvaror"],
	["majs","majs","Frukt och grönt"],
	["malört","malört","Kryddor"],
	["mandel","mandel","Torrvaror"],
	["mango","mango","Frukt och grönt"],
	["mangostan","mangostan","Frukt och grönt"],
	["margarin","margarin","Mejeri"],
	["matfett","matfett","Mejeri"],
	["medwurst","medwurst","Kött"],
	["mejram","mejram","Kryddor"],
	["melon","melon","Frukt och grönt"],
	["mjölk","mjölk","Mejeri"],
	["mjöl","mjöl","Torrvaror"],
	["morot","morot","Frukt och grönt"],
	["morötter","morötter","Frukt och grönt"],
	["muskot","muskot","Kryddor"],
	["musslor","musslor","Fisk"],
	["myrten","myrten","Kryddor"],
	["mörk sirap","mörk sirap","Torrvaror"],
	["nejlikor","nejlikor","Kryddor"],
	["nektarin","nektarin","Frukt och grönt"],
	["nötfärs","nötfärs","Kött"],
	["nötkött","nötkött","Kött"],
	["okra","okra","Frukt och grönt"],
	["olivolja","olivolja","Torrvaror"],
	["olja","olja","Torrvaror"],
	["oregano","oregano","Kryddor"],
	["ost","ost","Ost"],
	["ost","ost","Pålägg"],
	["oxfilé","oxfilé","Kött"],
	["palsternacka","palsternacka","Frukt och grönt"],
	["palsternackor","palsternackor","Frukt och grönt"],
	["papaya","papaya","Frukt och grönt"],
	["paprika","paprika","Frukt och grönt"],
	["paprikapulver","paprikapulver","Kryddor"],
	["paradiscorn","paradiscorn","Kryddor"],
	["parakasein","parakasein","Ost"],
	["parmesanost","parmesanost","Pålägg"],
	["passionsfrukt","passionsfrukt","Frukt och grönt"],
	["pata negra","pata negra","Kött"],
	["pepparmynta","pepparmynta","Kryddor"],
	["peppar","peppar","Kryddor"],
	["pepparrot","pepparrot","Kryddor"],
	["persika","persika","Frukt och grönt"],
	["persilja","persilja","Frukt och grönt"],
	["pimpinell","pimpinell","Kryddor"],
	["piplök","piplök","Kryddor"],
	["plommon","plommon","Frukt och grönt"],
	["pomerans","pomerans","Kryddor"],
	["potatismjöl","potatismjöl","Torrvaror"],
	["pumpa","pumpa","Frukt och grönt"],
	["purjolök","purjolök","Frukt och grönt"],
	["päron","päron","Frukt och grönt"],
	["rabarber","rabarber","Frukt och grönt"],
	["rambutan","rambutan","Frukt och grönt"],
	["renfana","renfana","Kryddor"],
	["renkött","renkött","Kött"],
	["renskav","renskav","Kött"],
	["ris","ris","Torrvaror"],
	["romansallad","romansallad","Frukt och grönt"],
	["rosenböna","rosenböna","Frukt och grönt"],
	["rosmarin","rosmarin","Kryddor"],
	["rostbiff","rostbiff","Kött"],
	["ruccola","ruccola","Frukt och grönt"],
	["rullad","rullad","Kött"],
	["rundpipig ost","rundpipig ost","Ost"],
	["russin","russin","Frukt och grönt"],
	["ryggbiff","ryggbiff","Kött"],
	["råbiff","råbiff","Kött"],
	["rågsikt","rågsikt","Torrvaror"],
	["rädisa","rädisa","Frukt och grönt"],
	["rädisor","rädisor","Frukt och grönt"],
	["räkor","räkor","Fisk"],
	["rättika","rättika","Frukt och grönt"],
	["röda vinbär","röda vinbär","Frukt och grönt"],
	["rödbeta","rödbeta","Frukt och grönt"],
	["röd caviar","röd caviar","Fisk"],
	["rött vin","rött vin","Vin och sprit"],
	["saffran","saffran","Kryddor"],
	["sallat","sallat","Frukt och grönt"],
	["salt","salt","Kryddor"],
	["salvior","salvior","Kryddor"],
	["schalottenlök","schalottenlök","Frukt och grönt"],
	["selleri","selleri","Frukt och grönt"],
	["senap","senap","Torrvaror"],
	["senapsfrö","senapsfrö","Kryddor"],
	["sesamolja","sesamolja","Torrvaror"],
	["sherry","sherry","Vin och sprit"],
	["sichuanpeppar","sichuanpeppar","Kryddor"],
	["sirap","sirap","Torrvaror"],
	["skinka","skinka","Kött"],
	["skånsk senap","skånsk senap","Kryddor"],
	["slanggurka","slanggurka","Frukt och grönt"],
	["smältost","smältost","Ost"],
	["smör","smör","Mejeri"],
	["snöripa","snöripa","Kött"],
	["socker","socker","Torrvaror"],
	["soja","soja","Kryddor"],
	["sommarkyndel","sommarkyndel","Kryddor"],
	["spansk körvel","spansk körvel","Kryddor"],
	["sparris","sparris","Frukt och grönt"],
	["spenat","spenat","Frukt och grönt"],
	["spiskummin","spiskummin","Kryddor"],
	["spättafilé","spättafilé","Fisk"],
	["squash","squash","Frukt och grönt"],
	["ströbröd","ströbröd","Torrvaror"],
	["stureost","stureost","Ost"],
	["svarta oliver","svarta oliver","Torrvaror"],
	["svartpeppar","svartpeppar","Kryddor"],
	["sylta","sylta","Kött"],
	["tabasco","tabasco","Kryddor"],
	["taggannona","taggannona","Frukt och grönt"],
	["timjan","timjan","Kryddor"],
	["tjälknöl","tjälknöl","Kött"],
	["tomatpuré","tomatpuré","Torrvaror"],
	["tomat","tomat","Frukt och grönt"],
	["tonfisk","tonfisk","Fisk"],
	["tryffelsvamp","tryffelsvamp","Kryddor"],
	["valnötskärnor","valnötskärnor","Torrvaror"],
	["vaniljkräm","vaniljkräm","Mejeri"],
	["vaniljsocker","vaniljsocker","Torrvaror"],
	["vattenmelon","vattenmelon","Frukt och grönt"],
	["vatten","vatten","Vatten"],
	["vetemjöl","vetemjöl","Torrvaror"],
	["viltkött","viltkött","Kött"],
	["vinbärsgele","vinbärsgele","Torrvaror"],
	["vinruta","vinruta","Kryddor"],
	["vinterkyndel","vinterkyndel","Kryddor"],
	["vispgrädde","vispgrädde","Mejeri"],
	["vitkål","vitkål","Frukt och grönt"],
	["vitlöksklyfta","vitlöksklyfta","Frukt och grönt"],
	["vitlökspulver","vitlökspulver","Kryddor"],
	["vitlök","vitlök","Frukt och grönt"],
	["vitpeppar","vitpeppar","Kryddor"],
	["vitt vin","vitt vin","Vin och sprit"],
	["vitvinsvinäger","vitvinsvinäger","Torrvaror"],
	["åbrodd","åbrodd","Kryddor"],
	["ägg","ägg","Mejeri"],
	["äpple","äpple","Frukt och grönt"],
	["ärtor","ärtor","Frukt och grönt"],
	["ättika","ättika","Torrvaror"],
	["ölost","ölost","Ost"],
	["örtsalt","örtsalt","kryddor"]
                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
# Each unit is of the following format:
# ("unit1","unit2"):conversion_factor, where unit1 contains conversion_factor X unit2
# For example: 1 cup has 16 tablespoons.
CONVERTER_TABLE = {
    ("tsk", "ml"):5,
    ("msk", "ml"):15,
    ("krm", "ml"):1,
    ("l", "ml"):1000,
    ("l", "cl"):100,
    ("l", "dl"):10,
    ("kg", "g"):1000,
    ("g", "mg"):1000}

# DENSITIES of common foods. This allows us to convert between mass and volume.
# Translators: You may be best off translating the food names below, since lists
# of food densities can be hard to come by!
DENSITY_TABLE={
    "vatten":1,
    "vindruvs juice":1.03,
    "grönsaksbuljong":1,
    "mjölk":1.029,
    "standardmjölk":1.029,
    "skummjölk":1.033,
    "kokosmjölk":0.875,
    "vispgrädde":0.994,
    "kaffegrädde":1.012,
    "honung":1.420,
    "socker":1.550,
    "salt":2.165,
    "smör":0.911,
    "olja":0.88,
    "olivolja":0.88,
    "majsolja":0.88,
    "sesamolja":0.88,
    "vetemjöl": 0.6,
    "mjöl": 0.6,
    "majsstärkelse": 0.6,
    "florsocker": 0.6
            }

# Standard unit names and alternate unit names that might appear.  For
# example: "c." is our standard abbreviation for cup.  "cup","c." or
# "cups" might appear in a recipe we are importing.  Each item of this
# list looks like this:
#
# ["standard", ["alternate1","alternate2","alternate3",...]]
#
# The first item should be the preferred abbreviation
# The second item should be the full name of the unit
# e.g. ["c.", ["cup",...]]
#
UNITS = [["tsk", ["tesked", "tsk", 'teskedar']],
         ["msk", ["matsked", "msk",'matskedar']],
         ["krm", ["kryddmått", "krm"]],
         ["ml", ["mililiter","ml", "ml."]],
         ["cl", ["centiliter","cl", "cl."]],
         ["dl", ["deciliter","dl", "dl."]],
         ["l", ["liter", "l.", "lit.",'l']],
         ["g", ["gram", "g.",'g']],
         ["mg", ["miligram", "mg.", "mg"]],
         ["kg", ["kilogram","kg.", "kg","kilo"]],
         # These names aren't really convertible, but we want them to
         # be recognized as units...
         ['liten',['liten','små']],
         ['normal',['normal','normalstor','normala','normalstora']],
         ['stor',['stor','stora']],
         ['klyfta',['klyfta','klyftor']],
         ['hel',['hel','hela']],
         ['paket',['paket']],
         ['låda',['låda','lådor']],
         ['burk',['burk','burkar']],
         ['skiva',['skiva','skivor']],
         ]

METRIC_RANGE = (1,999)

# The following sets up unit groups. Users will be able to turn
# these on or off (American users, for example, would likely turn
# off metric units, since we don't use them).
# (User choice not implemented yet)
UNIT_GROUPS = {
    'metric mass':[('mg',METRIC_RANGE),
                   ('g',METRIC_RANGE),
                   ('kg',(1,None))],
    'metric volume':[('ml',METRIC_RANGE),
                     ('cl',(1,99)),
                     ('dl',(1,9)),
                     ('l',(1,None)),],
    'imperial weight':[('grains',(0,27)),
                       ('dram',(0.5,15)),
                       ('oz.',(0.25,32)),
                       ('lb.',(0.25,None)),
                       ],
    'imperial volume':[('drop',(0,3)),
                       ('tsp.',(0.125,3)),
                       ('tbs.',(1,4)),
                       ('c.',(0.25,6)),
                       ('pt.',(1,1)),
                       ('qt.',(1,3)),
                       ('gallon',(1,None)),
                       ('peck',(1,2)),
                       ('bucket',(1,2)),
                       ('bushel',(1,None))]
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
    ("pt.", "lb."):['density',1],
    ("tbs.", "oz."):['density',0.5],
    ("c.", "oz."):['density',8],
    ("pt.", "oz."):['density',16],
    ("ml", "g"):['density',1],
    ('oz.','fl. oz.'):['density',1],
    }

# The units here need to correspond to the standard unit names defined
# in UNITS.  These are some core conversions from mass-to-volume,
# assuming a density of 1 (i.e. the density of water).
VOL_TO_MASS_TABLE = {
    ("ml", "g") : 1,
    ("ml", "mg") : 1000,
    ("ml", "kg"): 0.001,
    ("cl", "kg"): 0.01,
    ("cl", "g") : 10,
    ("dl", "kg") : 0.1,
    ("dl", "g") : 100,
    ("l", "kg") : 1}

# TIME ABBREVIATIONS (this is new!)
TIME_ABBREVIATIONS = {
    'sek':'sekunder',
    'min':'minuter',
    'tim':'timmar',
    's':'sekunder',
    'm':'minuter',
    't':'timmar',
    'h':'timmar'
    }

# These functions are rather important! Our goal is simply to
# facilitate look ups -- if the user types in "tomatoes", we want to
# find "tomato." Note that the strings these functions produce will
# _never_ be shown to the user, so it's fine to generate nonsense
# words as well as correct answers -- our goal is to generate a list
# of possible hits rather than to get the plural/singular form "right".

irregular_plurals={
    "geese":"goose",
    }
import re
two_digit_plural_matcher = re.compile('[szxo]es$')
one_digit_plural_matcher = re.compile("[^s]s$")
v_plural_matcher = re.compile('ves')

def guess_singulars (s):
    if len(s)<3: return []
    rets = []
    if irregular_plurals.has_key(s):
        rets.append(irregular_plurals[s])
    if two_digit_plural_matcher.search(s):
        wrd=s[0:-2]
        if not wrd in rets: rets.append(wrd)
    if v_plural_matcher.search(s):
        rets.append(s[0:-3]+'f')
    if one_digit_plural_matcher.search(s): rets.append(s[0:-1])
    return rets

def guess_plurals (s):
    if not s: return []
    ret = [s+'s',s+'es']
    if s[-1]=='f': ret.append(s[0:-1]+'ves')
    return ret
    
IGNORE = ["and","with","of","for","cold","warm","finely","thinly","roughly","coarsely"]

NUMBERS = {
    (1.0/8):['åttondel'],
    (1.0/4):['kvarts', 'en kvarts'],
    (3.0/4):['trekvarts'],
    (2.0/3):['två tredjedelar'],
    (1.0/3):['en tredjedel','en tredjedels'],
    (1.0/2):['en halv','halv'],
    1:['en','ett'],
    2:['två','ett par'],
    3:['tre'],
    4:['fyra'],
    5:['fem'],
    6:['sex'],
    7:['sju'],
    8:['åtta'],
    9:['nio'],
    10:['tio'],
    11:['elva'],
    12:['tolv','ett dussin'],
    20:['tjugo','ett tjog'],
    30:['trettio'],
    40:['förtio'],
    50:['femtio'],
    60:['sextio'],
    }
