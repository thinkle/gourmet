# -*- coding: utf-8 -*-
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

# Language: Deutsch (German)
# Translator: 
# Last-updated: 2005-01-15 (07/18/05)

CREDITS = u""

#The next line can be used to determine some things about how to handle this language
LANG_PROPERTIES={'hasAccents':True, 'capitalisedNouns':True,'useFractions':False} 


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

fields={'cuisine': ['deutsch', 'amerikanisch','italienisch','französisch',
		    'mexikanisch','asiatisch','indisch','griechisch','vegetarisch'],

        'rating' : ['5 - ausgezeichnet','4 - lecker',
		    '3 - OK','2 - mittelmäßig','1 - vergiss es!',
                    '(nicht geprüft)'],

        'source' : [],

        'category' :[
		     'Nachspeise','Vorspeise','Hauptgericht',
		     'Beilage','Salat','Suppe','Frühstück',
		     'Picknick','Andere','Plan'],
                  }

# In English, there are a heck of a lot of synonyms. This is a list
# for those synonyms.  [u"preferred word","alternate word","alternate word"]
# If there are none of these that you can think of in your language, just
# set this to:
# SYNONYMS=[]

# note from translator: some terms are not standard but used in common langugage, some are used in a fautive manner, 
# I decided to put them in different sections so it is still clear what is a synonym and what should not be a synonym.
SYNONYMS=[
    # the first item of each list is the default
    [u"Cocktailtomaten", u"Tomaten, cherry"],
    [u"Alfaalfa",u"Alfapha",u"Luzerne"],
    [u"Porree",u"Lauch"],
    [u"Frühlingszwiebel",u"Lauch-Zwiebeln"],
    [u"Zuckermelone",u"Gartenmelone"],
    [u"Bleichsellerie",u"Stangensellerie", u"Straudensellerie"],
    [u"Hammelfleisch",u"Hammel"],
    [u"Kalbfleisch",u"Kalb"],
    [u"Truthahn",u"Puter",u"Pute"],
    [u"Rindfleisch",u"Rind"],
    [u"Rotbusch",u"Rooibos",u"Rooibosch"],
    [u"Seelachs",u"Köhler"],
    [u"Anschovis",u"Anchovis",u"Sardelle"],
    [u"Kabeljau",u"Dorsch"],
    [u"Nutella", u"Nusspli"],
    [u"Tomatenmark",u"Tomatenkonzentrat"],
    [u"Weizenmehl",u"Mehl, weiß"],
    [u"Soja-Milch",u"Sojamilch",u"Soya-Milch", u"Soja Milch"],
    [u"Soja-Sauce", u"sauce soja",u"sauce soya",u"Soya-Sauce",u"Sojasoße", u"Sojasosse"],
    [u"Soja",u"Soya"], 
    [u"Sojabohnen",u"Soyabohnen"], 
    [u"Püree",u"Kartoffelpüree"],
    [u"Müsli",u"Muesli"],
    [u"Nudeln",u"Pasta"],
    [u"Chile",u"Chili",u"Chilli"],
    [u"Zucchini", u"Zuchini", u"Courgette"],
    [u"Tafeltrauben",u"Trauben, weiß",u"Trauben, grün"],
    [u"Garam Masala",u"Masala",u"Massala",u"Garam Massala"],
    [u"Gemüsebouillon",u"Gemüsebrühe"],
    [u"Hühnerbouillon",u"Hühnerbrühe"],
    [u"Muskat",u"Muskatnuss",u"Muscat",u"Muscatnuss"],
    [u"Sesammus",u"Tahin"],
    [u"Brokkoli", u"Broccoli"], 
    [u"Kräuter",u"gemischte Kräuter"],
    [u"Langkornreis",u"Reis"],
    [u"Eierschwammerl",u"Pfifferlinge"],
    [u"Herrenpilze",u"Steinpilze"],
    [u"Paradeiser",u"Tomaten"],

    # Irregular plurals
    [u"Äpfel",u"Apfel"],
    [u"Pfirsiche"u"Pfirsich"],
    [u"Nüsse", u"Nuss"],
    [u"Eier",u"Ei"]

    #non-standard usage
 
    #fautive/discouraged usages
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

AMBIGUOUS = {
    'Sellerie':['Sellerie','Staudensellerie'],
    }


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
# u"knows" about foods that they enter.

# I generated the below list using the wikipedia entry on foods as my
# starting point. You may want to do something similar for your
# locale.  Also, if the syntax of the below is too complicated, you
# can send me a list of category headings and ingredients for your
# locale and I'll do the necessary formatting <Thomas_Hinkle@alumni.brown.edu>

INGREDIENT_DATA = [  ## G e m ü s e  
		   [u"Alfaalfa",u"Alfalfa",u"Gemüse"],                 			#alfalfa sprouts
                   [u"Anis",u"Anis",u"Gemüse"],                       			#anise
                   [u"Artischocke",u"Artischocke",u"Gemüse"],				#artichoke
                   [u"Ölranke",u"Ölranke",u"Gemüse"],					#rocket
                   [u"Spargel",u"Spargel",u"Gemüse"],					#asparagus (white)
                   [u"weißer Spargel",u"Spargel, weißer",u"Gemüse"],			#asparagus - white
                   [u"grüner Spargel",u"Spargel, grüner",u"Gemüse"],			#asparagus - green
                   [u"Aubergine",u"Aubergine",u"Gemüse"],					#aubergine
                   [u"Avocado",u"Avocado",u"Gemüse"],					#avocado
                   [u"Brokkoli",u"Brokkoli",u"Gemüse"],					#broccoli
	           [u"Spinat",u"Spinat",u"Gemüse"],					#spinach
                   [u"Rosenkohl",u"Kohl, Rosenkohl",u"Gemüse"],				#brussels sprouts
                   [u"Kohl",u"Kohl",u"Gemüse"],						#cabbage
                   [u"Weißkohl",u"Kohl, Weißkohl",u"Gemüse"],				#white cabbage
                   [u"Rotkohl",u"Kohl, Rotkohl",u"Gemüse"],				#red cabbage
                   [u"Blumenkohl",u"Kohl, Blumenkohl",u"Gemüse"],				#cauliflower
                   [u"Chinakohl",u"Kohl, Chinakohl",u"Gemüse"],				#china cabbage
                   [u"Kohlrabi",u"Kohl, Kohlrabi",u"Gemüse"],				#kohlrabi
                   [u"Grünkohl",u"Kohl, Grünkohl",u"Gemüse"],				#kale

                   [u"Bleichsellerie",u"Bleichsellerie",u"Gemüse"],			#celery
                   [u"Zitronengras",u"Zitronengras",u"Gemüse"],				#lemon grass
                   [u"Mais",u"Mais",u"Gemüse"],						#corn

                   [u"Champignons",u"Champignons",u"Gemüse"],				#button mushrooms
                   [u"Pilze",u"Pilze",u"Gemüse"],						#large mushrooms
                   [u"Steinpilz",u"Steinpilze",u"Gemüse"],				#mushrooms
		   [u"Pfifferlinge",u"Pfifferlinge",u"Gemüse"],				#other woodland fungus

                   [u"Senfkeimlinge",u"Senfkeimlinge",u"Gemüse"],				#mustard greens
                   [u"Brennessel",u"Brennessel",u"Gemüse"],				#nettles
                   [u"Okra",u"Okra",u"Gemüse"],						#okra
                   [u"Schnittlauch",u"Schnittlauch",u"Gemüse"],				#chives

                   [u"Zwiebeln",u"Zwiebeln",u"Gemüse"],					#onion
                   [u"Schalotte",u"Schalotte",u"Gemüse"],					#shallot
                   [u"Frühlingszwiebel",u"Frühlingszwiebel",u"Gemüse"],			#spring onion, scallion
                   [u"rote Zwiebeln, rot",u"Zwiebeln, rote",u"Gemüse"],			#red (spanish) onion
                   [u"weiße Zwiebeln",u"Zwiebeln, weiße",u"Gemüse"],			#white onion
                   [u"gelbe Zwiebeln",u"Zwiebeln, gelbe",u"Gemüse"],			#yellow onion
                   [u"Metzgerzwiebeln",u"Zwiebeln, Metzger-",u"Gemüse"],			#large onion (salad)
                   [u"Speisezwiebeln",u"Zwiebeln, Speise-",u"Gemüse"],			#standard cooking onion
                   [u"Knoblauch",u"Knoblauch",u"Gemüse"],					#garlic
                   [u"Porree",u"Porree",u"Gemüse"],					#leek

                   [u"Paprika",u"Paprika",u"Gemüse"],					#pepper
                   [u"rote Paprika",u"Paprika, rote",u"Gemüse"],				#red bell pepper
                   [u"grüne Paprika",u"Paprika, grüne",u"Gemüse"],			#
                   [u"gelbe Paprika",u"Paprika, gelbe",u"Gemüse"],			#
                   [u"Chile",u"Chile",u"Gemüse"],						#chilli pepper
                   [u"Jalapeño-Chile",u"Chile, Jalapeño",u"Gemüse"],			#jalapeño pepper
                   [u"Habanero-Chile",u"Chile, Habanero",u"Gemüse"],			#habanero pepper

                   [u"Radieschen",u"Radieschen",u"Gemüse"],				#radish
                   [u"Rote Beet",u"Rote Beet",u"Gemüse"],					#beetroot
                   [u"Möhren",u"Möhren",u"Gemüse"],					#carrot
	           [u"Rettich",u"Rettich",u"Gemüse"],					#horse radish
                   [u"Wasabi",u"Wasabi",u"Gemüse"],					#japanese horseraddish
                   [u"Sellerie",u"Sellerie",u"Gemüse"],					#celeriac
                   [u"Pastinake",u"Pastinake",u"Gemüse"],					#parsnip
                   [u"Kohlrübe",u"Kohlrübe",u"Gemüse"],					#turnip
                   [u"Fenchel",u"Fenchel",u"Gemüse"],					#fennel

                   [u"Kopfsalat",u"Kopfsalat",u"Gemüse"],					#lettuce 
                   [u"Rucolasalat",u"Rucolasalat",u"Gemüse"],				#rucola 
                   [u"Friseesalat",u"Friseesalat",u"Gemüse"],				#open lettuce 
                   [u"Feldsalat",u"Feldesalat",u"Gemüse"],				#lettuce 

                   [u"Saubohnen",u"Saubohnen",u"Gemüse"],					#broad beans
                   [u"Bobby Bohnen",u"Bobby Bohnen",u"Gemüse"],				#small green beans
                   [u"Haricots",u"Haricots",u"Gemüse"],					#haricot beans
                   [u"Carbasc",u"Carbasc",u"Gemüse"],					#runner beans
                   [u"Erbsen",u"Erbsen",u"Gemüse"],					#peas
                   [u"Zuckererbsen",u"Zuckererbsen",u"Gemüse"],				#mange tous

                   [u"Zucchini",u"Zucchini",u"Gemüse"],					#zucchini
                   [u"Gurke (Salat-)",u"Gurke (Salat-)",u"Gemüse"],			#cucumber

                   [u"Kürbis",u"Kürbis",u"Gemüse"],					#pumpkin

                   [u"Cocktailtomaten",u"Tomaten, Cocktail-",u"Gemüse"],			#cocktail (cherry) tomato
                   [u"Tomaten",u"Tomaten",u"Gemüse"],					#cherry tomato
                   [u"Rispentomaten",u"Tomaten, Rispen-",u"Gemüse"],			#tomato on stems

                   [u"Kartoffel",u"Kartoffel",u"Gemüse"],					#potato
                   [u"Speisekartoffeln",u"Kartoffeln, Speise-",u"Gemüse"],		#standard cooking potatoes
                   [u"Süßkartoffel",u"Süßkartoffel",u"Gemüse"],				#sweet potato

                   [u"Jamswurzel",u"Jamswurzel",u"Gemüse"],				#yam
                   [u"Wasserkastanie",u"Wasserkastanie",u"Gemüse"],			#water chestnut
                   [u"Brunnenkresse",u"Brunnenkresse",u"Gemüse"],				#watercress

                   [u"Oliven",u"Oliven",u"Gemüse"],					#
                   [u"grüne Oliven",u"Oliven, grüne",u"Gemüse"],				#
                   [u"schwarze Oliven",u"Oliven, schwarze",u"Gemüse"],			#


                   ## H ü l s e n f r u c h t e
                   [u"grüne Bohnen",u"Bohnen, grüne",u"Gemüse"],				#green beans
                   [u"weiße Bohnen",u"Bohnen, weiße",u"Hülsenfrüchte"],			#green beans
                   [u"Azuki Bohnen",u"Bohnen, Azuki",u"Hülsenfrüchte"],			#azuki beans
                   [u"schwarze Bohnen",u"Bohnen, schwarze",u"Hülsenfrüchte"],		#black beans
                   [u"Borlottibohnen",u"Bohnen, Borlotti-",u"Hülsenfrüchte"],		#borlotti beans (not sure)
                   [u"Kichererbsen",u"Kichererbsen",u"Hülsenfrüchte"],			#chickpeas, garbanzos, or ceci beans
                   [u"Kidneybohnen",u"Bohnen, Kidney-",u"Hülsenfrüchte"],			#kidney beans
                   [u"Teller-Linsen",u"Linsen, Teller-",u"Hülsenfrüchte"],			#standard lentils
                   [u"rote Linsen",u"Linsen, rote",u"Hülsenfrüchte"],			#red lentils
                   [u"grüne Linsen",u"Linsen, grüne",u"Hülsenfrüchte"],			#green lentils
                   [u"schwarze Linsen",u"Linsen, schwarze",u"Hülsenfrüchte"],		#black lentils
                   [u"Gartenbohnen",u"Gartenbohnen",u"Gemüse"],				#lima bean or butter bean
                   [u"Mungbohnen",u"Bohnen, Mung-",u"Hülsenfrüchte"],			#mung beans
                   [u"Sojabohnen",u"Bohnen, Soja-",u"Hülsenfrüchte"],			#soybeans
                   [u"grüne Erbsen",u"Erbsen, grüne",u"Hülsenfrüchte"],			#green dried peas
                   [u"gelbe Erbsen",u"Erbsen, gelbe",u"Hülsenfrüchte"],			#yellow dried peas
                   [u"Schälerbsen",u"Erbsen, Schälerbsen",u"Hülsenfrüchte"],		#

                   ## F r u c h t e
                   [u"Obst",u"Obst",u"Obst"],						#general fruit
                   [u"Äpfel",u"Äpfel",u"Obst"],						#apple
                   [u"rote Äpfel",u"Äpfel, rote",u"Obst"],					#
                   [u"goldene Äpfel",u"Äpfel, goldene",u"Obst"],				#
                   [u"Granny Smith Äpfel",u"Äpfel, Granny Smith",u"Obst"],		#
                   [u"Fuji Äpfel",u"Äpfel, Fuji-",u"Obst"],				#
                   [u"grüne Äpfel",u"Äpfel, grüne",u"Obst"],				#green apple
                   [u"Granatäpfel",u"Granatäpfel",u"Obst"],				#pomegranate
                   [u"Quitte",u"Quitte",u"Obst"],						#quince
                   [u"Hagebutten",u"Hagebutten",u"Obst"],					#rose hip
                   [u"Aprikosen",u"Aprikosen",u"Obst"],					#apricot
                   [u"Birnen",u"Birnen",u"Obst"],						#pear
                   [u"Conference Birnen",u"Birnen, Conference",u"Obst"],			#pear, large conference
                   [u"William Birnen",u"Birnen, William",u"Obst"],			#pear, standard william
                   [u"Kirschen",u"Kirschen",u"Obst"],					#cherry
                   [u"Pflaumen",u"Pflaumen",u"Obst"],					#plum
                   [u"Pfirsiche",u"Pfirsiche",u"Obst"],					#peach
                   [u"Nektarinen",u"Nektarinen",u"Obst"],					#nectarine
                   [u"Brombeeren",u"Beeren, Brombeeren",u"Obst"],				#blackberry
                   [u"Himbeeren",u"Beeren, Himbeeren",u"Obst"],				#raspberry
                   [u"Erdbeeren",u"Beeren, Erdbeeren",u"Obst"],				#raspberry
                   [u"Heidelbeeren",u"Beeren, Heidelbeeren",u"Obst"],			#bilberry
                   [u"Blaubeeren",u"Beeren, Blaubeeren",u"Obst"],				#blueberry
                   [u"Preiselbeeren",u"Beeren, Preiselbeeren",u"Obst"],			#cranberry
                   [u"Johannisbeeren",u"Beeren, Johannisbeeren",u"Obst"],			#red currant
                   [u"schwarze Johannisbeeren",u"Beeren, schwarze Johannisbeeren",u"Obst"],#black currant
                   [u"Holunderbeeren",u"Beeren, Holunderbeeren",u"Obst"],			#elderberry
                   [u"Stachelbeeren",u"Stachelbeeren",u"Obst"],				#gooseberry
                   [u"Kiwi",u"Kiwi",u"Obst"],						#kiwi fruit
                   [u"Papaya",u"Papaya",u"Obst"],						#pawpaw
                   [u"Zuckermelonen",u"Zucker-",u"Obst"],					#cantaloupe
                   [u"Honigmelonen",u"Melonen, Honig-",u"Obst"],				#honeydew melon
                   [u"Galiamelonen",u"Melonen, Galia-",u"Obst"],				#galia melon
                   [u"Netzmelonen",u"Melonen, Netz-",u"Obst"],				#net melon
                   [u"Wassermelonen",u"Melonen, Wasser-",u"Obst"],			#watermelon
                   [u"Feigen",u"Feigen",u"Obst"],						#fig
                   [u"Weintrauben",u"Weintrauben",u"Obst"],				#grape
                   [u"Tafeltrauben",u"Weintrauben, Tafel",u"Obst"],			#green grapes
                   [u"blaue Weintrauben",u"Weintrauben, blau",u"Obst"],			#black grapes
                   [u"Datteln",u"Datteln",u"Obst"],					#date
                   [u"Grapefruit",u"Grapefruit",u"Obst"],					#grapefruit
                   [u"Limetten",u"Limetten",u"Obst"],					#lime
                   [u"Kumquat",u"Kumquat",u"Obst"],					#kumquat
                   [u"Zitronen",u"Zitronen",u"Obst"],					#lemon
                   [u"Mandarinen",u"Mandarinen",u"Obst"],					#mandarin
                   [u"Klementinen",u"Klementinen",u"Obst"],				#clementine
                   [u"Tangerinen",u"Tangerinen",u"Obst"],					#tangerine
                   [u"Orangen",u"Orangen",u"Obst"],					#orange
                   [u"Ugli",u"Ugli",u"Obst"],						#ugli fruit
                   [u"Guave",u"Guave",u"Obst"],						#guava
                   [u"Litschi",u"Litschi",u"Obst"],					#lychee
                   [u"Passionsfrucht",u"Passionsfrucht",u"Obst"],				#passion fruit
                   [u"Banane",u"Banane",u"Obst"],						#banana
                   [u"Wegerich",u"Wegerich",u"Obst"],					#plantain
                   [u"Kokosnuss",u"Kokosnuss",u"Obst"],					#coconut
                   [u"Durion",u"Durion",u"Obst"],						#durian
                   [u"Mango",u"Mangue",u"Obst"],						#mango
                   [u"Papaya",u"Papaya",u"Obst"],						#papaya
                   [u"Ananas",u"Ananas",u"Obst"],						#pineapple
                   [u"Tamarinde",u"Tamarinde",u"Obst"],					#tamarind
                   [u"Rhabarber",u"Rhabarber",u"Obst"],					#rhubarb
 

                   ## M e e r e s f r ü c h t e
                   [u"Anchovis",u"Anchovis",u"Meeresfrüchte"],				#anchovy
                   [u"Barsch",u"Barsch",u"Meeresfrüchte"],					#bass
                   [u"Kugelfisch",u"Kugelfisch",u"Meeresfrüchte"],				#blowfish
                   [u"Wels",u"Wels",u"Meeresfrüchte"],					#catfish
                   [u"Dorsch",u"Dorsch",u"Meeresfrüchte"],					#cod
                   [u"Aal",u"Aal",u"Meeresfrüchte"],					#eel
                   [u"Flunder",u"Flunder",u"Meeresfrüchte"],				#flounder
                   [u"Schellfisch",u"Schellfisch",u"Meeresfrüchte"],			#haddock
                   [u"Haddock",u"Haddock",u"Meeresfrüchte"],				#smoked haddock
                   [u"Heilbutt",u"Heilbutt",u"Meeresfrüchte"],				#halibut
                   [u"Zander",u"Zander",u"Meeresfrüchte"],					#pike
                   [u"Seelachs",u"Seelachs",u"Meeresfrüchte"],				#pollock
                   [u"Sardine",u"Sardine",u"Meeresfrüchte"],				#sardine
                   [u"Sprotte",u"Sprotte",u"Meeresfrüchte"],				#sprat
                   [u"Lachs",u"Lachs",u"Meeresfrüchte"],					#salmon
                   [u"Sägebarsch",u"Sägebarsch",u"Meeresfrüchte"],				#sea bass
                   [u"Hai",u"Hai",u"Meeresfrüchte"],					#shark
                   [u"Seezunge",u"Seezunge",u"Meeresfrüchte"],				#sole
                   [u"Stör",u"Stör",u"Meeresfrüchte"],					#sturgeon
                   [u"Schwertfisch",u"Schwertfisch",u"Meeresfrüchte"],			#swordfish
                   [u"Forelle",u"Forelle",u"Meeresfrüchte"],				#trout
                   [u"Thunfisch",u"Thunfisch",u"Meeresfrüchte"],				#tuna
                   [u"Weißfisch",u"Weißfisch",u"Meeresfrüchte"],				#whitefish
                   [u"Wittling",u"Wittling",u"Meeresfrüchte"],				#whiting
                   [u"Rogen",u"Rogen",u"Meeresfrüchte"],					#roe of fish
                   [u"Kaviar",u"Kaviar",u"Meeresfrüchte"],					#caviar
                   [u"Krebs",u"Krebs",u"Meeresfrüchte"],					#crab
                   [u"Hummer",u"Hummer",u"Meeresfrüchte"],				#lobster
                   [u"Garnele",u"Garnele",u"Meeresfrüchte"],				#prawns
                   [u"Krabbe",u"Krabbe",u"Meeresfrüchte"],					#shrimp
                   [u"Klaffmuschel",u"Klaffmuschel",u"Meeresfrüchte"],			#clam
                   [u"Muschel",u"Muschel",u"Meeresfrüchte"],				#mussel
                   [u"Tintenfisch",u"Tintenfisch",u"Meeresfrüchte"],			#octopus
                   [u"Auster",u"Auster",u"Meeresfrüchte"],					#oyster
                   [u"Schnecke",u"Schnecke",u"Meeresfrüchte"],				#snail
                   [u"Kalmar",u"Kalmar",u"Meeresfrüchte"],				#squid
                   [u"Kammuschel",u"Kammuschel",u"Meeresfrüchte"],			#scallop

                   ## F l e i s c h
                   [u"Speck",u"Speck",u"Fleisch"],						#chopped bacon 
                   [u"Bacon",u"Bacon",u"Fleisch"],						#bacon 
                   [u"Schinken",u"Schinken",u"Fleisch"],					#ham
                   [u"Hammel",u"Hammel",u"Fleisch"],					#mutton
                   [u"Lamm",u"Lamm",u"Fleisch"],						#lamb
                   [u"Kalb",u"Kalb",u"Fleisch"],						#veal
                   [u"Steak",u"Steak",u"Fleisch"],						#steak
                   [u"Hamburger",u"Hamburger",u"Fleisch"],				#hamburger
                   [u"Roastbeef",u"Roastbeef",u"Fleisch"],					#roast beef
                   [u"Hähnchen",u"Hähnchen",u"Fleisch"],					#chicken
                   [u"Pute",u"Pute",u"Fleisch"],						#turkey
                   [u"Ente",u"Ente",u"Fleisch"],						#duck
                   [u"Gans",u"Gans",u"Fleisch"],						#goose
		   [u"Rind",u"Rind",u"Fleisch"],						#beef
		   [u"Hackfleisch",u"Hackfleisch",u"Fleisch"],				#mince beef
		   [u"Hase",u"Hase",u"Fleisch"],						#hare
		   [u"Kaninchen",u"Kaninchen",u"Fleisch"],					#rabbit
		   [u"Hirsch",u"Hirsch",u"Fleisch"],					#deer
                   [u"Hühnerbrust",u"Hühnerbrust",u"Fleisch"],				#chicken breast
                   [u"Schweinefleisch",u"Schweinefleisch",u"Fleisch"],			#pork
                   [u"Chorizo",u"Chorizo",u"Fleisch"],					#chorizo
                   [u"Salami",u"Salami",u"Fleisch"],					#salami
                   [u"Wurst",u"Wurst",u"Fleisch"],						#sausage
                   [u"Bratwurst",u"Bratwurst",u"Fleisch"],					#sausage
                   [u"Weißwurst",u"Weißwurst",u"Fleisch"],					#sausage
                   [u"Currywurst",u"Currywurst",u"Fleisch"],				#sausage

		   ## L e b e n s m i t t e l
                   [u"Weizenmehl",u"Mehl, Weizen-",u"Lebensmittel"],			#all purpose flour
                   [u"Vollkorn Weizenmehl",u"Mehl, Vollkorn Weizen-",u"Lebensmittel"],	#wholemeal flour 
                   [u"Hirsemehl",u"Mehl, Hirse-",u"Lebensmittel"],			#flour
                   [u"Roggenmischung",u"Mehl, Roggenmischung",u"Lebensmittel"],		#rye flour
                   [u"Backpulver",u"Backpulver",u"Lebensmittel"],				#baking powder
                   [u"Natron",u"Natron",u"Lebensmittel"],					#baking soda
                   [u"Schokolade",u"Schokolade",u"Lebensmittel"],				#chocolate
                   [u"Schokotröpfen",u"Schokotröpfen",u"Lebensmittel"],			#chocolate chips
                   [u"Zucker",u"Zucker",u"Lebensmittel"],					#suger
		   [u"Süßstoff",u"Süßstoff",u"Lebensmittel"],				#artificial sweetner 
                   [u"brauner Zucker",u" Zucker, braun",u"Lebensmittel"],			#brown suger
                   [u"weißer Zucker",u"Zucker, weiß",u"Lebensmittel"],			#white sugar
                   [u"Raffinade",u"Zucker, Raffinade",u"Lebensmittel"],			#castor sugar
                   [u"Salz",u"Salz",u"Lebensmittel"],					#salt
                   [u"Meersalz",u"Salz, Meer-",u"Lebensmittel"],				#sea salt
                   [u"Rosinen",u"Rosinen",u"Lebensmittel"],				#currents
                   [u"Sultanienen",u"Sultanienen",u"Lebensmittel"],			#sultanas
                   [u"geraspelte Kokosnuss",u"Kokosnuss, geraspelt",u"Lebensmittel"],	#(modifier?)
                   [u"Vanille",u"Vanille",u"Lebensmittel"],				#vanilla
                   [u"Vanilleessenz",u"Vanilleessenz",u"Lebensmittel"],			#vanilla extract
                   [u"Walnusskerne",u"Walnusskerne",u"Lebensmittel"],			#walnut
                   [u"Cashewnüsse",u"Cashewnüsse",u"Lebensmittel"],			#cashew nut
                   [u"Mandeln",u"Mandeln",u"Lebensmittel"],				#almonds
                   [u"Erdnüsse",u"Erdnüsse",u"Lebensmittel"],				#peanut
                   [u"Kartoffelpüree",u"Kartoffelpüree",u"Lebensmittel"],			#potato mash
                   [u"Klöße",u"Klöße",u"Lebensmittel"],					#potato dumplings
                   [u"Polenta",u"Polenta",u"Lebensmittel"],				#yellow cornmeal
                   [u"kernige Haferflocken",u"Haferflocken, kernig",u"Lebensmittel"],	#rolled oats
                   [u"zarte Haferflocken",u"Haferflocken, zart",u"Lebensmittel"],		#fine rolled oats
                   [u"Ketchup",u"Ketchup",u"Lebensmittel"],				#ketchup
                   [u"Mayonnaise",u"Mayonnaise",u"Lebensmittel"],				#mayonnaise
		   [u"Knäckebrot",u"Knäckebrot",u"Lebensmittel"],				#ryebread wafers
		   [u"Dosentomaten",u"Tomaten, Dosen-",u"Lebensmittel"],			#canned tomatoes
		   [u"Dosenmais",u"Mais, Dosen-",u"Lebensmittel"],			#canned sweetcorn

                   [u"Sonnenblumenkerne",u"Sonnenblumenkerne",u"Lebensmittel"],		#sunflower seeds
                   [u"Sesammus",u"Sesammus",u"Lebensmittel"],				#sesame seeds

                   [u"Zitronensaft",u"Zitronensaft",u"Lebensmittel"],			#lemon juice
                   [u"Zitronenkonzentrat",u"Zitronenkonzentrat",u"Lebensmittel"],		#lemon concentrate
                   [u"Limettensaft",u"Saft, Limetten-",u"Lebensmittel"],			#lime juice
                   [u"Orangensaft",u"Saft, Orangen",u"Lebensmittel"],			#whole orange juice
                   [u"Orangennektar",u"Saft, Orangennektar",u"Lebensmittel"],		#orange juice

                   [u"Tomatensuppe",u"Tomatensuppe",u"Lebensmittel"],			#tomato sauce
                   [u"Bouillon",u"Bouillon",u"Lebensmittel"],				#broth
		   [u"Gemüsebouillon",u"Bouillon, Gemüse-",u"Lebensmittel"],		#vegetable broth
    		   [u"Hühnerbouillon",u"Bouillon, Hühner-",u"Lebensmittel"],		#broth, chicken
                   [u"Hollandaise",u"Hollandaise",u"Lebensmittel"],			#hollandais sauce

                   [u"gehackte Tomaten",u"Tomaten, gehackt",u"Lebensmittel"],		#chopped tomato
                   [u"geschälte Tomaten",u"Tomaten, geschält",u"Lebensmittel"],		#peeled tomato
                   [u"passierte Tomaten",u"Tomaten, passiert",u"Lebensmittel"],		#mashed tomato
                   [u"Tomatenmark",u"Tomatenmark",u"Lebensmittel"],			#pureed tomato

                   [u"Kekse",u"Kekse",u"Lebensmittel"],					#biscuits
                   [u"Müsli",u"Müsli",u"Lebensmittel"],					#muesli
                   [u"Pudding",u"Pudding",u"Lebensmittel"],				#instant custard pudding
		   [u"Stärke",u"Stärke",u"Lebensmittel"],					#corn starch

		   ## R e i s   u n d   T e i g w a r e n
                   [u"Nudeln",u"Nudeln",u"Reis & Teigwaren"],				#pasta
                   [u"Spaghetti",u"Spagghetti",u"Reis & Teigwaren"],			#spaghetti
                   [u"Penne",u"Penne",u"Reis & Teigwaren"],				#pasta tubes
                   [u"Canelonni",u"Canelonni",u"Reis & Teigwaren"],			#
                   [u"Fusilli",u"Fusilli",u"Reis & Teigwaren"],				#pasta twirls
                   [u"Riccioli",u"Riccioli",u"Reis & Teigwaren"],				#pasta twirls
                   [u"Lasagna",u"Lasagna",u"Reis & Teigwaren"],				#pasta sheets
		   [u"Vermicelli",u"Vermicelli",u"Reis & Teigwaren"],			#vermicelli

                   [u"Teig",u"Teig",u"Reis & Teigwaren"],					#dough
		   [u"Hefeteig", u"Teig, Hefe-",u"Reis & Teigwaren"],			#pastry dough
                   [u"Pizzateig",u"Teig, Pizza-",u"Reis & Teigwaren"],			#pizza dough

                   [u"Langkornreis",u"Reis, Langkorn-",u"Reis & Teigwaren"],		#rice longcorn
                   [u"Basmatireis",u"Reis, Basmati-",u"Reis & Teigwaren"],		#basmati rice
                   [u"Milchreis",u"Reis, Milch-",u"Reis & Teigwaren"],			#pudding rice
                   [u"Naturreis",u"Reis, Natur-",u"Reis & Teigwaren"],			#whole rice
                   [u"Wildreis",u"Reis, Wild-",u"Reis & Teigwaren"],			#wild (black) rice
                   [u"Spitzenlangkornreis",u"Reis, Spitzenlangkorn-",u"Reis & Teigwaren"],	#rice longcorn cook

                   ## B r o t
                   [u"Brot",u"Brot, allgemeines",u"Brot"],				#bread, any
                   [u"Weißbrot",u"Brot, weiß",u"Brot"],					#white bread
                   [u"Toastbrot",u"Brot, Toast-",u"Brot"],					#sliced white toasting bread
                   [u"Vollkornbrot",u"Brot, Vollkorn-",u"Brot"],				#wholemeal bread
                   [u"Sonnenblumenkernbrot",u"Brot, Sonnenblumenkern-",u"Brot"],		#sunflower seed wholmeal
                   [u"Kürbiskernbrot",u"Brot, Kürbiskern-",u"Brot"],			#pupkin seed wholemeal
                   [u"Sesambrot",u"Brot, Sesam-",u"Brot"],				#sesame seed wholemeal
                   [u"Dreikornbrot",u"Brot, Dreikorn-",u"Brot"],				#3 corn wholemeal bread
                   [u"Krustenbrot",u"Brot, Krusten-",u"Brot"],				#Crusty wholemeal bread
                   [u"Landbrot",u"Brot, Land-",u"Brot"],					#wholemeal bread
                   [u"Fladenbrot",u"Brot, Fladen-",u"Brot"],				#turkish round bread
                   [u"Pumpernickel",u"Pumpernickel",u"Brot"],				#pumpernickel bread


		   ## K r ä u t e r   u n d   G e w ü r z e
                   [u"Kräuter",u"Kräuter, gemischt",u"Gemüse"],				#mixed herbs
                   [u"Petersilie",u"Petersilie",u"Gemüse"],				#parsley
                   [u"schwarze Pfeffer",u"Pfeffer schwarz",u"Kräuter u Gewürze"],		#black pepper
                   [u"Cayennepfeffer",u"Pfeffer, Cayenne",u"Kräuter u Gewürze"],           #cayenne
                   [u"Kräuter de Provence",u"Kräuter de Provence",u"Kräuter u Gewürze"],   #Herbs de Provence
                   [u"Kräutersalz",u"Kräutersalz",u"Kräuter u Gewürze"],                   #Herbed salt
                   [u"Lorbeerblatt",u"Lorbeerblatt",u"Kräuter u Gewürze"],                 #Bay leaf
                   [u"Gewürznelken",u"Gewürznelken",u"Kräuter u Gewürze"],                 #
                   [u"Chilipulver",u"Chilipulver",u"Kräuter u Gewürze"],			#(modifier?)
                   [u"Curry",u"Curry",u"Kräuter u Gewürze"],				#curry powder
                   [u"Currypaste",u"Currypaste",u"Kräuter u Gewürze"],			#curry paste
                   [u"Madras Curry",u"Curry, madras",u"Kräuter u Gewürze"],		#hotter curry powder
                   [u"Garam Masala",u"Garam Masala",u"Kräuter u Gewürze"],		#
                   [u"Zimtschote",u"Zimt, Zimtschote",u"Kräuter u Gewürze"],		#(modifier?)
                   [u"gemahlener Zimt",u"Zimt, gemahlener",u"Kräuter u Gewürze"],		#(modifier?)
                   [u"Korianderkerne",u"Korianderkerne",u"Kräuter u Gewürze"],		#(modifier?)
                   [u"gemahlener Koriander",u"Koriander, gemahlener",u"Kräuter u Gewürze"],#(modifier?)
                   [u"Cuminkerne",u"Cuminkerne",u"Kräuter u Gewürze"],			#(modifier?)
                   [u"gemahlener Cumin",u"Cumin, gemahlener",u"Kräuter u Gewürze"],	#(modifier?)
                   [u"Senfkerne",u"Senfkerne",u"Kräuter u Gewürze"],			#(modifier?)
                   [u"Senf",u"Senf",u"Kräuter u Gewürze"],					#(modifier?)
                   [u"Dijon-Senf",u"Senf, Dijon",u"Kräuter u Gewürze"],			#(modifier?)
                   [u"Muskatnuss",u"Muskatnuss",u"Kräuter u Gewürze"],			#nutmeg
                   [u"Paprika, gemahlen",u"Paprika, gemahlen",u"Kräuter u Gewürze"],	#
                   [u"Ingwerpulver",u"Ingwer, Ingwerpulver",u"Kräuter u Gewürze"],		#ground ginger
                   [u"Kurkuma",u"Kurkuma",u"Kräuter u Gewürze"],				#turmeric, curcuma
                   [u"Majoran",u"Majoran",u"Kräuter u Gewürze"],				#turmeric, curcuma
                   [u"Oregano",u"Oregano",u"Kräuter u Gewürze"],				#oregano
                   [u"Basilikum, gerebelt",u"Basilikum, gerebelt",u"Kräuter u Gewürze"],	#basil, crushed
                   [u"frisches Basilikum",u"Basilikum, frisches",u"Kräuter u Gewürze"],	#fresh basil leaves
                   [u"frischer Koriander",u"Koriander, frischer",u"Kräuter u Gewürze"],	#fresh coriander leaves
                   [u"frisches Schnittlauch",u"Schnittlauch, frisches",u"Kräuter u Gewürze"],	#fresh chives
                   [u"frischer Ingwer",u"Ingwer, frischer",u"Kräuter u Gewürze"],		#fresh ginger
                   [u"Ingwerpaste",u"Ingwerpaste",u"Kräuter u Gewürze"],			#ginger paste


		   ## M a r m e l a d e
		   [u"Pflaumenmarmelade",u"Marmelade, Pflaumen-",u"Konfitüren"],		#plum jam
		   [u"Aprikosenmarmelade",u"Marmelade, Aprikosen-",u"Konfitüren"],	#apricot jam
		   [u"Orangenmamalade",u"Marmalade, Orangen-",u"Konfitüren"],		#orange jam
		   [u"Marmelade",u"Marmelade",u"Konfitüren"],				#jam - general
		   [u"Erdbeermarmelade",u"Marmelade, Erdbeer-",u"Konfitüren"],		#strawberry jam
		   [u"Himbeermarmelade",u"Marmelade, Himbeer-",u"Konfitüren"],		#raspberry jam
		   [u"Erdnussbutter",u"Erdnussbutter",u"Konfitüren"],			#peanut butter
		   [u"Nutella",u"Nutella",u"Konfitüren"],					#nussply
		   [u"Sesammus",u"Sesammus",u"Konfitüren"],				#tahini - sesame spread
                   [u"Honig",u"Honig",u"Konfitüren"],					#honey

		   ## I n t e r n a t i o n a l
                   [u"Tartex",u"Tartex",u"International"],					#tartex spread
                   [u"Kokosmilch",u"Kokusmilch",u"International"],			#coconut milk
                   [u"Kokoscreme",u"Kokuscreme",u"International"],			#coconut cream
                   [u"grüne Currypaste",u"Currypaste, grüne",u"International"],		#green curry paste
                   [u"rote Currypaste",u"Currypaste, rote",u"International"],		#red curry paste
                   [u"Reisessig",u"Essig, Reis-",u"International"],			#rice vinegar
                   [u"Salsa",u"Salsa",u"International"],					#salsam
                   [u"Sesamkerne",u"Sesamkerne",u"International"],			#sesame seeds
                   [u"Soja-Sauce",u"Soja-Sauce",u"International"],				#soy sauce
                   [u"Sojacreme",u"Sojacreme",u"International"],		                #soya cream
		   [u"Bulgur",u"Bulgur",u"International"],					#bulgar
                   [u"Couscous",u"Couscous",u"International"],				#couscous
                   [u"Falafel",u"Falafel",u"International"],				#felafel
                   [u"Tofu",u"Tofu",u"International"],					#tofu
                   [u"Pak-choï",u"Pak-choï",u"Gemüse"],					#bok choy
	
		   ## M i l c h p r o d u k t e
                   [u"Milch",u"Milch",u"Milchprodukte"],					#milk, unspecified
                   [u"Käse",u"Käse, allgemeiner",u"Milchprodukte"],			#cheese, any
                   [u"Butter",u"Butter",u"Milchprodukte"],					#butter
                   [u"Margarine",u"Margarine",u"Milchprodukte"],				#	
                   [u"Eier",u"Eier",u"Milchprodukte"],					#egg
                   [u"frische Milch",u"Milch, frische",u"Milchprodukte"],			#milk
                   [u"fettarme Milch",u"Milch, fettarme",u"Milchprodukte"],		#skimmed milk
		   [u"H-Milch",u"Milch, H-Milch",u"Milchprodukte"],			#long-life milk
		   [u"Sojamilch",u"Milch, Sojamilch", u"Milchprodukte"],			#soya milk
		   [u"Buttermilch",u"Milch, Buttermilch",u"Milchprodukte"],		#buttermilk
                   [u"Sauerrahm",u"Sauerrahm",u"Milchprodukte"],				#sour cream
		   [u"Sahne",u"Sahne",u"Milchprodukte"],					#
		   [u"Sahne 10% Fett",u"Sahne, 10% Fett",u"Milchprodukte"],		#
		   [u"Sahne 15% Fett",u"Sahne, 15% Fett",u"Milchprodukte"],		#
		   [u"Sahne 35% Fett",u"Sahne, 35% Fett",u"Milchprodukte"],		#
                   [u"Joghurt",u"Joghurt",u"Milchprodukte"],				#yogurt
		   [u"Quark",u"Quark",u"Milchprodukte"],					#
		   [u"Speisequark Magerstufe",u"Quark, Speise- Magerstufe",u"Milchprodukte"],	#
		   [u"Kräuterquark",u"Quark, Kräuter",u"Milchprodukte"],			#
                   [u"Cheddar-Käse",u"Käse, Cheddar",u"Milchprodukte"],			#cheddar cheese
                   [u"Hartkäse",u"Käse, Hart-",u"Milchprodukte"],				#general hard cheese
                   [u"Hüttenkäse",u"Käse, Hüttenkäse",u"Milchprodukte"],			#cottage cheese
                   [u"Schnittkäse",u"Käse, Schnittkäse",u"Milchprodukte"],			#cottage cheese
                   [u"Fetakäse",u"Käse, Fetakäse",u"Milchprodukte"],			#feta cheese
                   [u"Ziegenkäse",u"Käse, Ziegenkäse",u"Milchprodukte"],			#fresh cheese white goat
                   [u"Schaffskäse",u"Schaffskäse",u"Milchprodukte"],			#sheeps cheese
                   [u"Emmentaler",u"Käse, Emmentalerkäse",u"Milchprodukte"],		#emmental
                   [u"Mozzarella",u"Käse, Mozzarella",u"Milchprodukte"],			#mozzarella cheese
                   [u"Parmesan",u"Käse, Parmesan",u"Milchprodukte"],			#parmesan cheese
                   [u"Provolone",u"Käse, Provolone",u"Milchprodukte"],			#provolone cheese
                   [u"Ricotta",u"Käse, Ricotta",u"Milchprodukte"],				#ricotta cheese
                   [u"Gouda",u"Käse, Gouda",u"Milchprodukte"],				#cheese Gouda
                   [u"Brie",u"Käse, Brie",u"Milchprodukte"],				#cheese Brie
                   [u"Streichkäse",u"Käse, Steich",u"Milchprodukte"],			#spreading cheese
                   [u"Philladelphia",u"Käse, Philladelphia",u"Milchprodukte"],		#philladelphia cheese


		   ## h e i ß e   G e t r ä n k e
                   [u"schwarzer Tee",u"Tee, schwarzer",u"Getränke, heiß"],			#black tea
                   [u"gemahlener Kaffee, ",u"Kaffee, gemahlener",u"Getränke, heiß"],	#ground coffee
                   [u"gemahler entkoffeinierter Kaffee",u"Kaffee, gemahlener entkoffeinierter",u"Getränke, heiß"],	#decaff ground coffee
                   [u"Kaffeefilter",u"Kaffeefilter",u"Getränke, heiß"],			#coffee filters
                   [u"Kakao",u"Kakao",u"Getränke, heiß"],					#drinking chocolate
                   [u"Carokaffee",u"Carokaffee",u"Getränke, heiß"],			#caro coffee
                   [u"Früchtetee, ",u"Tee, Früchtetee",u"Getränke, heiß"],			#fruit tea
                   [u"Pfefferminztee",u"Tee, Pfefferminztee",u"Getränke, heiß"],		#peppermint tea
                   [u"Hagebuttentee",u"Tee, Hagebuttentee",u"Getränke, heiß"],		#rosehip tea
                   [u"Kamillentee",u"Tee, Kamillentee",u"Getränke, heiß"],		#camomile tea
                   [u"Fencheltee",u"Tee, Fencheltee",u"Getränke, heiß"],			#fenchel tea
                   [u"Rotbuschtee",u"Tee, Rotbuschtee",u"Getränke, heiß"],			#roobusch tea
                   [u"Kräutertee",u"Tee, Kräutertee",u"Getränke, heiß"],			#herb tea
                   [u"grüner Tee",u"Tee, grüner",u"Getränke, heiß"],			#green tea
                   [u"Yogitee",u"Tee, Yogitee",u"Getränke, heiß"],				#yogi (ayurvedic) tea

		   ## F l u ß i g k e i t e n
                   [u"Tafelessig",u"Essig, Tafel-",u"Flüssigkeiten"],			#table vinegar
                   [u"Obstessig",u"Essig, Obst-",u"Flüssigkeiten"],			#table vinegar
                   [u"Balsamico-Essig",u"Essig, Balsamico-",u"Flüssigkeiten"],		#balsamic vinegar
                   [u"Sonnenblumenöl",u"Öl, Sonnenblumenöl",u"Flüssigkeiten"],		#sunflower oil
                   [u"Olivenöl",u"Öl, Olivenöl",u"Flüssigkeiten"],				#olive oil
                   [u"Sesamöl",u"Öl, Sesamöl",u"Flüssigkeiten"],				#sesame oil
                   [u"Pflanzenöl",u"Öl, Pflanzenöl",u"Flüssigkeiten"],			#vegetable oil
		   [u"Sojaöl",u"Öl, Sojaöl",u"Flüssigkeiten"],				#soya oil
                   [u"Weißwein",u"Wein, weiß",u"Flüssigkeiten"],				#white wine
                   [u"Rotwein",u"Wein, rot",u"Flüssigkeiten"],				#red wine

                   ## t h i n g   y o u   s h o u l d   h a v e   a t   h o m e 
                   [u"Wasser",u"Wasser",u"Flüssigkeiten"]					#water

                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
# Each unit is of the following format:
# (u"unit1",u"unit2"):conversion_factor, where unit1 contains conversion_factor X unit2
# For example: 1 cup has 16 tablespoons.
CONVERTER_TABLE = {
    (u"Tasse", u"EL"):16,
    (u"EL", u"TL"):3,
    (u"pt.", u"Tasse"):2,
    (u"qt.", u"Tasse"):4,
    (u"l", u"ml"):1000,
    (u"l", u"cl"):100,
    (u"l", u"dl"):10,
    (u"oz.", u"g"):28.35,
    (u"kg", u"g"):1000,
    (u"g", u"mg"):1000,
    (u"TL", u"Tröpchen"):76,
    (u"Dose, mittel", u"g"):400,
    (u"Dose, groß",   u"g"):800,
    (u"Dose, klein",  u"g"):200,
    (u"lb.", u"oz."):16,
    (u"l", u"qt."):1.057
}


# DENSITIES of common foods. This allows us to convert between mass and volume.
# Translators: You may be best off translating the food names below, since lists
# of food densities can be hard to come by!
DENSITY_TABLE={
    u"Wasser":1,				#water
    u"Traubensaft":1.03,			#juice, grape
    u"Bouillon, gemüse":1,		#vegetable broth
    u"Bouillon, hühner":1,		#broth, chicken
    u"Milch":1.029,			#milk
    u"Milch entier":1.029,		#milk, whole
    u"Milch, fettarm":1.033,		#milk, skim
    u"Milch 2%":1.031,			#milk, 2%
    u"Milch 1%":1.03,			#milk, 1%
    u"Kokosmilch":0.875,		#coconut milk
    u"Buttermilch":1.03,		#buttermilk
    u"Sahne riche":0.994,		#heavy cream
    u"Sahne légère":1.012,		#light cream
    u"Sahne 11,5%":1.025,		#half-and-half
    u"Honig":1.420,			#honey
    u"Zucker":1.550,			#sugar, white
    u"Salz":2.165,			#salt
    u"Butter":0.911,			#butter
    u"Pflanzen Öl":0.88,			#oil, vegetable
    u"Oliven Öl":0.88,			#oil, olive
    u"Sonnenblumen Öl":0.88,		#oil, corn
    u"Sesam Öl":0.88,			#oil, sesame
    u"Mehl": 0.6,			#flour, all purpose
    u"Vollkornmehl": 0.6,		#flour, whole wheat
    u"Stärke": 0.6,			#corn starch
    u"Zucker en poudre": 0.6,		#sugar, powdered
    u"Zucker glace": 0.6			#sugar, confectioners
      }

### ORIGINAL TABLES FROM ENGLISH

# Standard unit names and alternate unit names that might appear.  For
# example: u"c." is our standard abbreviation for cup.  u"cup",u"c." or
# u"cups" might appear in a recipe we are importing.  Each item of this
# list looks like this:
#
# [u"standard", [u"alternate1",u"alternate2",u"alternate3",...]]
#
# The first item should be the preferred abbreviation
# The second item should be the full name of the unit
# e.g. [u"c.", [u"cup",...]]
#
UNITS = [
         [u"ml", [u"Milliliter",u"milliliter",u"Milliliters",u"milliliters",u"ml", u"ml."]],
         [u"cl", [u"Centiliter",u"centiliter",u"Centiliters",u"centiliters",u"cl", u"cl."]],
         [u"dl", [u"Deciliter",u"deciliter",u"Deciliters",u"deciliters",u"dl", u"dl."]],
         [u"l", [u"Liter",u"Liters",u"liter",u"liters",u"l.", u"lit.", u"l"]],

         [u"g", [u"Gramm",u"Gramme",u"gramm", u"gramme", u"g.",u"g",u"gram",u"grams"]],
         [u"mg", [u"Milligramm",u"milligramm",u"Milligramme",u"milligramme",u"mg.", u"mg",u"milligram",u"milligrams"]],
         [u"kg", [u"Kilogramm",u"kilogramm",u"Kilogramme",u"kilogramme",u"kg.", u"kg",u"kilogram",u"kilograms"]],

         [u"cm", [u"Centimeter",u"centimeter",u"Centimeters",u"centimeters",u"cm", u"cm."]],
         [u"mm", [u"Millimeter",u"millimeter",u"Millimeters",u"millimeters",u"mm", u"mm."]],
         [u"m", [u"Meter",u"meter",u"Meters",u"meters",u"m", u"m."]],

         [u"Tröpfchen",[u"Tröpfchen",u"tröpfchen",u"troepfchen",u"Troepfchen",u"drop",u"drops"]],
         [u"TL", [u"Teelöffel",u"Teelöffeln",u"teelöffel",u"teelöffeln",u"tl",u"TL",u"tsp", u"tsp.",u"tea spoon", u"teaspoon"]],
         [u"EL", [u"Esslöffel",u"Esslöffeln",u"esslöffel",u"esslöffeln",u"el",u"EL",u"tbs", u"tbsp", u"tbs.", u"tbsp.", u"table spoon",u"tablespoon"]],
         [u"Tasse", [u"Tasse",u"Tassen",u"tasse",u"tassen",u"cup", u"c.", u"cups",u"Glas",u"glas", u"Glass", u"glass"]],
	 [u"Becher", [u"Becher",u"becher"]],

         [u"St.", [u"St.",u"Stück",u"Stücke",u"Stueck",u"Stuecke",u"Mal",u"stück",u"stücke",u"stueck",u"stuecke", u"mal",u"piece", u"pieces",u"St",u"st"]],
         [u"Dose, mittel", [u"Dose, mittel",u"dose, mittel",u"mittlere Dose",u"mittlere dose"]],
         [u"Dose, groß", [u"Dose, groß", u"dose, groß",u"größe Dose",u"größe dose"]],
         [u"Dose, klein", [u"Dose, klein",u"dose, klein",u"kleine Dose",u"kleine dose"]],
	 [u"Zeh", [u"Zeh",u"Zehen",u"zeh",u"zehen"]],           #garlic
	 [u"Paket",[u"Paket",u"Pakete",u"paket",u"pakete", u"Packung", u"packung", u"pack"]],
	 [u"Prise",[u"Prise",u"Prisen",u"prise",u"prisen"]],    #pinch
	 [u"Bund",[u"Bund",u"Bunde",u"bund",u"bunde"]],         #bunch

         [u"lb.", [u"Pfund",u"pfund",u"pound",u"pounds",u"lb",u"lb.", u"lbs."]],
         [u"oz.", [ u"ounce",u"ounces",u"oz",u"oz."]],
         [u"qt.", [u"quart", u"qt.", u"quarts"]],
         [u"pt.", [u"pint", u"pt.", u"pints"]],
         [u"gallon", [u"gallon", u"gallons",u"gal."]]

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
    'imperial weight':[('oz.',(0.25,32)),
                       ('lb.',(0.25,None)),
                       ],
    'imperial volume':[('Tröpfchen',(0,3)),
                       ('TL',(0.125,3)),
                       ('EL',(1,4)),
                       ('Tasse',(0.25,6)),
                       ('pt.',(1,1)),
                       ('qt.',(1,3))]
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
    (u"pt.", u"lb."):['density',1],
    (u"EL", u"oz."):['density',0.5],
    (u"Tasse", u"oz."):['density',8],
    (u"l", u"kg"):['density',1],
    (u"ml", u"g"):['density',1]
    }

# The units here need to correspond to the standard unit names defined
# in UNITS.  These are some core conversions from mass-to-volume,
# assuming a density of 1 (i.e. the density of water).
VOL_TO_MASS_TABLE = {
    (u"pt.", u"lb.") : 1,
    (u"tbs.", u"oz.") : 0.5,
    (u"c.", u"oz.") : 8,
    (u"pt.", u"oz.") : 16,
    (u"ml", u"g") : 1,
    (u"ml", u"mg") : 1000,
    (u"ml", u"kg"): 0.001,
    (u"cl", u"kg"): 0.01,
    (u"cl", u"g") : 10,
    (u"dl", u"kg") : 0.1,
    (u"dl", u"g") : 100,    
    (u"l", u"kg") : 1
    }

### From translator :
### FRENCH PART TO BE REVISED !!! US units != UK units != Canadian units !!!
### I will work on these later... 
# VOL_TO_MASS_TABLE = {
#     (u"chop",u"lb") : 1,					#(warning, might not be accurate, see below)
#     (u"c. à table",u"oz") : 0.5,
#     (u"tasse",u"oz") : 8,
#     (u"chop",u"oz") : 20,					#(warning, modified, see u"chopine" in granddictionnaire)
#     (u"ml",u"g") : 1,
#     (u"ml",u"mg") : 1000,
#     (u"ml",u"kg"): 0.001,
#     (u"cl",u"kg"): 0.01,
#     (u"cl",u"g") : 10,
#     (u"dl",u"kg") : 0.1,
#     (u"dl",u"g") : 100,    
#     (u"l",u"kg") : 1}

# TIME ABBREVIATIONS (this is new!)
TIME_ABBREVIATIONS = {
    'sec':'Sek.',
    'min':'Min.',
    'hr':'Std.'
    }

IGNORE = [u"und",u"mit",u"von",u"für",
          u"kalt",u"kalter",u"kalte",u"kaltes",u"kalten",
          u"warm",u"warmer",u"warme",u"warmes",u"warmen",
          u"dünn",u"dünner",u"dünne",u"dünnes",u"dünnen",
          u"dick",u"dicker",u"dicke",u"dickes",u"dicken"
          ]

NUMBERS = {
    }
                    
# These functions are rather important! Our goal is simply to
# facilitate look ups -- if the user types in u"tomatoes", we want to
# find "tomato." Note that the strings these functions produce will
# _never_ be shown to the user, so it's fine to generate nonsense
# words as well as correct answers -- our goal is to generate a list
# of possible hits rather than to get the plural/singular form "right".

def guess_singulars (s):
    # Note - German, here we're not only going to try to make nouns singular,
    # we could also get an adjective, so lets also take the adjectival endings off
    if len(s)<3: return []
    ret = []
    if s[-1]=='n':
        if s[-2]=='e':
            ret.append(s[0:-2]) # try chopping off 'en'
        if (s[-2]!='u') & (s[-2]!='o') & (s[-2]!='a') & (s[-2]!='i'):
            ret.append(s[0:-1]) # try chopping off the n

    if s[-1]=='s':
        ret.append(s[0:-1]) # try chopping off the s
        if s[-2]=='e':
            ret.append(s[0:-2]) # try chopping off 'es'

    if s[-1]=='e':
        ret.append(s[0:-1]) # try chopping off the 'e'

    if (s[-1]=='r') & (s[-2]=='e'):
        ret.append(s[0:-2]) # try chopping off the 'er'
    
    return ret

def guess_plurals (s): 
    # Ditto above, assume this could also be an adjective, so try adding the common agreements
    return [s+'n', s+'en', s+'e', s+'er', s+'s', s+'es']

