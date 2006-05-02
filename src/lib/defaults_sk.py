#!/usr/bin/python
# -*- coding: utf-8 -*-
#
## we set up default information.
## first, easy to maintain lists which can eventually be moved to
## files.

# TRANSLATOR WARNING: DO NOT TRANSLATE THE FIELD NAMES: ONLY THE VALUES!!!
CREDITS = "Branislav Brango Hanáček"

# only translate the items in the list [..] (and feel free to create categories
# that make sense for your locale -- no need to translate these ones). DO NOT
# translate 'cuisine','rating','source' or 'category'
fields={'cuisine': [
                    'Americká',
                    'Čínska',
                    'Čínska kantonská',
                    'Čínska kantonská',
                    'Čínska šanghajská',
                    'Čínska pekingská',
                    'Čínska sečuánska',
                    'Česká',
                    'Japonská',
                    'Juhozápadná',
                    'Maďarská',
                    'Mexická',
                    'Nemecká',
                    'Nemecká porýnie',
                    'Slovenská',
                    'Talianska',
                    'Thajská',
                    'Vietnamská'
                   ],
        'rating' : [
                    'Výnikajúce',
                    'Výborné',
                    'Dobré',
                    'Jedlé',
                    'Slabé',
                    'Nechutné'
                   ],
        'source' : [],
        'category' : [
                      'Cestovinový šalát',
                      'Cestoviny bezmäsité',
                      'Cestoviny skoro bezmäsité',
                      'Cestoviny s mäsom',
                      'Grilovanie',
                      'Jedlá z bravčového mäsa',
                      'Jedlá z diviny',
                      'Jedlá z húb',
                      'Jedlá z hovädzieho mäsa',
                      'Jedlá z hydiny',
                      'Jedlá z mäsa',
                      'Jedlá z rýb',
                      'Jedlá z teľacieho mäsa',
                      'Konzervovanie',
                      'Konzervovanie - nátierky',
                      'Šalát',
                      'Polievka',
                      'Polievka bezmäsitá',
                      'Polievka mäsová',
                      'Polievka skoro bezmäsitá',
                      'Polievka z rýb', 
                      'Predjedlo',
                      'Skoro bezmäsité jedlá',
                      'Zákusok',
                      'Zeleninový šalát',
                      'Zeleninový šalát s mäsom'
                     ],
                  }

# In English, there are a heck of a lot of synonyms. This is a list
# for those synonyms.  ["preferred word","alternate word","alternate word"]
# If there are none of these that you can think of in your language, just
# set this to:
SYNONYMS=[]

# a dictionary key=ambiguous word, value=list of possible non-ambiguous terms
AMBIGUOUS = {}


# triplicates ITEM, KEY, SHOPPING CATEGORY
#
# These will be defaults. They should include whatever foods might be
# standard for your locale, with whatever sensible default categories
# you can think of (again, thinking of your locale, not simply translating
# what I've done).
INGREDIENT_DATA = [
# základné potraviny
                   ["voda","voda","základné potraviny"],
                   ["hnedý cukor","hnedý cukor","základné potraviny"],
                   ["cukor","cukor","základné potraviny"],
                   ["balzamikový ocot","balzamikový ocot","základné potraviny"],
                   ["vínny ocot","vínny ocot","základné potraviny"],
                   ["jablčný ocot","jablčný ocot","základné potraviny"],
                   ["ryžové víno","ryžové víno","základné potraviny"],
                   ["ryža","ryža","základné potraviny"],
                   ["guľatá ryža","guľatá ryža","základné potraviny"],
                   ["ryža basmati","ryža basmati","základné potraviny"],
                   ["dlhozrnná ryža","dlhozrnná ryža","základné potraviny"],
                   ["ryža natural","ryža natural","základné potraviny"],
                   ["kuskus","kuskus","základné potraviny"],
                   ["špagety","špagety","základné potraviny"],
                   ["cestoviny","cestoviny","základné potraviny"],
                   ["chlieb","chlieb","základné potraviny"],
                   ["pečivo","pečivo","základné potraviny"],
                   ["žemľa","žemľa","základné potraviny"],
                   ["horčica","horčica","základné potraviny"],
                   ["kremžská horčica","kremžská horčica","základné potraviny"],
                   ["dijonská horčica","dijonská horčica","základné potraviny"],
                   ["krutóny","krutóny","základné potraviny"],
                   ["pomarančová šťava","pomarančová šťava","základné potraviny"],
                   ["citrónová šťava","citrónová šťava","základné potraviny"],
                   ["vajce","vajce","základné potraviny"],
                   ["med","med","základné potraviny"],
                   ["droždie","droždie","základné potraviny"],
                   ["sušené droždie","sušené droždie","základné potraviny"],
                   ["paradajkový pretlak","paradajkový pretlak","základné potraviny"],
                   ["hladká múka","hladká múka","základné potraviny"],
                   ["polohrubá múka","polohrubá múka","základné potraviny"],
                   ["hrubá múka","hrubá múka","základné potraviny"],
                   ["celozrnná múka","celozrnná múka","základné potraviny"],
                   ["krupica","krupica","základné potraviny"],
                   ["biele víno", "biele víno","základné potraviny"],
                   ["červené víno", "červené víno","základné potraviny"],
                   ["soľ", "soľ","základné potraviny"],
                   ["morská soľ", "morská soľ","základné potraviny"],

# oleje a tuky
                   ["olej","olej","oleje a tuky"],
                   ["slnečnicový olej","slnečnicový olej","oleje a tuky"],
                   ["olivový olej","olivový olej","oleje a tuky"],
                   ["sójový olej","sójový olej","oleje a tuky"],
                   ["sezamový olej","sezamový olej","oleje a tuky"],
                   ["ľanový olej","ľanový olej","oleje a tuky"],
                   ["bravčová masť","bravčová masť","oleje a tuky"],
                   ["husacia masť","husacia masť","oleje a tuky"],
                   ["kačacia masť","kačacia masť","oleje a tuky"],
                   ["vlašský orech","vlašský orech","oleje a tuky"],
                   ["arašídy","arašídy","oleje a tuky"],
                   ["pražené arašídy","pražené arašídy","oleje a tuky"],
                   ["orechy kešu","orechy kešu","oleje a tuky"],
                   ["majonéza","majonéza","oleje a tuky"],
                   ["sezamové semená","sezamové semená","oleje a tuky"],
                   ["slnečnicové semená","slnečnicové semená","oleje a tuky"],
                   ["píniové semená","píniové semená","oleje a tuky"],

# mlieko a mliečne výrobky
                   ["mlieko","mlieko","mlieko a mliečne výrobky"],
                   ["maslo","maslo","mlieko a mliečne výrobky"],
                   ["syr","syr","mlieko a mliečne výrobky"],
                   ["strúhaný syr","strúhaný syr","mlieko a mliečne výrobky"],
                   ["syr Niva","syr Niva","mlieko a mliečne výrobky"],
                   ["camembert","camembert","mlieko a mliečne výrobky"],
                   ["bryndza","bryndza","mlieko a mliečne výrobky"],
                   ["tavený syr","tavený syr","mlieko a mliečne výrobky"],
                   ["tvaroh","tvaroh","mlieko a mliečne výrobky"],
                   ["syr feta","syr feta","mlieko a mliečne výrobky"],
                   ["parmezán","parmezán","mlieko a mliečne výrobky"],
                   ["mozarella","mozarella","mlieko a mliečne výrobky"],
                   ["jogurt","jogurt","mlieko a mliečne výrobky"],
                   ["kefír","kefír","mlieko a mliečne výrobky"],
                   ["sladká smotana","sladká smotana","mlieko a mliečne výrobky"],
                   ["kyslá smotana","kyslá smotana","mlieko a mliečne výrobky"],
                   ["syr ricotta","syr ricotta","mlieko a mliečne výrobky"],
                   ["čedar","čedar","mlieko a mliečne výrobky"],
# bylinky
                   ["koriandrová vňať","koriandrová vňať","bylinky"],
                   ["pažítka","pažítka","zelenina"],
                   ["petržlenová vňať","petržlenová vňať","zelenina"],
                   ["zelerová vňať","zelerová vňať","zelenina"],
# strukoviny
                   ["bôb","bôb","strukoviny"],
                   ["čierna fazuľa","čierna fazuľa","strukoviny"],
                   ["cícer","cícer","strukoviny"],
                   ["fazuľa azuki","fazuľa azuki","strukoviny"],
                   ["fazuľa borlotti","fazuľa borlotti","strukoviny"],
                   ["fazuľa","fazuľa","strukoviny"],
                   ["fazuľa šarlátová","fazuľa šarlátová","strukoviny"],
                   ["fazuľa mungo","fazuľa mungo","strukoviny"],
                   ["fazuľové klíčky","fazuľové klíčky","strukoviny"],
                   ["maslová fazuľa","maslová fazuľa","strukoviny"],
                   ["sója","sója","strukoviny"],
                   ["šošovica","šošovica","strukoviny"],
# koreniny
                   ["aníz","aníz","korenie"],
                   ["citrónová tráva","citrónová tráva","korenie"],
                   ["čilli paprička","čilli paprička","korenie"],
                   ["paprika jalapeno","paprika jalapeno","korenie"],
                   ["zázvor","zázvor","korenie"],
                   ["mletý zázvor","mletý zázvor","korenie"],
                   ["koriandrové semeno","koriandrové semeno", "korenie"],
                   ["bazalka čerstvá","bazalka čerstvá", "korenie"],
                   ["bazalka sušená","bazalka sušená", "korenie"],
                   ["garam masala","garam masala", "korenie"],
                   ["škorica celá","škorica celá", "korenie"],
                   ["škorica mletá","škorica mletá", "korenie"],
                   ["rasca celá","rasca celá", "korenie"],
                   ["rasca mletá","rasca mletá", "korenie"],
                   ["čierne korenie celé","čierne korenie celé", "korenie"],
                   ["čierne korenie mleté","čierne korenie mleté", "korenie"],
                   ["biele korenie celé","biele korenie celé", "korenie"],
                   ["biele korenie mleté","biele korenie mleté", "korenie"],
                   ["zelené korenie celé","zelené korenie celé", "korenie"],
                   ["zelené korenie mleté","zelené korenie mleté", "korenie"],
                   ["salsa","salsa", "korenie"],
                   ["sójová omáčka","sójová omáčka", "korenie"],
                   ["sójová omáčka svetlá","sójová omáčka svetlá", "korenie"],

# huby
                   ["bedľa","bedľa","huby"],
                   ["huby","huby","huby"],
                   ["šampiňóny","šampiňóny","huby"],
                   ["kuriatka","kuriatka","huby"],
                   ["huby šintake","huby šintake","huby"],
                   ["hliva ustricová","hliva ustricová","huby"],
# zelenina
                   ["artičoky","artičoky","zelenina"],
                   ["avokádo","avokádo","zelenina"],
                   ["baklažán","baklažán","zelenina"],
                   ["biela reďkovka","biela reďkovka","zelenina"],
                   ["brokolica","brokolica","zelenina"],
                   ["bruselská kapusta","bruselská kapusta","zelenina"],
                   ["cesnak","cesnak","zelenina"],
                   ["cibuľa","cibuľa","zelenina"],
                   ["biela cibuľa","biela cibuľa","zelenina"],
                   ["červená cibuľa","červená cibuľa","zelenina"],
                   ["cukini","cukini","zelenina"],
                   ["cukrová repa","cukrová repa","zelenina"],
                   ["cvikľa","cvikľa","zelenina"],
                   ["čínska kapusta (bok choy)","čínska kapusta (bok choy)","zelenina"],
                   ["červená paprika","červená paprika","zelenina"],
                   ["dyňa","dyňa","zelenina"],
                   ["envídia","envídia","zelenina"],
                   ["fenikel","fenikel","zelenina"],
                   ["frisee šalát","frisee šalát","zelenina"],
                   ["hlávkový šalát","hlávkový šalát","zelenina"],
                   ["hrach","hrach","strukoviny"],
                   ["jarná cibuľka","jarná cibuľka","zelenina"],
                   ["jeruzalemské artičoky","jeruzalemské artičoky","zelenina"],
                   ["kaleráb","kaleráb","zelenina"],
                   ["kapusta","kapusta","zelenina"],
                   ["karfiol","karfiol","zelenina"],
                   ["koreňová zelenina","koreňová zelenina","zelenina"],
                   ["koriander","koriander","korenie"],
                   ["kukurica","kukurica","obilniny"],
                   ["kvaka","kvaka","zelenina"],
                   ["kvasená uhorka","kvasená uhorka","zelenina"],
                   ["šalátová uhorka","šalátová uhorka","zelenina"],
                   ["uhorka","uhorka","zelenina"],
                   ["šalotka","šalotka","zelenina"],
                   ["špargľa","špargľa","zelenina"],
                   ["špenát","špenát","zelenina"],
                   ["žerucha","žerucha","zelenina"],
                   ["žihľava","žihľava","zelenina"],
                   ["mrkva","mrkva","zelenina"],
                   ["paštrnák","paštrnák","zelenina"],
                   ["pór","pór","zelenina"],
                   ["paprika","paprika","zelenina"],
                   ["paradajka","paradajka","zelenina"],
                   ["kokteilové paradajky","kokteilové paradajky","zelenina"],
                   ["petržlen","petržlen","zelenina"],
                   ["radicchio","radicchio","zelenina"],
                   ["reďkovka","reďkovka","zelenina"],
                   ["rukola","rukola","zelenina"],
                   ["sladký zemiak","sladký zemiak","zelenina"],
                   ["tekvica","tekvica","zelenina"],
                   ["uhorka","uhorka","zelenina"],
                   ["vodný gaštan","vodný gaštan","zelenina"],
                   ["wasabi","wasabi","zelenina"],
                   ["zelená fazuľka","zelená fazuľka","strukoviny"],
                   ["zelená fazuľka","zelená fazuľka","zelenina"],
                   ["zeler","zeler","zelenina"],
                   ["zemiak","zemiak","zelenina"],
                   ["olivy zelené","olivy zelené","zelenina"],
                   ["olivy čierne","olivy čierne","zelenina"],
# Ovocie
                   ["ananás","ananás","ovocie"],
                   ["ananásový melón","ananásový melón","ovocie"],
                   ["arónia","arónia","ovocie"],
                   ["banán","banán","ovocie"],
                   ["baza ","baza ","ovocie"],
                   ["biela ríbezľa","biela ríbezľa","ovocie"],
                   ["borievka","borievka","ovocie"],
                   ["broskyňa","broskyňa","ovocie"],
                   ["brusnica ","brusnica ","ovocie"],
                   ["citrón","citrón","ovocie"],
                   ["clementine","clementine","ovocie"],
                   ["čerešňa","čerešňa","ovocie"],
                   ["černica","černica","ovocie"],
                   ["červená ríbezľa","červená ríbezľa","ovocie"],
                   ["čierna ríbezľa","čierna ríbezľa","ovocie"],
                   ["dráč ","dráč ","ovocie"],
                   ["dula","dula","ovocie"],
                   ["durian","durian","ovocie"],
                   ["ďatľa","ďatľa","ovocie"],
                   ["figa","figa","ovocie"],
                   ["granátové jablko","granátové jablko","ovocie"],
                   ["grepfruit","grepfruit","ovocie"],
                   ["guáve ","guáve ","ovocie"],
                   ["hloh","hloh","ovocie"],
                   ["hrozno","hrozno","ovocie"],
                   ["jablko","jablko","ovocie"],
                   ["jahoda ","jahoda ","ovocie"],
                   ["jarabina","jarabina","ovocie"],
                   ["jojoba","jojoba","ovocie"],
                   ["kiwi","kiwi","ovocie"],
                   ["kokosový orech","kokosový orech","ovocie"],
                   ["liči","liči","ovocie"],
                   ["limeta","limeta","ovocie"],
                   ["malina","malina","ovocie"],
                   ["mandarínka","mandarínka","ovocie"],
                   ["mango","mango","ovocie"],
                   ["maracuja","maracuja","ovocie"],
                   ["marhuľa","marhuľa","ovocie"],
                   ["medový melón","medový melón","ovocie"],
                   ["mišpuľa","mišpuľa","ovocie"],
                   ["moruša","moruša","ovocie"],
                   ["nektarinka","nektarinka","ovocie"],
                   ["ostružina moruška","ostružina moruška","ovocie"],
                   ["papája","papája","ovocie"],
                   ["pitaya","pitaya","ovocie"],
                   ["plané jablko","plané jablko","ovocie"],
                   ["pomaranč","pomaranč","ovocie"],
                   ["rakytník","rakytník","ovocie"],
                   ["rebarbora","rebarbora","zelenina"],
                   ["trnka","trnka","zelenina"],
                   ["slivka","slivka","ovocie"],
                   ["vodný melón ","vodný melón ","ovocie"],
                   ["zelené jablko","zelené jablko","ovocie"],
## ryby a morské potvory
                   ["ančivičky","ančivičky","ryby a morské potvory"],
                   ["okún","okún","ryby a morské potvory"],
                   ["treska","treska","ryby a morské potvory"],
                   ["úhor","úhor","ryby a morské potvory"],
                   ["platesa","platesa","ryby a morské potvory"],
                   ["šťuka","šťuka","ryby a morské potvory"],
                   ["sardinka","sardinka","ryby a morské potvory"],
                   ["losos","losos","ryby a morské potvory"],
                   ["morský okún","morský okún","ryby a morské potvory"],
                   ["žralok","žralok","ryby a morské potvory"],
                   ["chňapáč","chňapáč","ryby a morské potvory"],
                   ["jeseter","jeseter","ryby a morské potvory"],
                   ["mečiar","mečiar","ryby a morské potvory"],
                   ["pstruh","pstruh","ryby a morské potvory"],
                   ["tuniak","tuniak","ryby a morské potvory"],
                   ["belica","belica","ryby a morské potvory"],
                   ["ikry","ikry","ryby a morské potvory"],
                   ["kaviár","kaviár","ryby a morské potvory"],
                   ["krab","krab","ryby a morské potvory"],
                   ["rak","rak","ryby a morské potvory"],
                   ["homár","homár","ryby a morské potvory"],
                   ["kreveta","kreveta","ryby a morské potvory"],
                   ["garnát","garnát","ryby a morské potvory"],
                   ["mäkkýš","mäkkýš","ryby a morské potvory"],
                   ["mušľa","mušľa","ryby a morské potvory"],
                   ["chobotnica","chobotnica","ryby a morské potvory"],
                   ["ustrica","ustrica","ryby a morské potvory"],
                   ["slimák","slimák","ryby a morské potvory"],
                   ["kalmar","kalmar","ryby a morské potvory"],
                   ["hrebenatka","hrebenatka","ryby a morské potvory"],
## mäso a mäsové výrobky
                   ["slanina","slanina","mäso a údeniny"],
                   ["oravská slanina","oravská slanina","mäso a údeniny"],
                   ["anglická slanina","anglická slanina","mäso a údeniny"],
                   ["klobása","klobása","mäso a údeniny"],
                   ["párky","párky","mäso a údeniny"],
                   ["saláma","saláma","mäso a údeniny"],
                   ["maďarská saláma","maďarská saláma","mäso a údeniny"],
                   ["suchá saláma","suchá saláma","mäso a údeniny"],
                   ["šunka","šunka","mäso a údeniny"],
                   ["baranie mäso","baranie mäso","mäso a údeniny"],
                   ["jahňacie mäso","jahňacie mäso","mäso a údeniny"],
                   ["teľacie mäso","teľacie mäso","mäso a údeniny"],
                   ["steak","steak","mäso a údeniny"],
                   ["hamburger","hamburger","mäso a údeniny"],
                   ["bravčové mäso","bravčové mäso","mäso a údeniny"],
                   ["hovädzie mäso","hovädzie mäso","mäso a údeniny"],
                   ["kuracie mäso","kuracie mäso","mäso a údeniny"],
                   ["slepačie mäso","slepačie mäso","mäso a údeniny"],
                   ["morčacie mäso","morčacie mäso","mäso a údeniny"],
                   ["husacie mäso","husacie mäso","mäso a údeniny"],
                   ["kačacie mäso","kačacie mäso","mäso a údeniny"],
                   ["kuracie prsia","kuracie prsia","mäso a údeniny"],
                   ["kuracie krídla","kuracie krídla","mäso a údeniny"],
                   ["morčacie prsia","morčacie prsia","mäso a údeniny"],
                   ["tlačenka","tlačenka","mäso a údeniny"],
                   ["celé kura","celé kura","mäso a údeniny"],
                   ["celá sliepka","celá sliepka","mäso a údeniny"],
                   ["bravčové kolienko","bravčové kolienko","mäso a údeniny"],
                   ["bravčové paprčky","bravčové paprčky","mäso a údeniny"],
                   ["údené karé","údené karé","mäso a údeniny"],
                   ["bravčová krkovička","bravčová krkovička","mäso a údeniny"],
                   ["bravčová panenka","bravčová panenka","mäso a údeniny"],
                   ["sviečkovica","sviečkovica","mäso a údeniny"]
                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
CONVERTER_TABLE = {
    ("Šálka", "ČL"):16,
    ("PL", "ČL"):3,
    ("l", "ml"):1000,
    ("l", "cl"):100,
    ("l", "dl"):10,
    ("kg", "g"):1000,
    ("g", "mg"):1000
    }

# DENSITIES of common foods. This allows us to convert between mass and volume.
DENSITY_TABLE={
    "voda":1,
    "juice, grape":1.03,
    "vegetable broth":1,
    "broth, vegetable":1,
    "broth, chicken":1,
    "milk":1.029,
    "milk, whole":1.029,
    "milk, skim":1.033,
    "milk, 2%":1.031,
    "milk, 1%":1.03,
    "coconut milk":0.875,
    "buttermilk":1.03,
    "heavy cream":0.994,
    "light cream":1.012,
    "half and half":1.025,
    "honey":1.420,
    "sugar, white":1.550,
    "salt":2.165,
    "butter":0.911,
    "oil, vegetable":0.88,
    "oil, olive":0.88,
    "oil, corn":0.88,
    "oil, sesame":0.88,
    "flour, all purpose": 0.6,
    "flour, whole wheat": 0.6,
    "corn starch": 0.6,
    "sugar, powdered": 0.6,
    "sugar, confectioners": 0.6
            }

# Stand unit names and alternate unit names that might appear.
# For example: "c." is our standard for cup. "cup","c." or "cups" might appear
# in a recipe we are importing.
# Each item of this list looks like this:
#
# ["standard", ["alternate1","alternate2","alternate3",...]]

UNITS = [
         ["ČL",    ["čajová lyžička","ČL.", "čajové lyžičky", "čajovej lyžičky", "čajových lyžičiek"]],
         ["PL",    ["polievková lyžica","PL.", "polievkové lyžice", "polievovej lyžice", "polievkových lyžíc"]],
         ["šálka", ["šálky", "šálok"]],
         ["ml",    ["mililiter", "ml.", "mililitre", "mililitrov", "mililitra"]],
         ["cl",    ["centiliter","cl.", "centilitre", "centiliterov", "centilitra"]],
         ["dl",    ["deciliter","dl.", "decilitre","decilitrov", "decilitra"]],
         ["l",     ["liter", "l.", "litre", "litrov", "litra"]],
         ["g",     ["gram", "g.", "gramy", "gramov", "gramu"]],
         ["mg",    ["miligram", "mg.", "miligramy", "miligramov", "miligramu"]],
         ["kg",    ["kilogram","kg.", "kilogramy",  "kilogramov", "kilogramu"]]
         ]

WEIGHTS = ['g','mg','kg']
VOLUMES = ['ČL','PL','ml','cl','dl','l', 'šálka']

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
                     ('l',(1,None)),]
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
    ("ml.", "g."):['density',1]}

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

# A quick look at the wikipedia suggests that plural forms of nouns
# may be rather complex
# http://en.wikipedia.org/wiki/Slovak_declension#Nouns so I won't
# attempt it myself.

# If someone implements this at a later date, please note that if
# guess_singulars() returns something, guess_plurals() usually won't
# be called (Gourmet uses these when trying to find a key for a word
# -- if it sees "Tomatoes" and believes that the word is "Tomato", it
# won't bother trying to guess "Tomatoeses".

def guess_singulars (s): return []
def guess_plurals (s): return []

IGNORE=[]

NUMBERS = {
    }
