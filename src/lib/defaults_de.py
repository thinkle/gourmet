#!/usr/bin/python
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

CREDITS = ""

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

fields={'cuisine': ['deutsch', 'amerikanisch','italienisch','franzoisisch',
		    'mexicanisch','asiatisch','griechisch','vegetarisch'],

        'rating' : ['5 - ausgezeichnet','4 - lecker',
		    '3 - OK','2 - mittelmässig','1 - vergiss es!',
                    '(nicht geprüft)'],

        'source' : [],

        'category' :[
		     'Nachspeise','Vorspeise','Hauptgericht',
		     'Beilage','Salat','Suppe','Frühstuck',
		     'Picnik','Andere','Plan'],
                  }

# In English, there are a heck of a lot of synonyms. This is a list
# for those synonyms.  ["preferred word","alternate word","alternate word"]
# If there are none of these that you can think of in your language, just
# set this to:
# SYNONYMS=[]

# note from translator: some terms are not standard but used in common langugage, some are used in a fautive manner, 
# I decided to put them in different sections so it is still clear what is a synonym and what should not be a synonym.
SYNONYMS=[
    # the first item of each list is the default
    ["Cocktailtomaten", "Tomaten, cherry"],
    ["Alfaalfa","Alfapha","Luzerne"],
    ["Porree","Lauch"],
    ["Frühlingszwiebel","Lauch-Zwiebeln"],
    ["Zuckermelone","Gartenmelone"],
    ["Bleichsellerie","Stangensellerie", "Straudensellerie"],
    ["Hammelfleisch","Hammel"],
    ["Kalbfleisch","Kalb"],
    ["Truthahn","Puter","Pute"],
    ["Rindfleisch","Rind"],
    ["Rotbusch","Roobusch","Roibusch"],
    ["Seelachs","Köhler"],
    ["Anschovis","Anchovis","Sardelle"],
    ["Kabeljau","Dorsch"],
    ["Nutella", "Nusspli"],
    ["Tomatenmark","Tomatenkonzentrat"],
    ["Weizenmehl","Mehl, weiß"],
    ["Soja-Milch","Sojamilch","Soya-Milch", "Soja Milch"],
    ["Soja-Sauce", "sauce soja","sauce soya","Soya-Sauce","Sojasoße", "Sojasosse"],
    ["Soja","Soya"], 
    ["Sojabohnen","Soyabohnen"], 
    ["Püree","Kartoffelpüree"],
    ["Müsli","Muesli"],
    ["Nudeln","Pasta"],
    ["Chile","Chili","Chilli"],
    ["Zucchini", "Zuchini", "Courgette"],
    ["Tafeltrauben","Trauben, weiß","Trauben, grün"],
    ["Garam Masala","Masala","Massala","Garam Massala"],
    ["Gemüsebouillon","Gemüsebrühe"],
    ["Hühnerbouillon","Hühnerbrühe"],
    ["Muskat","Muskatnuss","Muscat","Muscatnuss"],
    ["Sesamus","Tahin"],
    ["Brokkoli", "Broccoli"], 
    ["Kräuter","gemischte Kräuter"],
    ["Langkornreis","Reis"],

    # Irregular plurals
    ["Äpfeln","Apfel"],
    ["Pfirsiche", "Pfirsich"],
    ["Nüsse","Nüße","Nuss","Nuß", "Nusse", "Nuße"],
    ["Eier", "Ei"]

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
    'Sellerie':['Sellerie','Straudensellerie'],
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
# "knows" about foods that they enter.

# I generated the below list using the wikipedia entry on foods as my
# starting point. You may want to do something similar for your
# locale.  Also, if the syntax of the below is too complicated, you
# can send me a list of category headings and ingredients for your
# locale and I'll do the necessary formatting <Thomas_Hinkle@alumni.brown.edu>

INGREDIENT_DATA = [  ## G e m ü s e  
		   ["Alfaalfa","Alfalfa","Gemüse"],                 			#alfalfa sprouts
                   ["Anis","Anis","Gemüse"],                       			#anise
                   ["Artischocke","Artischocke","Gemüse"],				#artichoke
                   ["Ölranke","Ölranke","Gemüse"],					#rocket
                   ["Spargel","Spargel","Gemüse"],					#asparagus (white)
                   ["weißer Spargel","Spargel, weißer","Gemüse"],			#asparagus - white
                   ["grüner Spargel","Spargel, grüner","Gemüse"],			#asparagus - green
                   ["Aubergine","Aubergine","Gemüse"],					#aubergine
                   ["Avocado","Avocado","Gemüse"],					#avocado
                   ["Brokkoli","Brokkoli","Gemüse"],					#broccoli
	           ["Spinat","Spinat","Gemüse"],					#spinach
                   ["Rosenkohl","Kohl, Rosenkohl","Gemüse"],				#brussels sprouts
                   ["Kohl","Kohl","Gemüse"],						#cabbage
                   ["Weißkohl","Kohl, Weißkohl","Gemüse"],				#white cabbage
                   ["Rotkohl","Kohl, Rotkohl","Gemüse"],				#red cabbage
                   ["Blumenkohl","Kohl, Blumenkohl","Gemüse"],				#cauliflower
                   ["Chinakohl","Kohl, Chinakohl","Gemüse"],				#china cabbage
                   ["Kohlrabi","Kohl, Kohlrabi","Gemüse"],				#kohlrabi
                   ["Grünkohl","Kohl, Grünkohl","Gemüse"],				#kale

                   ["Bleichsellerie","Bleichsellerie","Gemüse"],			#celery
                   ["Zitronengras","Zitronengras","Gemüse"],				#lemon grass
                   ["Mais","Mais","Gemüse"],						#corn

                   ["Champignons","Champignons","Gemüse"],				#button mushrooms
                   ["Pilze","Pilze","Gemüse"],						#large mushrooms
                   ["Steinpilz","Steinpilze","Gemüse"],				#mushrooms
		   ["Pfifferlinge","Pfifferlinge","Gemüse"],				#other woodland fungus

                   ["Senfkeimlinge","Senfkeimlinge","Gemüse"],				#mustard greens
                   ["Brennessel","Brennessel","Gemüse"],				#nettles
                   ["Okra","Okra","Gemüse"],						#okra
                   ["Schnittlauch","Schnittlauch","Gemüse"],				#chives

                   ["Zwiebeln","Zwiebeln","Gemüse"],					#onion
                   ["Schalotte","Schalotte","Gemüse"],					#shallot
                   ["Frühlingszwiebel","Frühlingszwiebel","Gemüse"],			#spring onion, scallion
                   ["rote Zwiebeln, rot","Zwiebeln, rote","Gemüse"],			#red (spanish) onion
                   ["weiße Zwiebeln","Zwiebeln, weiße","Gemüse"],			#white onion
                   ["gelbe Zwiebeln","Zwiebeln, gelbe","Gemüse"],			#yellow onion
                   ["Metzgerzwiebeln","Zwiebeln, Metzger-","Gemüse"],			#large onion (salad)
                   ["Speisezwiebeln","Zwiebeln, Speise-","Gemüse"],			#standard cooking onion
                   ["Knoblauch","Knoblauch","Gemüse"],					#garlic
                   ["Porree","Porree","Gemüse"],					#leek

                   ["Paprika","Paprika","Gemüse"],					#pepper
                   ["rote Paprika","Paprika, rote","Gemüse"],				#red bell pepper
                   ["grüne Paprika","Paprika, grüne","Gemüse"],				#
                   ["gelbe Paprika","Paprika, gelbe","Gemüse"],				#
                   ["Chile","Chile","Gemüse"],						#chilli pepper
                   ["Jalapeño-Chile","Chile, Jalapeño","Gemüse"],			#jalapeño pepper
                   ["Habanero-Chile","Chile, Habanero","Gemüse"],			#habanero pepper

                   ["Radieschen","Radieschen","Gemüse"],				#radish
                   ["Rote Beet","Rote Beet","Gemüse"],					#beetroot
                   ["Möhren","Möhren","Gemüse"],					#carrot
	           ["Rettich","Rettich","Gemüse"],					#horse radish
                   ["Wasabi","Wasabi","Gemüse"],					#japanese horseraddish
                   ["Sellerie","Sellerie","Gemüse"],					#celeriac
                   ["Pastinake","Pastinake","Gemüse"],					#parsnip
                   ["Kohlrübe","Kohlrübe","Gemüse"],					#turnip
                   ["Fenchel","Fenchel","Gemüse"],					#fennel

                   ["Kopfsalat","Kopfsalat","Gemüse"],					#lettuce 
                   ["Rucolasalat","Rucolasalat","Gemüse"],				#rucola 
                   ["Friseesalat","Friseesalat","Gemüse"],				#open lettuce 
                   ["Feldsalat","Feldesalat","Gemüse"],					#lettuce 

                   ["Saubohnen","Saubohnen","Gemüse"],					#broad beans
                   ["Bobby Bohnen","Bobby Bohnen","Gemüse"],				#small green beans
                   ["Haricots","Haricots","Gemüse"],					#haricot beans
                   ["Carbasc","Carbasc","Gemüse"],					#runner beans
                   ["Erbsen","Erbsen","Gemüse"],					#peas
                   ["Zuckererbsen","Zuckererbsen","Gemüse"],				#mange tous

                   ["Zucchini","Zucchini","Gemüse"],					#zucchini
                   ["Gurke (Salat-)","Gurke (Salat-)","Gemüse"],			#cucumber

                   ["Kürbis","Kürbis","Gemüse"],					#pumpkin

                   ["Cocktailtomaten","Tomaten, Cocktail-","Gemüse"],			#cocktail (cherry) tomato
                   ["Tomaten","Tomaten","Gemüse"],					#cherry tomato
                   ["Rispentomaten","Tomaten, Rispen-","Gemüse"],			#tomato on stems

                   ["Kartoffel","Kartoffel","Gemüse"],					#potato
                   ["Speisekartoffeln","Kartoffeln, Speise-","Gemüse"],			#standard cooking potatoes
                   ["Süßkartoffel","Süßkartoffel","Gemüse"],				#sweet potato

                   ["Jamswurzel","Jamswurzel","Gemüse"],				#yam
                   ["Kastanien","Kastanien","Gemüse"],					#water chestnut
                   ["Brunnenkresse","Brunnenkresse","Gemüse"],				#watercress

                   ["Oliven","Oliven","Gemüse"],					#
                   ["grüne Oliven","Oliven, grüne","Gemüse"],				#
                   ["schwarze Oliven","Oliven, schwarze","Gemüse"],			#


                   ## H ü l s e n f r u c h t e
                   ["grüne Bohnen","Bohnen, grüne","Gemüse"],				#green beans
                   ["weiße Bohnen","Bohnen, weiße","Hülsenfrüchte"],			#green beans
                   ["Azuki Bohnen","Bohnen, Azuki","Hülsenfrüchte"],			#azuki beans
                   ["schwarze Bohnen","Bohnen, schwarze","Hülsenfrüchte"],		#black beans
                   ["Borlottibohnen","Bohnen, Borlotti-","Hülsenfrüchte"],		#borlotti beans (not sure)
                   ["Kichererbsen","Kichererbsen","Hülsenfrüchte"],			#chickpeas, garbanzos, or ceci beans
                   ["Kidneybohnen","Bohnen, Kidney-","Hülsenfrüchte"],			#kidney beans
                   ["Teller-Linsen","Linsen, Teller-","Hülsenfrüchte"],			#standard lentils
                   ["rote Linsen","Linsen, rote","Hülsenfrüchte"],			#red lentils
                   ["grüne Linsen","Linsen, grüne","Hülsenfrüchte"],			#green lentils
                   ["schwarze Linsen","Linsen, schwarze","Hülsenfrüchte"],		#black lentils
                   ["Gartenbohnen","Gartenbohnen","Gemüse"],				#lima bean or butter bean
                   ["Mungbohnen","Bohnen, Mung-","Hülsenfrüchte"],			#mung beans
                   ["Sojabohnen","Bohnen, Soja-","Hülsenfrüchte"],			#soybeans
                   ["grüne Erbsen","Erbsen, grüne","Hülsenfrüchte"],			#green dried peas
                   ["gelbe Erbsen","Erbsen, gelbe","Hülsenfrüchte"],			#yellow dried peas
                   ["Schälerbsen","Erbsen, Schälerbsen","Hülsenfrüchte"],		#

                   ## F r u c h t e
                   ["Obst","Obst","Obst"],						#general fruit
                   ["Äpfeln","Äpfeln","Obst"],						#apple
                   ["rote Äpfeln","Äpfeln, rote","Obst"],				#
                   ["goldene Äpfel","Äpfeln, goldene","Obst"],				#
                   ["Granny Smith Äpfeln","Äpfel, Granny Smith","Obst"],		#
                   ["Fuji Äpfeln","Äpfeln, Fuji-","Obst"],				#
                   ["grüne Äpfeln","Äpfeln, grüne","Obst"],				#green apple
                   ["Granatapfeln","Granatapfeln","Obst"],				#pomegranate
                   ["Quitte","Quitte","Obst"],						#quince
                   ["Hagebutten","Hagebutten","Obst"],					#rose hip
                   ["Aprikosen","Aprikosen","Obst"],					#apricot
                   ["Birnen","Birnen","Obst"],						#pear
                   ["Conference Birnen","Birnen, Conference","Obst"],			#pear, large conference
                   ["William Birnen","Birnen, William","Obst"],				#pear, standard william
                   ["Kirschen","Kirschen","Obst"],					#cherry
                   ["Pflaumen","Pflaumen","Obst"],					#plum
                   ["Pfirsiche","Pfirsiche","Obst"],					#peach
                   ["Nektarinen","Nektarinen","Obst"],					#nectarine
                   ["Brombeeren","Beeren, Brombeeren","Obst"],				#blackberry
                   ["Himbeeren","Beeren, Himbeeren","Obst"],				#raspberry
                   ["Erdbeeren","Beeren, Erdbeeren","Obst"],				#raspberry
                   ["Heidelbeeren","Beeren, Heidelbeeren","Obst"],			#bilberry
                   ["Blaubeeren","Beeren, Blaubeeren","Obst"],				#blueberry
                   ["Preiselbeeren","Beeren, Preiselbeeren","Obst"],			#cranberry
                   ["Johannisbeeren","Beeren, Johannisbeeren","Obst"],			#red currant
                   ["schwarze Johannisbeeren","Beeren, schwarze Johannisbeeren","Obst"],	#black currant
                   ["Holunderbeeren","Beeren, Holunderbeeren","Obst"],			#elderberry
                   ["Stachelbeeren","Stachelbeeren","Obst"],				#gooseberry
                   ["Kiwi","Kiwi","Obst"],						#kiwi fruit
                   ["Papaya","Papaya","Obst"],						#pawpaw
                   ["Zuckermelonen","Zucker-","Obst"],					#cantaloupe
                   ["Honigmelonen","Melonen, Honig-","Obst"],				#honeydew melon
                   ["Galiamelonen","Melonen, Galia-","Obst"],				#galia melon
                   ["Netzmelonen","Melonen, Netz-","Obst"],				#net melon
                   ["Wassermelonen","Melonen, Wasser-","Obst"],				#watermelon
                   ["Feigen","Feigen","Obst"],						#fig
                   ["Weintrauben","Weintrauben","Obst"],				#grape
                   ["Tafeltrauben","Weintrauben, Tafel","Obst"],			#green grapes
                   ["blaue Weintrauben","Weintrauben, blau","Obst"],			#black grapes
                   ["Datteln","Datteln","Obst"],					#date
                   ["Grapefruit","Grapefruit","Obst"],					#grapefruit
                   ["Limetten","Limetten","Obst"],					#lime
                   ["Kumquat","Kumquat","Obst"],					#kumquat
                   ["Zitronen","Zitronen","Obst"],					#lemon
                   ["Mandarinen","Mandarinen","Obst"],					#mandarin
                   ["Klementinen","Klementinen","Obst"],				#clementine
                   ["Tangerinen","Tangerinen","Obst"],					#tangerine
                   ["Orangen","Orangen","Obst"],					#orange
                   ["Ugli","Ugli","Obst"],						#ugli fruit
                   ["Guave","Guave","Obst"],						#guava
                   ["Litschi","Litschi","Obst"],					#lychee
                   ["Passionsfrucht","Passionsfrucht","Obst"],				#passion fruit
                   ["Banane","Banane","Obst"],						#banana
                   ["Wegerich","Wegerich","Obst"],					#plantain
                   ["Kokosnuss","Kokosnuss","Obst"],					#coconut
                   ["Durion","Durion","Obst"],						#durian
                   ["Mango","Mangue","Obst"],						#mango
                   ["Papaya","Papaya","Obst"],						#papaya
                   ["Ananas","Ananas","Obst"],						#pineapple
                   ["Tamarinde","Tamarinde","Obst"],					#tamarind
                   ["Rahbarber","Rahbarber","Obst"],					#rhubarb
 

                   ## M e e r e s f r ü c h t e
                   ["Anchovis","Anchovis","Meeresfrüchte"],				#anchovy
                   ["Barsch","Barsch","Meeresfrüchte"],					#bass
                   ["Kugelfisch","Kugelfisch","Meeresfrüchte"],				#blowfish
                   ["Wels","Wels","Meeresfrüchte"],					#catfish
                   ["Dorsch","Dorsch","Meeresfrüchte"],					#cod
                   ["Aal","Aal","Meeresfrüchte"],					#eel
                   ["Flunder","Flunder","Meeresfrüchte"],				#flounder
                   ["Schellfisch","Schellfisch","Meeresfrüchte"],			#haddock
                   ["Haddock","Haddock","Meeresfrüchte"],				#smoked haddock
                   ["Heilbutt","Heilbutt","Meeresfrüchte"],				#halibut
                   ["Zander","Zander","Meeresfrüchte"],					#pike
                   ["Seelachs","Seelachs","Meeresfrüchte"],				#pollock
                   ["Sardine","Sardine","Meeresfrüchte"],				#sardine
                   ["Sprotte","Sprotte","Meeresfrüchte"],				#sprat
                   ["Lachs","Lachs","Meeresfrüchte"],					#salmon
                   ["Sägebarsch","Sägebarsch","Meeresfrüchte"],				#sea bass
                   ["Hai","Hai","Meeresfrüchte"],					#shark
                   ["Seezunge","Seezunge","Meeresfrüchte"],				#sole
                   ["Stör","Stör","Meeresfrüchte"],					#sturgeon
                   ["Schwertfisch","Schwertfisch","Meeresfrüchte"],			#swordfish
                   ["Forelle","Forelle","Meeresfrüchte"],				#trout
                   ["Thunfisch","Thunfisch","Meeresfrüchte"],				#tuna
                   ["Weißfisch","Weißfisch","Meeresfrüchte"],				#whitefish
                   ["Wittling","Wittling","Meeresfrüchte"],				#whiting
                   ["Rogen","Rogen","Meeresfrüchte"],					#roe of fish
                   ["Kaviar","Kaviar","Meeresfrüchte"],					#caviar
                   ["Krebs","Krebs","Meeresfrüchte"],					#crab
                   ["Hummer","Hummer","Meeresfrüchte"],					#lobster
                   ["Garnele","Garnele","Meeresfrüchte"],				#prawns
                   ["Krabbe","Krabbe","Meeresfrüchte"],					#shrimp
                   ["Klaffmuschel","Klaffmuschel","Meeresfrüchte"],			#clam
                   ["Muschel","Muschel","Meeresfrüchte"],				#mussel
                   ["Tintenfisch","Tintenfisch","Meeresfrüchte"],			#octopus
                   ["Auster","Auster","Meeresfrüchte"],					#oyster
                   ["Schnecke","Schnecke","Meeresfrüchte"],				#snail
                   ["Kalmar","Kalmar","Meeresfrüchte"],					#squid
                   ["Kammuschel","Kammuschel","Meeresfrüchte"],				#scallop

                   ## F l e i s c h
                   ["Speck","Speck","Fleisch"],						#chopped bacon 
                   ["Bacon","Bacon","Fleisch"],						#bacon 
                   ["Schinken","Schinken","Fleisch"],					#ham
                   ["Hammel","Hammel","Fleisch"],					#mutton
                   ["Lamm","Lamm","Fleisch"],						#lamb
                   ["Kalb","Kalb","Fleisch"],						#veal
                   ["Steak","Steak","Fleisch"],						#steak
                   ["Hamburger","Hamburger","Fleisch"],					#hamburger
                   ["Roastbeef","Roastbeef","Fleisch"],					#roast beef
                   ["Hähnchen","Hähnchen","Fleisch"],					#chicken
                   ["Pute","Pute","Fleisch"],						#turkey
                   ["Ente","Ente","Fleisch"],						#duck
                   ["Gans","Gans","Fleisch"],						#goose
		   ["Rind","Rind","Fleisch"],						#beef
		   ["Hackfleisch","Hackfleisch","Fleisch"],				#mince beef
		   ["Hase","Hase","Fleisch"],						#hare
		   ["Kaninchen","Kaninchen","Fleisch"],					#rabbit
		   ["Hirsch","Hirsch","Fleisch"],					#deer
                   ["Hühnerbrust","Hühnerbrust","Fleisch"],				#chicken breast
                   ["Schweinefleisch","Schweinefleisch","Fleisch"],			#pork
                   ["Chorizo","Chorizo","Fleisch"],					#chorizo
                   ["Salami","Salami","Fleisch"],					#salami
                   ["Wurst","Wurst","Fleisch"],						#sausage
                   ["Bratwurst","Bratwurst","Fleisch"],					#sausage
                   ["Weißwurst","Weißwurst","Fleisch"],					#sausage
                   ["Currywurst","Currywurst","Fleisch"],				#sausage

		   ## L e b e n s m i t t e l
                   ["Weizenmehl","Mehl, Weizen-","Lebensmittel"],					#all purpose flour
                   ["Vollkorn Weizenmehl","Mehl, Vollkorn Weizen-","Lebensmittel"],	#wholemeal flour 
                   ["Hirsemehl","Mehl, Hirse-","Lebensmittel"],				#flour
                   ["Roggenmischung","Mehl, Roggenmischung","Lebensmittel"],		#rye flour
                   ["Backpulver","Backpulver","Lebensmittel"],				#baking powder
                   ["Natron","Natron","Lebensmittel"],					#baking soda
                   ["Schokolade","Schokolade","Lebensmittel"],				#chocolate
                   ["Schokotröpfen","Schokotröpfen","Lebensmittel"],			#chocolate chips
                   ["Zucker","Zucker","Lebensmittel"],					#suger
		   ["Süßstoff","Süßstoff","Lebensmittel"],				#artificial sweetner 
                   ["brauner Zucker"," Zucker, braun","Lebensmittel"],			#brown suger
                   ["weißer Zucker","Zucker, weiß","Lebensmittel"],			#white sugar
                   ["Raffinade","Zucker, Raffinade","Lebensmittel"],			#castor sugar
                   ["Salz","Salz","Lebensmittel"],					#salt
                   ["Meersalz","Salz, Meer-","Lebensmittel"],				#sea salt
                   ["Rosinen","Rosinen","Lebensmittel"],				#currents
                   ["Sultanienen","Sultanienen","Lebensmittel"],			#sultanas
                   ["geraspelte Kokosnuss","Kokosnuss, geraspelt","Lebensmittel"],	#(modifier?)
                   ["Vanille","Vanille","Lebensmittel"],				#vanilla
                   ["Vanilleessenz","Vanilleessenz","Lebensmittel"],			#vanilla extract
                   ["Walnusskerne","Walnusskerne","Lebensmittel"],			#walnut
                   ["Cashewnüsse","Cashewnüsse","Lebensmittel"],			#cashew nut
                   ["Mandeln","Mandeln","Lebensmittel"],				#almonds
                   ["Erdnüsse","Erdnüsse","Lebensmittel"],				#peanut
                   ["Kartoffelpüree","Kartoffelpüree","Lebensmittel"],			#potato mash
                   ["Klöße","Klöße","Lebensmittel"],					#potato dumplings
                   ["Pollenta","Pollenta","Lebensmittel"],				#yellow cornmeal
                   ["kernige Haferflocken","Haferflocken, kernig","Lebensmittel"],	#rolled oats
                   ["zarte Haferflocken","Haferflocken, zart","Lebensmittel"],		#fine rolled oats
                   ["Ketchup","Ketchup","Lebensmittel"],				#ketchup
                   ["Mayonnaise","Mayonnaise","Lebensmittel"],				#mayonnaise
		   ["Knäckebrot","Knäckebrot","Lebensmittel"],				#ryebread wafers
		   ["Dosentomaten","Tomaten, Dosen-","Lebensmittel"],			#canned tomatoes
		   ["Dosenmais","Mais, Dosen-","Lebensmittel"],				#canned sweetcorn

                   ["Sonnenblumenkerne","Sonnenblumenkerne","Lebensmittel"],		#sunflower seeds
                   ["Sesammus","Sesammus","Lebensmittel"],				#sesame seeds

                   ["Zitronensaft","Zitronensaft","Lebensmittel"],			#lemon juice
                   ["Zitronenkonzentrat","Zitronenkonzentrat","Lebensmittel"],		#lemon concentrate
                   ["Limettensaft","Saft, Limetten-","Lebensmittel"],			#lime juice
                   ["Orangensaft","Saft, Orangen","Lebensmittel"],			#whole orange juice
                   ["Orangennektar","Saft, Orangennektar","Lebensmittel"],		#orange juice

                   ["Tomatensuppe","Tomatensuppe","Lebensmittel"],			#tomato sauce
                   ["Bouillon","Bouillon","Lebensmittel"],				#broth
		   ["Gemüsebouillon","Bouillon, Gemüse-","Lebensmittel"],		#vegetable broth
    		   ["Hühnerbouillon","Bouillon, Hühner-","Lebensmittel"],		#broth, chicken
                   ["Hollandais","Hollandais","Lebensmittel"],				#hollandais sauce

                   ["gehackte Tomaten","Tomaten, gehackt","Lebensmittel"],		#chopped tomato
                   ["geschälte Tomaten","Tomaten, geschält","Lebensmittel"],		#peeled tomato
                   ["passierte Tomaten","Tomaten, passiert","Lebensmittel"],		#mashed tomato
                   ["Tomatenmark","Tomatenmark","Lebensmittel"],			#pureed tomato

                   ["Kekse","Kekse","Lebensmittel"],					#biscuits
                   ["Müsli","Müsli","Lebensmittel"],					#muesli
                   ["Pudding","Pudding","Lebensmittel"],				#instant custard pudding
		   ["Stärke","Stärke","Lebensmittel"],					#corn starch

		   ## R e i s   u n d   T e i g w a r e n
                   ["Nudeln","Nudeln","Reis & Teigwaren"],				#pasta
                   ["Spaghetti","Spagghetti","Reis & Teigwaren"],			#spaghetti
                   ["Penne","Penne","Reis & Teigwaren"],				#pasta tubes
                   ["Canelonni","Canelonni","Reis & Teigwaren"],			#
                   ["Fusilli","Fusilli","Reis & Teigwaren"],				#pasta twirls
                   ["Riccioli","Riccioli","Reis & Teigwaren"],				#pasta twirls
                   ["Lasagna","Lasagna","Reis & Teigwaren"],				#pasta sheets
		   ["Vermicelli","Vermicelli","Reis & Teigwaren"],			#vermicelli

                   ["Teig","Teig","Reis & Teigwaren"],					#dough
		   ["Hefeteig", "Teig, Hefe-","Reis & Teigwaren"],			#pastry dough
                   ["Pizzateig","Teig, Pizza-","Reis & Teigwaren"],			#pizza dough

                   ["Langkornreis","Reis, Langkorn-","Reis & Teigwaren"],		#rice longcorn
                   ["Basmatireis","Reis, Basmati-","Reis & Teigwaren"],			#basmati rice
                   ["Milchreis","Reis, Milch-","Reis & Teigwaren"],			#pudding rice
                   ["Naturreis","Reis, Natur-","Reis & Teigwaren"],			#whole rice
                   ["Wildreis","Reis, Wild-","Reis & Teigwaren"],			#wild (black) rice
                   ["Spitzenlangkornreis","Reis, Spitzenlangkorn-","Reis & Teigwaren"],	#rice longcorn cook

                   ## B r o t
                   ["Brot","Brot, allgemeines","Brot"],					#bread, any
                   ["Weißbrot","Brot, weiß","Brot"],					#white bread
                   ["Toastbrot","Brot, Toast-","Brot"],					#sliced white toasting bread
                   ["Vollkornbrot","Brot, Vollkorn-","Brot"],				#wholemeal bread
                   ["Sonnenblumenkernbrot","Brot, Sonnenblumenkern-","Brot"],		#sunflower seed wholmeal
                   ["Kürbiskernbrot","Brot, Kürbiskern-","Brot"],			#pupkin seed wholemeal
                   ["Sesambrot","Brot, Sesam-","Brot"],					#sesame seed wholemeal
                   ["Dreikornbrot","Brot, Dreikorn-","Brot"],				#3 corn wholemeal bread
                   ["Krustenbrot","Brot, Krusten-","Brot"],				#Crusty wholemeal bread
                   ["Landbrot","Brot, Land-","Brot"],					#wholemeal bread
                   ["Fladenbrot","Brot, Fladen-","Brot"],				#turkish round bread
                   ["Pumpernickel","Pumpernickel","Brot"],				#pumpernickel bread


		   ## K r ä u t e r   u n d   G e w ü r z e
                   ["Kräuter","Kräuter, gemischt","Gemüse"],				#mixed herbs
                   ["Petersilie","Petersilie","Gemüse"],				#parsley
                   ["schwarze Pfeffer","Pfeffer schwarz","Kräuter u Gewürze"],		#black pepper
                   ["Cayennepfeffer","Pfeffer, Cayenne","Kräuter u Gewürze"],           #cayenne
                   ["Kräuter de Provence","Kräuter de Provence","Kräuter u Gewürze"],   #Herbs de Provence
                   ["Kräutersalz","Kräutersalz","Kräuter u Gewürze"],                   #Herbed salt
                   ["Lorbeerblatt","Lorbeerblatt","Kräuter u Gewürze"],                 #Bay leaf
                   ["Gewürznelken","Gewürznelken","Kräuter u Gewürze"],                 #
                   ["Chilipulver","Chilipulver","Kräuter u Gewürze"],			#(modifier?)
                   ["Curry","Curry","Kräuter u Gewürze"],				#curry powder
                   ["Currypaste","Currypaste","Kräuter u Gewürze"],			#curry paste
                   ["Madras Curry","Curry, madras","Kräuter u Gewürze"],		#hotter curry powder
                   ["Garam Masala","Garam Masala","Kräuter u Gewürze"],			#
                   ["Zimtschote","Zimt, Zimtschote","Kräuter u Gewürze"],		#(modifier?)
                   ["gemahlener Zimt","Zimt, gemahlener","Kräuter u Gewürze"],		#(modifier?)
                   ["Korianderkerne","Korianderkerne","Kräuter u Gewürze"],		#(modifier?)
                   ["gemahlener Koriander","Koriander, gemahlener","Kräuter u Gewürze"],	#(modifier?)
                   ["Cuminkerne","Cuminkerne","Kräuter u Gewürze"],			#(modifier?)
                   ["gemahlener Cumin","Cumin, gemahlener","Kräuter u Gewürze"],	#(modifier?)
                   ["Senfkerne","Senfkerne","Kräuter u Gewürze"],			#(modifier?)
                   ["Senf","Senf","Kräuter u Gewürze"],					#(modifier?)
                   ["Dijon-Senf","Senf, Dijon","Kräuter u Gewürze"],			#(modifier?)
                   ["Muskatnuss","Muskatnuss","Kräuter u Gewürze"],			#nutmeg
                   ["Paprika, gemahlen","Paprika, gemahlen","Kräuter u Gewürze"],	#
                   ["Ingwerpulver","Ingwer, Ingwerpulver","Kräuter u Gewürze"],		#ground ginger
                   ["Kurkuma","Kurkuma","Kräuter u Gewürze"],				#turmeric, curcuma
                   ["Majoran","Majoran","Kräuter u Gewürze"],				#turmeric, curcuma
                   ["Oregano","Oregano","Kräuter u Gewürze"],				#oregano
                   ["Basilikum, gerebelt","Basilikum, gerebelt","Kräuter u Gewürze"],	#basil, crushed
                   ["frisches Basilikum","Basilikum, frisches","Kräuter u Gewürze"],	#fresh basil leaves
                   ["frischer Koriander","Koriander, frischer","Kräuter u Gewürze"],	#fresh coriander leaves
                   ["frisches Schnittlauch","Schnittlauch, frisches","Kräuter u Gewürze"],	#fresh chives
                   ["frischer Ingwer","Ingwer, frischer","Kräuter u Gewürze"],		#fresh ginger
                   ["Ingwerpaste","Ingwerpaste","Kräuter u Gewürze"],			#ginger paste


		   ## M a r m e l a d e
		   ["Pflaumenmarmelade","Marmelade, Pflaumen-","Konfitüren"],		#plum jam
		   ["Aprikosenmarmelade","Marmelade, Aprikosen-","Konfitüren"],		#apricot jam
		   ["Orangenmamalade","Marmalade, Orangen-","Konfitüren"],		#orange jam
		   ["Marmelade","Marmelade","Konfitüren"],				#jam - general
		   ["Erdbeermarmelade","Marmelade, Erdbeer-","Konfitüren"],		#strawberry jam
		   ["Himbeermarmelade","Marmelade, Himbeer-","Konfitüren"],		#raspberry jam
		   ["Erdnussbutter","Erdnussbutter","Konfitüren"],			#peanut butter
		   ["Nutella","Nutella","Konfitüren"],					#nussply
		   ["Sesamus","Sesamus","Konfitüren"],					#tahini - sesame spread
                   ["Honig","Honig","Konfitüren"],					#honey

		   ## I n t e r n a t i o n a l
                   ["Tartex","Tartex","International"],					#tartex spread
                   ["Kokosmilch","Kokusmilch","International"],				#coconut milk
                   ["Kokoscreme","Kokuscreme","International"],				#coconut cream
                   ["grüne Currypaste","Currypaste, grüne","International"],		#green curry paste
                   ["rote Currypaste","Currypaste, rote","International"],		#red curry paste
                   ["Reisessig","Essig, Reis-","International"],			#rice vinegar
                   ["Salsa","Salsa","International"],					#salsam
                   ["Sesamkerne","Sesamkerne","International"],				#sesame seeds
                   ["Soja-Sauce","Soja-Sauce","International"],				#soy sauce
                   ["Sojacreme","Sojacreme","International"],		                #soya cream
		   ["Bulgur","Bulgur","International"],					#bulgar
                   ["Couscous","Couscous","International"],				#couscous
                   ["Falafel","Falafel","International"],				#felafel
                   ["Tofu","Tofu","International"],					#tofu
                   ["Pak-choï","Pak-choï","Gemüse"],					#bok choy
	
		   ## M i l c h p r o d u k t e
                   ["Milch","Milch","Milchprodukte"],					#milk, unspecified
                   ["Käse","Käse, allgemeiner","Milchprodukte"],			#cheese, any
                   ["Butter","Butter","Milchprodukte"],					#butter
                   ["Margarine","Margarine","Milchprodukte"],				#	
                   ["Eier","Eier","Milchprodukte"],						#egg
                   ["frische Milch","Milch, frische","Milchprodukte"],			#milk
                   ["fettarme Milch","Milch, fettarme","Milchprodukte"],		#skimmed milk
		   ["H-Milch","Milch, H-Milch","Milchprodukte"],			#long-life milk
		   ["Sojamilch","Milch, Sojamilch", "Milchprodukte"],			#soya milk
		   ["Buttermilch","Milch, Buttermilch","Milchprodukte"],		#buttermilk
                   ["Sauerrahm","Sauerrahm","Milchprodukte"],				#sour cream
		   ["Sahne","Sahne","Milchprodukte"],					#
		   ["Sahne 10% Fett","Sahne, 10% Fett","Milchprodukte"],		#
		   ["Sahne 15% Fett","Sahne, 15% Fett","Milchprodukte"],		#
		   ["Sahne 35% Fett","Sahne, 35% Fett","Milchprodukte"],		#
                   ["Joghurt","Joghurt","Milchprodukte"],				#yogurt
		   ["Quark","Quark","Milchprodukte"],					#
		   ["Speisequark Magerstufe","Quark, Speise- Magerstufe","Milchprodukte"],	#
		   ["Kräuterquark","Quark, Kräuter","Milchprodukte"],			#
                   ["Cheddar-Käse","Käse, Cheddar","Milchprodukte"],			#cheddar cheese
                   ["Hartkäse","Käse, Hart-","Milchprodukte"],				#general hard cheese
                   ["Hüttenkäse","Käse, Hüttenkäse","Milchprodukte"],			#cottage cheese
                   ["Schnittkäse","Käse, Schnittkäse","Milchprodukte"],			#cottage cheese
                   ["Fetakäse","Käse, Fetakäse","Milchprodukte"],			#feta cheese
                   ["Ziegenkäse","Käse, Ziegenkäse","Milchprodukte"],			#fresh cheese white goat
                   ["Schaffskäse","Schaffskäse","Milchprodukte"],			#sheeps cheese
                   ["Emmentaler","Käse, Emmentalerkäse","Milchprodukte"],		#emmental
                   ["Mozzarella","Käse, Mozzarella","Milchprodukte"],			#mozzarella cheese
                   ["Parmesan","Käse, Parmesan","Milchprodukte"],			#parmesan cheese
                   ["Provolone","Käse, Provolone","Milchprodukte"],			#provolone cheese
                   ["Ricotta","Käse, Ricotta","Milchprodukte"],				#ricotta cheese
                   ["Gouda","Käse, Gouda","Milchprodukte"],				#cheese Gouda
                   ["Brie","Käse, Brie","Milchprodukte"],				#cheese Brie
                   ["Streichkäse","Käse, Steich","Milchprodukte"],			#spreading cheese
                   ["Philladelphia","Käse, Philladelphia","Milchprodukte"],		#philladelphia cheese


		   ## h e i ß e   G e t r ä n k e
                   ["schwarzer Tee","Tee, schwarzer","Getränke, heiß"],			#black tea
                   ["gemahlener Kaffee, ","Kaffee, gemahlener","Getränke, heiß"],	#ground coffee
                   ["gemahler entkoffeinierter Kaffee","Kaffee, gemahlener entkoffeinierter","Getränke, heiß"],	#decaff ground coffee
                   ["Kaffeefilter","Kaffeefilter","Getränke, heiß"],			#coffee filters
                   ["Kakao","Kakao","Getränke, heiß"],					#drinking chocolate
                   ["Carokaffee","Carokaffee","Getränke, heiß"],			#caro coffee
                   ["Früchtetee, ","Tee, Früchtetee","Getränke, heiß"],			#fruit tea
                   ["Pfefferminztee","Tee, Pfefferminztee","Getränke, heiß"],		#peppermint tea
                   ["Hagebuttentee","Tee, Hagebuttentee","Getränke, heiß"],		#rosehip tea
                   ["Kamillentee","Tee, Kamillentee","Getränke, heiß"],			#camomile tea
                   ["Fencheltee","Tee, Fencheltee","Getränke, heiß"],			#fenchel tea
                   ["Rotbuschtee","Tee, Rotbuschtee","Getränke, heiß"],			#roobusch tea
                   ["Kräutertee","Tee, Kräutertee","Getränke, heiß"],			#herb tea
                   ["grüner Tee","Tee, grüner","Getränke, heiß"],			#green tea
                   ["Yogitee","Tee, Yogitee","Getränke, heiß"],				#yogi (ayurvedic) tea

		   ## F l u ß i g k e i t e n
                   ["Tafelessig","Essig, Tafel-","Flüssigkeiten"],			#table vinegar
                   ["Obstessig","Essig, Obst-","Flüssigkeiten"],			#table vinegar
                   ["Balsamico-Essig","Essig, Balsamico-","Flüssigkeiten"],		#balsamic vinegar
                   ["Sonnenblumenöl","Öl, Sonnenblumenöl","Flüssigkeiten"],		#sunflower oil
                   ["Olivenöl","Öl, Olivenöl","Flüssigkeiten"],				#olive oil
                   ["Sesamöl","Öl, Sesamöl","Flüssigkeiten"],				#sesame oil
                   ["Pflanzenöl","Öl, Pflanzenöl","Flüssigkeiten"],			#vegetable oil
		   ["Sojaöl","Öl, Sojaöl","Flüssigkeiten"],				#soya oil
                   ["Weißwein","Wein, weiß","Flüssigkeiten"],				#white wine
                   ["Rotwein","Wein, rot","Flüssigkeiten"],				#red wine

                   ## t h i n g   y o u   s h o u l d   h a v e   a t   h o m e 
                   ["Wasser","Wasser","Flüssigkeiten"]					#water

                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
# Each unit is of the following format:
# ("unit1","unit2"):conversion_factor, where unit1 contains conversion_factor X unit2
# For example: 1 cup has 16 tablespoons.
CONVERTER_TABLE = {
    ("Tasse", "EL"):16,
    ("EL", "TL"):3,
    ("pt.", "Tasse"):2,
    ("qt.", "Tasse"):4,
    ("l", "ml"):1000,
    ("l", "cl"):100,
    ("l", "dl"):10,
    ("oz.", "g"):28.35,
    ("kg", "g"):1000,
    ("g", "mg"):1000,
    ("TL", "Tröpchen"):76,
    ("Dose, mittel", "g"):400,
    ("Dose, groß",   "g"):800,
    ("Dose, klein",  "g"):200,
    ("lb.", "oz."):16,
    ("l", "qt."):1.057
}


# DENSITIES of common foods. This allows us to convert between mass and volume.
# Translators: You may be best off translating the food names below, since lists
# of food densities can be hard to come by!
DENSITY_TABLE={
    "Wasser":1,				#water
    "Traubensaft":1.03,			#juice, grape
    "Bouillon, gemüse":1,		#vegetable broth
    "Bouillon, hühner":1,		#broth, chicken
    "Milch":1.029,			#milk
    "Milch entier":1.029,		#milk, whole
    "Milch, fettarm":1.033,		#milk, skim
    "Milch 2%":1.031,			#milk, 2%
    "Milch 1%":1.03,			#milk, 1%
    "Kokosmilch":0.875,			#coconut milk
    "Buttermilch":1.03,			#buttermilk
    "Sahne riche":0.994,		#heavy cream
    "Sahne légère":1.012,		#light cream
    "Sahne 11,5%":1.025,		#half-and-half
    "Honig":1.420,			#honey
    "Zucker":1.550,			#sugar, white
    "Salz":2.165,			#salt
    "Butter":0.911,			#butter
    "Pflanzen Öl":0.88,			#oil, vegetable
    "Oliven Öl":0.88,			#oil, olive
    "Sonnenblumen Öl":0.88,		#oil, corn
    "Sesam Öl":0.88,			#oil, sesame
    "Mehl": 0.6,			#flour, all purpose
    "Vollkornmehl": 0.6,		#flour, whole wheat
    "Stärke": 0.6,			#corn starch
    "Zucker en poudre": 0.6,		#sugar, powdered
    "Zucker glace": 0.6			#sugar, confectioners
      }

### ORIGINAL TABLES FROM ENGLISH

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
UNITS = [
         ["ml", ["Milliliter","milliliter","Milliliters","milliliters","ml", "ml."]],
         ["cl", ["Centiliter","centiliter","Centiliters","centiliters","cl", "cl."]],
         ["dl", ["Deciliter","deciliter","Deciliters","deciliters","dl", "dl."]],
         ["l", ["Liter","Liters","liter","liters","l.", "lit.", "l"]],

         ["g", ["Gramm","Gramme","gramm", "gramme", "g.","g","gram","grams"]],
         ["mg", ["Milligramm","milligramm","Milligramme","milligramme","mg.", "mg","milligram","milligrams"]],
         ["kg", ["Kilogramm","kilogramm","Kilogramme","kilogramme","kg.", "kg","kilogram","kilograms"]],

         ["cm", ["Centimeter","centimeter","Centimeters","centimeters","cm", "cm."]],
         ["mm", ["Millimeter","millimeter","Millimeters","millimeters","mm", "mm."]],
         ["m", ["Meter","meter","Meters","meters","m", "m."]],

         ["Tröpfchen",["Tröpfchen","tröpfchen","troepfchen","Troepfchen","drop","drops"]],
         ["TL", ["Teelöffel","Teelöffeln","teelöffel","teelöffeln","tl","TL","tsp", "tsp.","tea spoon", "teaspoon"]],
         ["EL", ["Esslöffel","Esslöffeln","esslöffel","esslöffeln","el","EL","tbs", "tbsp", "tbs.", "tbsp.", "table spoon","tablespoon"]],
         ["Tasse", ["Tasse","Tassen","tasse","tassen","cup", "c.", "cups","Glas","glas", "Glass", "glass"]],
	 ["Becher", ["Becher","becher"]],

         ["St.", ["St.","Stück","Stücke","Stueck","Stuecke","Mal","stück","stücke","stueck","stuecke", "mal","piece", "pieces","St","st"]],
         ["Dose, mittel", ["Dose, mittel","dose, mittel","mittlere Dose","mittlere dose"]],
         ["Dose, groß", ["Dose, groß", "dose, groß","größe Dose","größe dose"]],
         ["Dose, klein", ["Dose, klein","dose, klein","kleine Dose","kleine dose"]],
	 ["Zeh", ["Zeh","Zehen","zeh","zehen"]],           #garlick
	 ["Paket",["Paket","Pakete","paket","pakete", "Packung", "packung", "pack"]],
	 ["Prise",["Prise","Prisen","prise","prisen"]],    #pinch
	 ["Bund",["Bund","Bunde","bund","bunde"]],         #bunch

         ["lb.", ["Pfund","pfund","pound","pounds","lb","lb.", "lbs."]],
         ["oz.", [ "ounce","ounces","oz","oz."]],
         ["qt.", ["quart", "qt.", "quarts"]],
         ["pt.", ["pint", "pt.", "pints"]],
         ["gallon", ["gallon", "gallons","gal."]]

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
    ("pt.", "lb."):['density',1],
    ("EL", "oz."):['density',0.5],
    ("Tasse", "oz."):['density',8],
    ("l", "kg"):['density',1],
    ("ml", "g"):['density',1]
    }

# The units here need to correspond to the standard unit names defined
# in UNITS.  These are some core conversions from mass-to-volume,
# assuming a density of 1 (i.e. the density of water).
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
    ("l", "kg") : 1
    }

### From translator :
### FRENCH PART TO BE REVISED !!! US units != UK units != Canadian units !!!
### I will work on these later... 
# VOL_TO_MASS_TABLE = {
#     ("chop","lb") : 1,					#(warning, might not be accurate, see below)
#     ("c. à table","oz") : 0.5,
#     ("tasse","oz") : 8,
#     ("chop","oz") : 20,					#(warning, modified, see "chopine" in granddictionnaire)
#     ("ml","g") : 1,
#     ("ml","mg") : 1000,
#     ("ml","kg"): 0.001,
#     ("cl","kg"): 0.01,
#     ("cl","g") : 10,
#     ("dl","kg") : 0.1,
#     ("dl","g") : 100,    
#     ("l","kg") : 1}

# TIME ABBREVIATIONS (this is new!)
TIME_ABBREVIATIONS = {
    'sec':'Sek.',
    'min':'Min.',
    'hr':'Std.'
    }

IGNORE = ["und","mit","von","für",
          "kalt","kalte","kalter","kaltes","kalten",
          "warm","warmer","warme","warmes","warmen",
          "dunn","dunner","dunne","dunnes","dunnen",
          "dick","dicker","dicke","dickes","dicken"
          ]

NUMBERS = {
    }
                    
# These functions are rather important! Our goal is simply to
# facilitate look ups -- if the user types in "tomatoes", we want to
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

