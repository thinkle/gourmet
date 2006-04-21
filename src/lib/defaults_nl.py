#!/usr/bin/python
# -*- coding: utf-8 -*-
#
## we set up default information.
## first, easy to maintain lists which can eventually be moved to
## files.

# TRANSLATOR WARNING: DO NOT TRANSLATE THE FIELD NAMES: ONLY THE VALUES!!!
CREDITS = "Gregory"

# only translate the items in the list [..] (and feel free to create categories
# that make sense for your locale -- no need to translate these ones). DO NOT
# translate 'cuisine','rating','source' or 'category'
fields={'cuisine': ['Amerikaans','Italiaans','Mexicaans',
                    'Zuid-westers','Aziatisch/Thais','Aziatisch/Vietnamees',
                    'Aziatisch/Chinees','Aziatisch/Japans',],
        'rating' : ['Excellent','Zeer goed','Goed','Matig','Zwak'],
        'source' : ['Kookboek'],
        'category' : ['Dessert','Voorgerecht','Salade','Soep',
                      'Ontbijt'],
                  }

# In English, there are a heck of a lot of synonyms. This is a list
# for those synonyms.  ["preferred word","alternate word","alternate word"]
# If there are none of these that you can think of in your language, just
# set this to:
# SYNONYMS=[]
SYNONYMS=[]

# a dictionary key=ambiguous word, value=list of possible non-ambiguous terms
AMBIGUOUS = {}


# triplicates ITEM, KEY, SHOPPING CATEGORY
# These will be defaults. They should include whatever foods might be
# standard for your locale, with whatever sensible default categories
# you can think of (again, thinking of your locale, not simply translating
# what I've done).
INGREDIENT_DATA = [["alfalfa spruiten","alfalfa spruiten","land- en tuinbouw producten"],
                   ["anijs","anijs","land- en tuinbouw producten"],
                   ["artisjok","artisjok","land- en tuinbouw producten"],
                   ["arugula","arugula","land- en tuinbouw producten"],
                   ["asperge","asperge","land- en tuinbouw producten"],
                   ["aubergine","aubergine","land- en tuinbouw producten"],
                   ["avocado","avocado","land- en tuinbouw producten"],
                   ["groene bonen","groene bonen","land- en tuinbouw producten"],
                   ["azukibonen","azukibonen","land- en tuinbouw producten"],
                   ["boonspruiten","boonspruiten","land- en tuinbouw producten"],
                   ["zwarte bonen","zwarte bonen","land- en tuinbouw producten"],
                   ["black-eyed peas","black-eyed peas","land- en tuinbouw producten"],
                   ["borlotti bonen","borlotti bonen","land- en tuinbouw producten"],
                   ["broad bonen","broad bonen","land- en tuinbouw producten"],
                   ["kikkererwten, garbanzos","kikkererwten, garbanzos","land- en tuinbouw producten"],
                   ["nierbonen","nierbonen","land- en tuinbouw producten"],
                   ["linzen","linzen","land- en tuinbouw producten"],
                   ["limabonen of boterbonen","limabonen of boterbonen","land- en tuinbouw producten"],
                   ["mung bonen","mung bonen","land- en tuinbouw producten"],
                   ["navy bonen","navy bonen","land- en tuinbouw producten"],
                   ["pronkbonen of Spaase bonen","pronkbonen of Spaanse bonen","land- en tuinbouw producten"],
                   ["sojabonen","sojabonen","land- en tuinbouw producten"],
                   ["erwten","erwten","land- en tuinbouw producten"],
                   ["snap peas","snap peas","land- en tuinbouw producten"],
                   ["bok choy","bok choy","land- en tuinbouw producten"],
                   ["broodfruit","broodfruit","land- en tuinbouw producten"],
                   ["groene bloemkool","groene bloemkool","land- en tuinbouw producten"],
                   ["broccoli","broccoli","land- en tuinbouw producten"],
                   ["spruitjes","spruitjes","land- en tuinbouw producten"],
                   ["kool","kool","land- en tuinbouw producten"],
                   ["bloemkool","bloemkool","land- en tuinbouw producten"],
                   ["selder","selder","land- en tuinbouw producten"],
                   ["maïssalade","maïssalade","land- en tuinbouw producten"],
                   ["witloof","witloof","land- en tuinbouw producten"],
                   ["kropsla","kropsla","land- en tuinbouw producten"],
                   ["maïs","maïs","land- en tuinbouw producten"],
                   ["champignons","champignons","land- en tuinbouw producten"],
                   ["netels","netels","land- en tuinbouw producten"],
                   ["bieslook","bieslook","land- en tuinbouw producten"],
                   ["look","look","land- en tuinbouw producten"],
                   ["prei","prei","land- en tuinbouw producten"],
                   ["ajuin","ajuin","land- en tuinbouw producten"],
                   ["sjalot","sjalot","land- en tuinbouw producten"],
                   ["peterselie","peterselie","land- en tuinbouw producten"],
                   ["peper","peper","land- en tuinbouw producten"],
                   ["zwarte peper","zwarte peper","land- en tuinbouw producten"],
                   ["witte peper","witte peper","land- en tuinbouw producten"],
                   ["chili peper","chili peper","land- en tuinbouw producten"],
                   ["jalapeño peper","peper, jalapeño","land- en tuinbouw producten"],
                   ["habanero peper","peper, habanero","land- en tuinbouw producten"],
                   ["rabarber","rabarber","land- en tuinbouw producten"],
                   ["biet","biet","land- en tuinbouw producten"],
                   ["wortel","wortel","land- en tuinbouw producten"],
                   ["maniok","maniok","land- en tuinbouw producten"],
                   ["ginger","ginger","land- en tuinbouw producten"],
                   ["radijs","radijs","land- en tuinbouw producten"],
                   ["wasabi","wasabi","land- en tuinbouw producten"],
                   ["witte radijs","witte radijs","land- en tuinbouw producten"],
                   ["spinazie","spinazie","land- en tuinbouw producten"],
                   ["komkommer","komkommer","land- en tuinbouw producten"],
                   ["pompoen","pompoen","land- en tuinbouw producten"],
                   ["spaghetti squash","squash, spaghetti","land- en tuinbouw producten"],
                   ["tomaat","tomaat","land- en tuinbouw producten"],
                   ["aardappel","aardappel","land- en tuinbouw producten"],
                   ["zoete aardappel","zoete aardappel","land- en tuinbouw producten"],
                   ["waterkers","waterkers","land- en tuinbouw producten"],
                   ["appel","appel","land- en tuinbouw producten"],
                   ["juneberry","juneberry","land- en tuinbouw producten"],
                   ["granaatappel","granaatappel","land- en tuinbouw producten"],
                   ["abricot","abricot","land- en tuinbouw producten"],
                   ["kers","kers","land- en tuinbouw producten"],
                   ["perzik","perzik","land- en tuinbouw producten"],
                   ["nectarine","nectarine","land- en tuinbouw producten"],
                   ["braambes","braambes","land- en tuinbouw producten"],
                   ["framboos","framboos","land- en tuinbouw producten"],
                   ["bergbraambes","bergbraambes","land- en tuinbouw producten"],
                   ["beredruif","beredruif","land- en tuinbouw producten"],
                   ["bosbes","bosbes","land- en tuinbouw producten"],
                   ["Amerikaanse veenbes","Amerikaanse veenbes","land- en tuinbouw producten"],
                   ["lingonberry","lingonberry","land- en tuinbouw producten"],
                   ["berberis","berberis","land- en tuinbouw producten"],
                   ["rode bes","bes, rood","land- en tuinbouw producten"],
                   ["zwarte bes","bes, zwart","land- en tuinbouw producten"],
                   ["witte bes","bes, wit","land- en tuinbouw producten"],
                   ["vlierbes","vlierbes","land- en tuinbouw producten"],
                   ["kruisbes","kruisbes","land- en tuinbouw producten"],
                   ["overzees-wegedoorn","overzees-wegedoorn","land- en tuinbouw producten"],
                   ["moerbeiboom","moerbeiboom","land- en tuinbouw producten"],
                   ["kiwi","kiwi","land- en tuinbouw producten"],
                   ["papaja","papaja","land- en tuinbouw producten"],
                   ["peer","peer","land- en tuinbouw producten"],
                   ["kantaloep","kantaloep","land- en tuinbouw producten"],
                   ["watermeloen","watermeloen","land- en tuinbouw producten"],
                   ["aardbei","aardbei","land- en tuinbouw producten"],
                   ["vijg","vijg","land- en tuinbouw producten"],
                   ["druif","druif","land- en tuinbouw producten"],
                   ["pompelmoes","pompelmoes","land- en tuinbouw producten"],
                   ["citroen","citroen","land- en tuinbouw producten"],
                   ["limoen","limoen","land- en tuinbouw producten"],
                   ["mandarijn","mandarijn","land- en tuinbouw producten"],
                   ["clementine","clementine","land- en tuinbouw producten"],
                   ["sinaasappel","sinaasappel","land- en tuinbouw producten"],
                   ["lychee","lychee","land- en tuinbouw producten"],
                   ["passievrucht","passievrucht","land- en tuinbouw producten"],
                   ["banaan","banaan","land- en tuinbouw producten"],
                   ["ster fruit","ster fruit","land- en tuinbouw producten"],
                   ["kokosnoot","kokosnoot","land- en tuinbouw producten"],
                   ["durian","durian","land- en tuinbouw producten"],
                   ["mango","mango","land- en tuinbouw producten"],
                   ["ananas","ananas","land- en tuinbouw producten"],

                   ["ansjovis","ansjovis","vis & zeevruchten"],
                   ["baars","baars","vis & zeevruchten"],
                   ["blowfish","blowfish","vis & zeevruchten"],
                   ["meerval","meerval","vis & zeevruchten"],
                   ["kabeljouw","kabeljouw","vis & zeevruchten"],
                   ["paling","paling","vis & zeevruchten"],
                   ["bot","bot","vis & zeevruchten"],
                   ["schelvis","schelvis","vis & zeevruchten"],
                   ["heilbot","heilbot","vis & zeevruchten"],
                   ["zeebaars","zeebaars","vis & zeevruchten"],
                   ["snoek","snoek","vis & zeevruchten"],
                   ["sardien","sardien","vis & zeevruchten"],
                   ["zalm","zalm","vis & zeevruchten"],
                   ["zeebaars","zeebaars","vis & zeevruchten"],
                   ["haai","haai","vis & zeevruchten"],
                   ["snapper","snapper","vis & zeevruchten"],
                   ["schorpioenvis","schorpioenvis","vis & zeevruchten"],
                   ["tong","tong","vis & zeevruchten"],
                   ["steur","steur","vis & zeevruchten"],
                   ["zwaardvis","zwaardvis","vis & zeevruchten"],
                   ["tegelvis","tegelvis","vis & zeevruchten"],
                   ["forel","forel","vis & zeevruchten"],
                   ["tonijn","tonijn","vis & zeevruchten"],
                   ["witing","witing","vis & zeevruchten"],
                   ["kuiten","kuiten","vis & zeevruchten"],
                   ["kaviaar","kaviaar","vis & zeevruchten"],
                   ["zalmkuiten","zalmkuiten","vis & zeevruchten"],
                   ["krab","krab","vis & zeevruchten"],
                   ["rivierkreeften","rivierkreeften","vis & zeevruchten"],
                   ["kreeft","kreeft","vis & zeevruchten"],
                   ["garnaal","garnaal","vis & zeevruchten"],
                   ["scampi","scampi","vis & zeevruchten"],
                   ["tweekleppig schelpdier","tweekleppig schelpdier","vis & zeevruchten"],
                   ["mossel","mossel","vis & zeevruchten"],
                   ["octopus","octopus","vis & zeevruchten"],
                   ["oester","oester","vis & zeevruchten"],
                   ["slak","slak","vis & zeevruchten"],
                   ["inktvis","inktvis","vis & zeevruchten"],
                   ["kammossel","kammossel","vis & zeevruchten"],

                   ["spek","spek","vlees"],
                   ["chorizo","chorizo","vlees"],
                   ["fuet","fuet","vlees"],
                   ["salami","salami","vlees"],
                   ["ham","ham","vlees"],
                   ["mutton","mutton","vlees"],
                   ["lam","lam","vlees"],
                   ["kalf","kalf","vlees"],
                   ["steak","steak","vlees"],
                   ["hamburger","hamburger","vlees"],
                   ["roast beef","roast beef","vlees"],
                   ["konijn","konijn","vlees"],
                   ["struisvogel","struisvogel","vlees"],
                   ["muskusrat","muskusrat","vlees"],
                   ["waterkonijn","waterkonijn","vlees"],
                   ["kip","kip","vlees"],
                   ["kalkoen","kalkoen","vlees"],
                   ["eend","eend","vlees"],
                   ["gans","gans","vlees"],

                   ## my old list
                   ['plantaardige bouillon','bouillon, plantaardig','soepen & sausen'],
                   ['basilicum','basilicum','land- en tuinbouw producten',],
                   ['lichtbruine suiker','suiker, lichtbruin','bakken',],
                   ['azijn','azijn','wijnen & oliën',],
                   ['okkernoot','okkernoot','bakken',],
                   ['korianderzaadjes','korianderzaadjes','kruiden',],
                   ['couscous','couscous','pasta\'s',],
                   ['rijst','rijst','pasta\'s',],
                   ['olijfolie','olie, olijf','wijnen & oliën',],
                   ['vanille extract','vanille extract','bakken',],
                   ['rode aardappel','aardappel, rood','land- en tuinbouw producten',],
                   ['currypoeder','currypoeder','kruiden',],
                   ['gedroogde garnaal','garnaal, gedroogd','internationaal',],
                   ['dijon mosterd','mosterd, dijon','condiments',],
                   ['maïsolie','olie, maïs','wijnen & oliën',],
                   ['feta kaas','kaas, feta','zuivelproducten',],
                   ['kerstomaat','tomaat, kers','land- en tuinbouw producten',],
                   ['spaghetti','spaghetti','pasta\'s',],
                   ['witte ajuin','ajuin, wit','land- en tuinbouw producten',],
                   ['yoghurt','yoghurt','zuivelproducten',],
                   ['croutons','croutons','brood',],
                   ['chili poeder','chili poeder','kruiden',],
                   ['krulsla','sla, gekruld','land- en tuinbouw producten',],
                   ['rijstazijn','azijn, rijst','internationaal',],
                   ['pasta','pasta','pasta\'s',],
                   ['zure room','zure room','zuivelproducten',],
                   ['sinaasappelsap','sinaasappelsap','land- en tuinbouw producten',],
                   ['spinazie','spinazie','land- en tuinbouw producten',],
                   ['plantaardige olie','olie, plantaardig','wijnen & oliën',],
                   ['pindakaas','pindakaas','brood',],
                   ['ei','ei','zuivelproducten',],
                   ['limoen','limoen','land- en tuinbouw producten',],
                   ['olijven','olijven','land- en tuinbouw producten',],
                   ['boter','boter','zuivelproducten',],
                   ['cheddar kaas','kaas, cheddar','zuivelproducten',],
                   ['mozzarella kaas','kaas, mozzarella','zuivelproducten',],
                   ['witte suiker','suiker, wit','bakken',],
                   ['fresh kaas white goat','kaas, fresh white goat','zuivelproducten',],
                   ['geel maïsmeel','maïsmeel, geel','bakken',],
                   ['paprika','paprika','kruiden',],
                   ['ster anijs','ster anijs','kruiden',],
                   ['bruine suiker','suiker, bruin','bakken',],
                   ['honing','honing','bakken',],
                   ['citroensap','citroensap','land- en tuinbouw producten',],
                   ['rode ajuin','ajuin, rood','land- en tuinbouw producten',],
                   ['melk','melk','zuivelproducten',],
                   ['bakpoeder','bakpoeder','bakken',],
                   ['tomatensap','tomatensap','soepen & sausen',],
                   ['mosterdzaadjes','zaadjes, mosterd','kruiden',],
                   ['parmesan kaas','kaas, parmesan','pasta\'s',],
                   ['mayonnaise','mayonnaise','brood',],
                   ['gerookte Gouda kaas','kaas, gerookte Gouda','zuivelproducten',],
                   ['kokosmelk','kokosmelk','internationaal',],
                   ['bloem','bloem','bakken',],
                   ['salsa','salsa','internationaal',],
                   ['broccoli','broccoli','land- en tuinbouw producten',],
                   ['witte wijn','wijn, wit','wijnen & oliën',],
                   ['rode wijn','wijn, rood','wijnen & oliën',],
                   ['bruin bier','bier, bruin','wijnen & oliën',],
                   ['blond bier','bier, blond','wijnen & oliën',],
                   ['witbier','bier, wit','wijnen & oliën',],
                   ['zwarte gemalen peper','zwarte peper, gemalen','kruiden',],
                   ['witte gemalen peper','witte peper, gemalen','kruiden',],
                   ['sojasaus','sojasaus','internationaal',],
                   ['sesamzaadjes','sesamzaadjes','internationaal',],
                   ['zout','zout','bakken',],
                   ['kurkuma','kurkuma','kruiden',],
                   ['kipfilet' ,'kip, filet' , 'vlees',],
                   ['hele kip' ,'kip, heel' , 'vlees',],
                   ['kippenboutje' ,'kip, bouten' , 'vlees',],
                   ['rundsvlees' ,'rundsvlees' , 'vlees',],
                   ['gehakt' ,'gehakt' , 'vlees',],
                   ['varkensvlees' ,'varkensvlees' , 'vlees',],
                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
CONVERTER_TABLE = {
    ("l", "ml"):1000,
    ("l", "cl"):100,
    ("l", "dl"):10,
    ("kg", "g"):1000,
    ("g", "mg"):1000
    }

# DENSITIES of common foods. This allows us to convert between mass and volume.
DENSITY_TABLE={
    "water":1,
    "sap, druif":1.03,
    "plantaardige bouillon":1,
    "bouillon, plantaardig":1,
    "bouillon, kip":1,
    "melk":1.029,
    "melk, vol":1.029,
    "melk, mager":1.033,
    "melk, 2%":1.031,
    "melk, 1%":1.03,
    "kokosmelk":0.875,
    "karnemelk":1.03,
    "zware room":0.994,
    "lichte room":1.012,
    "half en half":1.025,
    "honing":1.420,
    "suiker, wit":1.550,
    "zout":2.165,
    "boter":0.911,
    "olie, plantaardig":0.88,
    "olie, olijf":0.88,
    "olie, maïs":0.88,
    "olie, sesam":0.88,
    "bloem, alle doeleinden": 0.6,
    "bloem, whole wheat": 0.6,
    "maïszetmeel": 0.6,
    "suiker, bloem": 0.6,
    "suiker, zoetigheden": 0.6
    }

# Stand unit names and alternate unit names that might appear.
# For example: "c." is our standard for cup. "cup","c." or "cups" might appear
# in a recipe we are importing.
# Each item of this list looks like this:
#
# ["standard", ["alternate1","alternate2","alternate3",...]]

UNITS = [["bucket" , ["bucket","buckets","bckt."]],
         ["grains", ["grain","grains"]],
         ["dram", ["dram","drams"]],
         ["drop",["drop"]],
         ["bos", ["bossen","bosje"]],
         ["theelp.", ["theelepel","theelepels","theelepeltje","theelepeltjes","theelpl.","theelpl"]],
         ["eetlp.", ["eetlepel","eetlepels","eetlpl.","eetlpl"]],
         ["lb.", [ "pond","lb","lb.","lbs.","ponden"]],
         ["k.", ["kop","kopje","kp.","koppen"]],
         ["qt.", ["quart","qt.","quarts"]],
         ["pt.", ["pint","pt.","pints"]],
         ["ml", ["mililiter","ml.","mlit.","mililiters"]],
         ["cl", ["centiliter","cl.","clit.","centiliters"]],
         ["dl", ["deciliter","dl.","dlit.","deciliters"]],
         ["l", ["liter","l.","lit.","liters"]],
         ["g", ["gram","g.","gr","gr.","grammen"]],
         ["mg", ["miligram","mg.","mg","miligrammen"]],
         ["kg", ["kilogram","kg.","kg","kilogrammen"]]
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
    'imperial weight':[('grains',(0,27)),
                       ('dram',(0.5,15)),
                       ('oz.',(0.25,32)),
                       ('lb.',(0.25,None)),
                       ],
    'imperial volume':[('drop',(0,3)),
                       ('tsp.',(0.125,3)),
                       ('tbs.',(1,4)),
                       ('k.',(0.25,6)),
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
    ("k.", "oz."):['density',8],
    ("pt.", "oz."):['density',16],
    ("ml", "g"):['density',1]}

# The units here need to correspond to the standard unit names defined
# in UNITS
VOL_TO_MASS_TABLE = {
    ("pt.", "lb.") : 1,
    ("tbs.", "oz.") : 0.5,
    ("c.", "oz.") : 8,
    ("pt.", "oz.") : 16,
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

def guess_singulars (s): return []
def guess_plurals (s):
    """This is a very lame attempt at Dutch grammar!

    Obviously this isn't close to a good plural generator, but I
    thought it might make an occasional match, so what the hell.
    """
    return [s+"en",s+"s"]

IGNORE = []
