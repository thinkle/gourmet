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

# Language: English
# Translator: None (English is our default language).
# Last-updated: 4/27/05

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

fields={'cuisine': ['American','Italian','Mexican',
                    'Southwestern','Asian/Thai','Asian/Vietnamese',
                    'Asian/Chinese','Asian/Japanese',],
        'rating' : ['Excellent','Great','Good','Fair','Poor'],
        'source' : [],
        'category' : ['Dessert','Entree','Salad','Soup',
                      'Breakfast'],
                  }

# In English, there are a heck of a lot of synonyms. This is a list
# for those synonyms.  ["preferred word","alternate word","alternate word"]
# If there are none of these that you can think of in your language, just
# set this to:
# SYNONYMS=[]
SYNONYMS=[
    # the first item of each list is the default
    ["eggplant","aubergine"],
    ["scallion","green onion","spring onion"],
    ["arugula","rocket"],
    ["azuki beans", "adzuki beans", "adzuki", "azuki"],
    ["snap peas","mangetout"],
    ["bok choy","chinese leaves"],
    ["chilli pepper","capsicum"],
    ["corn","sweetcorn","maise","sweet corn"],
    ["red bell pepper","red pepper"],
    ["bell pepper, green", "green pepper", "bell pepper","green bell pepper", "pepper"],
    ["beet","beetroot"],
    ["collard greens","spring greens"],
    ["cilantro","coriander"],
    ["turabaga","swede"],
    ["zucchini","courgette"],
    ["chokeberry","cooking apple"],
    ["juneberry","saskatoon"],
    ["nannyberry","sheepberry"],
    ["kiwi fruit","chinese gooseberry"],
    ["sunberry","wonderberry"],
    ["start fruit","carambola"],
    ["dragonfruit" , "pitaya"],
    ["jackfruit","nangka"],
    ["langsat","longkong", "duku"],
    ["velvet persimmon","mabolo"],
    ["mamoncillo", "quenepa", "genip"],
    ["rose apple", "malay apple"],
    ["salak", "snakefruit"],
    ["sapodilla", "chiku", "sapadilla", "snake fruit", "sawo"],
    ["soursop", "guanabana"],
    ['black cod','sablefish'],
    ['chilean sea bass','patagonian toothfish'],
    ['flour, all purpose','flour, all-purpose','flour','white flour'],
    ['sugar, white','sugar'],    
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

INGREDIENT_DATA = [["alfalfa sprouts","alfalfa sprouts","produce"],
                   ["anise","anise","produce"],
                   ["artichoke","artichoke","produce"],
                   ["arugula","arugula","produce"],
                   ["asparagus","asparagus","produce"],
                   ["eggplant","eggplant","produce"],
                   ["avocado","avocado","produce"],
                   ["green beans","green beans","produce"],
                   ["azuki beans","azuki beans","produce"],
                   ["bean sprouts","bean sprouts","produce"],
                   ["black beans","black beans","produce"],
                   ["black-eyed peas","black-eyed peas","produce"],
                   ["borlotti beans","borlotti beans","produce"],
                   ["broad beans","broad beans","produce"],
                   ["chickpeas, garbanzos, or ceci beans","chickpeas, garbanzos, or ceci beans","produce"],
                   ["green beans","green beans","produce"],
                   ["kidney beans","kidney beans","produce"],
                   ["lentils","lentils","produce"],
                   ["lima bean","butter bean","produce"],
                   ["mung beans","mung beans","produce"],
                   ["navy beans","navy beans","produce"],
                   ["runner beans","runner beans","produce"],
                   ["soybeans","soybeans","produce"],
                   ["peas","peas","produce"],
                   ["snap peas","snap peas","produce"],
                   ["bok choy","bok choy","produce"],
                   ["breadfruit","breadfruit","produce"],
                   ["broccoflower","broccoflower","produce"],
                   ["broccoli","broccoli","produce"],
                   ["brussels sprouts","brussels sprouts","produce"],
                   ["cabbage","cabbage","produce"],
                   ["calabrese","calabrese","produce"],
                   ["cauliflower","cauliflower","produce"],
                   ["celery","celery","produce"],
                   ["chard","chard","produce"],
                   ["cilantro","cilantro","produce"],
                   ["collard greens","collard greens","produce"],
                   ["corn salad","corn salad","produce"],
                   ["endive","endive","produce"],
                   ["fennel","fennel","produce"],
                   ["fiddleheads","fiddleheads","produce"],
                   ["frisee","frisee","produce"],
                   ["kale","kale","produce"],
                   ["kohlrabi","kohlrabi","produce"],
                   ["lemon grass","lemon grass","produce"],
                   ["lettuce lactuca sativa","lettuce lactuca sativa","produce"],
                   ["corn","corn","produce"],
                   ["mushrooms","mushrooms","produce"],
                   ["mustard greens","mustard greens","produce"],
                   ["nettles","nettles","produce"],
                   ["new zealand spinach","new zealand spinach","produce"],
                   ["okra","okra","produce"],
                   ["onion family","onion family","produce"],
                   ["chives","chives","produce"],
                   ["garlic","garlic","produce"],
                   ["leek allium porrum","leek allium porrum","produce"],
                   ["onion","onion","produce"],
                   ["shallot","shallot","produce"],
                   ["scallion","scallion","produce"],
                   ["parsley","parsley","produce"],
                   ["green pepper","bell pepper, green","produce"],
                   ["red bell pepper","bell pepper, red","produce"],
                   ["chilli pepper","chilli pepper","produce"],
                   ["jalapeño pepper","pepper, jalapeño","produce"],
                   ["habanero pepper","pepper, habanero","produce"],
                   ["radicchio","radicchio","produce"],
                   ["rapini","rapini","produce"],
                   ["rhubarb","rhubarb","produce"],
                   ["root vegetables","root vegetables","produce"],
                   ["beet","beet","produce"],
                   ["carrot","carrot","produce"],
                   ["cassava (manioc)","cassava (manioc)","produce"],
                   ["celeriac","celeriac","produce"],
                   ["daikon","daikon","produce"],
                   ["fennel","fennel","produce"],
                   ["ginger","ginger","produce"],
                   ["parsnip","parsnip","produce"],
                   ["radish","radish","produce"],
                   ["rutabaga","rutabaga","produce"],
                   ["turnip","turnip","produce"],
                   ["wasabi","wasabi","produce"],
                   ["white radish","white radish","produce"],
                   ["skirret","skirret","produce"],
                   ["spinach","spinach","produce"],
                   ["acorn squash","squash, acorn","produce"],
                   ["butternut squash","squash, butternut","produce"],
                   ["zucchini","zucchini","produce"],
                   ["cucumber","cucumber","produce"],
                   ["gem squash","squash, gem","produce"],
                   ["patty pans","patty pans","produce"],
                   ["pumpkin","pumpkin","produce"],
                   ["spaghetti squash","squash, spaghetti","produce"],
                   ["tat soi","tat soi","produce"],
                   ["tomato","tomato","produce"],
                   ["jicama","jicama","produce"],
                   ["jerusalem artichoke","jerusalem artichoke","produce"],
                   ["potato","potato","produce"],
                   ["sweet potato","sweet potato","produce"],
                   ["taro","taro","produce"],
                   ["yam","yam","produce"],
                   ["water chestnut","water chestnut","produce"],
                   ["watercress","watercress","produce"],
                   # fruits, from wikipedia list
                   ["apple","apple","produce"],
                   ["green apple","green apple","produce"],
                   ["crabapple","crabapple","produce"],
                   ["chokeberry","chokeberry","produce"],
                   ["hawthorn","hawthorn","produce"],
                   ["juneberry","juneberry","produce"],
                   ["loquat","loquat","produce"],
                   ["medlar","medlar","produce"],
                   ["pomegranate","pomegranate","produce"],
                   ["quince","quince","produce"],
                   ["rowan","rowan","produce"],
                   ["rose hip","rose hip","produce"],
                   ["apricot","apricot","produce"],
                   ["cherry","cherry","produce"],
                   ["plum","plum","produce"],
                   ["peach","peach","produce"],
                   ["nectarine","nectarine","produce"],
                   ["blackberry","blackberry","produce"],
                   ["boysenberry","boysenberry","produce"],
                   ["raspberry","raspberry","produce"],
                   ["cloudberry","cloudberry","produce"],
                   ["wineberry","wineberry","produce"],
                   ["bearberry","bearberry","produce"],
                   ["bilberry","bilberry","produce"],
                   ["blueberry ","blueberry ","produce"],
                   ["cranberry ","cranberry ","produce"],
                   ["huckleberry ","huckleberry ","produce"],
                   ["lingonberry","lingonberry","produce"],
                   ["barberry ","barberry ","produce"],
                   ["red currant","currant, red","produce"],
                   ["black currant","currant, black","produce"],
                   ["white currant","currant, white","produce"],
                   ["elderberry ","elderberry ","produce"],
                   ["gooseberry ","gooseberry ","produce"],
                   ["nannyberry","nannyberry","produce"],
                   ["sea-buckthorn","sea-buckthorn","produce"],
                   ["wolfberry","wolfberry","produce"],
                   ["crowberry","crowberry","produce"],
                   ["mulberry","mulberry","produce"],
                   ["goumi","goumi","produce"],
                   ["kiwi fruit ","kiwi fruit ","produce"],
                   ["persimmon ","persimmon ","produce"],
                   ["buffaloberry","buffaloberry","produce"],
                   ["pawpaw","pawpaw","produce"],
                   ["american persimmon","american persimmon","produce"],
                   ["prickly pear ","prickly pear ","produce"],
                   ["saguaro","saguaro ","produce"],
                   ["pitaya","pitaya","produce"],
                   ["cantaloupe","cantaloupe","produce"],
                   ["honeydew","honeydew","produce"],
                   ["sunberry","sunberry","produce"],
                   ["watermelon ","watermelon ","produce"],
                   ["strawberry ","strawberry ","produce"],
                   ["angelica","angelica","produce"],
                   ["rhubarb","rhubarb","produce"],
                   ["fig ","fig ","produce"],
                   ["grape","grape","produce"],
                   ["jujube","jujube","produce"],
                   ["black mulberry","black mulberry","produce"],
                   ["pomegranate","pomegranate","produce"],
                   ["date","date","produce"],
                   ["citron","citron","produce"],
                   ["grapefruit","grapefruit","produce"],
                   ["pommelo","pommelo","produce"],
                   ["key lime","key lime","produce"],
                   ["kumquat","kumquat","produce"],
                   ["lemon","lemon","produce"],
                   ["lime","lime","produce"],
                   ["mandarin","mandarin","produce"],
                   ["clementine","clementine","produce"],
                   ["tangelo","tangelo","produce"],
                   ["tangerine","tangerine","produce"],
                   ["orange","orange","produce"],
                   ["ugli fruit","ugli fruit","produce"],
                   ["guava ","guava ","produce"],
                   ["longan","longan","produce"],
                   ["lychee","lychee","produce"],
                   ["passion fruit","passion fruit","produce"],
                   ["feijoa","feijoa","produce"],
                   ["akee","akee","produce"],
                   ["banana","banana","produce"],
                   ["plantain","plantain","produce"],
                   ["breadfruit","breadfruit","produce"],
                   ["camucamu","camucamu","produce"],
                   ["star fruit","star fruit","produce"],
                   ["cempedak","cempedak","produce"],
                   ["cherimoya","cherimoya","produce"],
                   ["coconut","coconut","produce"],
                   ["custard apple","custard apple","produce"],
                   ["dragonfruit","dragonfruit","produce"],
                   ["durian","durian","produce"],
                   ["guarana","guarana","produce"],
                   ["jackfruit","jackfruit","produce"],
                   ["keppel fruit","keppel fruit","produce"],
                   ["langsat","langsat","produce"],
                   ["velvet persimmon","velvet persimmon","produce"],
                   ["mamey sapote","mamey sapote","produce"],
                   ["mamoncillo","mamoncillo","produce"],
                   ["mango","mango","produce"],
                   ["mangosteen","mangosteen","produce"],
                   ["marang","marang","produce"],
                   ["papaya","papaya","produce"],
                   ["peanut butter fruit","peanut butter fruit","produce"],
                   ["pineapple","pineapple","produce"],
                   ["poha","poha","produce"],
                   ["rambutan","rambutan","produce"],
                   ["rose apple","rose apple","produce"],
                   ["salak","salak","produce"],
                   ["sapodilla","sapodilla","produce"],
                   ["soursop","soursop","produce"],
                   ["sugar apple","sugar apple","produce"],
                   ["tamarind","tamarind","produce"],
                   ## seafood, from wikipedia list
                   ["anchovy","anchovy","seafood"],
                   ["bass","bass","seafood"],
                   ["striped bass","striped bass","seafood"],
                   ["black cod","black cod","seafood"],
                   ["blowfish","blowfish","seafood"],
                   ["catfish","catfish","seafood"],
                   ["cod","cod","seafood"],
                   ["eel","eel","seafood"],
                   ["flounder","flounder","seafood"],
                   ["haddock","haddock","seafood"],
                   ["halibut","halibut","seafood"],
                   ["lingcod","lingcod","seafood"],
                   ["mahi mahi","mahi mahi","seafood"],
                   ["monkfish","monkfish","seafood"],
                   ["orange roughy","orange roughy","seafood"],
                   ["chilean sea bass","chilean sea bass","seafood"],
                   ["pike","pike","seafood"],
                   ["pollock","pollock","seafood"],
                   ["sanddab","sanddab","seafood"],
                   ["sardine","sardine","seafood"],
                   ["salmon","salmon","seafood"],
                   ["sea bass","sea bass","seafood"],
                   ["shark","shark","seafood"],
                   ["snapper","snapper","seafood"],
                   ["rockfish","rockfish","seafood"],
                   ["rock cod","rock cod","seafood"],
                   ["pacific snapper","pacific snapper","seafood"],
                   ["red snapper","red snapper","seafood"],
                   ["sole","sole","seafood"],
                   ["sturgeon","sturgeon","seafood"],
                   ["surimi","surimi","seafood"],
                   ["swordfish","swordfish","seafood"],
                   ["tilapia","tilapia","seafood"],
                   ["tilefish","tilefish","seafood"],
                   ["trout","trout","seafood"],
                   ["tuna","tuna","seafood"],
                   ["whitefish","whitefish","seafood"],
                   ["whiting","whiting","seafood"],
                   ["roe","roe","seafood"],
                   ["caviar","caviar","seafood"],
                   ["salmon roe","salmon roe","seafood"],
                   ["crab","crab","seafood"],
                   ["dungness crab","dungness crab","seafood"],
                   ["king crab","king crab","seafood"],
                   ["snow crab","snow crab","seafood"],
                   ["crayfish","crayfish","seafood"],
                   ["lobster","lobster","seafood"],
                   ["shrimp","shrimp","seafood"],
                   ["prawns","prawns","seafood"],
                   ["abalone","abalone","seafood"],
                   ["clam","clam","seafood"],
                   ["mussel","mussel","seafood"],
                   ["octopus","octopus","seafood"],
                   ["oyster","oyster","seafood"],
                   ["snail","snail","seafood"],
                   ["squid","squid","seafood"],
                   ["scallop","scallop","seafood"],
                   ## meats (garnered from wikipedia lists)
                   ["bacon","bacon","meats"],
                   ["chorizo","chorizo","meats"],
                   ["fuet","fuet","meats"],
                   ["salami","salami","meats"],
                   ["ham","ham","meats"],
                   ["mutton","mutton","meats"],
                   ["lamb","lamb","meats"],
                   ["veal","veal","meats"],
                   ["steak","steak","meats"],
                   ["hamburger","hamburger","meats"],
                   ["roast beef","roast beef","meats"],
                   ["chicken","chicken","meats"],
                   ["turkey","turkey","meats"],
                   ["duck","duck","meats"],
                   ["goose","goose","meats"],
                   ## my old list
                   ["tamarind water","tamarind water", "international"],
                   ["tamarind juice","tamarind juice", "international"],
                   ['vegetable broth','broth, vegetable', 'soups&sauces'],
                   ['fresh basil','basil, fresh', 'produce',],
                   ['light sugar brown','sugar, light brown', 'baking',],
                   ['balsamic vinegar','vinegar, balsamic', 'wines&oils',],
                   ['zuchini','zuchini', 'produce',],
                   ['avocado','avocado', 'produce',],
                   ['walnut','walnut', 'baking',],
                   ['celery','celery', 'produce',],
                   ['coriander seeds','coriander, seeds', 'spices',],
                   ['provolone cheese','cheese, provolone', 'dairy',],
                   ['galanga','galanga', 'produce',],
                   ['couscous','couscous', 'pastas',],
                   ['rice','rice', 'pastas',],
                   ['flour tortillas','tortillas, flour', 'dairy',],
                   ['olive oil','oil, olive', 'wines&oils',],
                   ['vanilla extract','vanilla extract', 'baking',],
                   ['red potato-skinned','potato, red-skinned', 'produce',],
                   ['powdered ginger','ginger, powdered', 'spices',],
                   ['roasted chili paste','roasted chili paste', 'international',],
                   ['curry powder','curry powder', 'spices',],
                   ['dried shrimp','shrimp, dried', 'international',],
                   ['dijon mustard','mustard, dijon', 'condiments',],
                   ['whole rock cod or snapper','whole rock cod or snapper', 'seafood',],
                   ['shells pasta','pasta, shells', 'pastas',],
                   ['green canned chiles','green chiles, canned', 'international',],
                   ['nutmeg','nutmeg', 'spices',],
                   ['sourdough bread','bread, sourdough', 'bread',],
                   ['corn oil','oil, corn', 'wines&oils',],
                   ['lemon grass','lemon grass', 'produce',],
                   ['feta cheese','cheese, feta', 'dairy',],
                   ['jack cheese','cheese, jack', 'dairy',],
                   ['grape tomato','tomato, grape', 'produce',],
                   ['cherry tomato','tomato, cherry', 'produce',],
                   ['spaghetti','spaghetti', 'pastas',],
                   ['cottage cheese','cheese, cottage', 'dairy',],
                   ['white onion','onion, white', 'produce',],
                   ['baking soda','baking soda', 'baking',],
                   ['garam masala','garam masala', 'spices',],
                   ['yogurt','yogurt', 'dairy',],
                   ['monkfish','monkfish', 'seafood',],
                   ['croutons','croutons', 'bread',],
                   ['ground coriander','coriander, ground', 'spices',],
                   ['chili powder','chili powder', 'spices',],
                   ['curly lettuce leaf','lettuce, curly leaf', 'produce',],
                   ['dark sugar brown','sugar, dark brown', 'baking',],
                   ['rice vinegar','vinegar, rice', 'international',],
                   ['pasta','pasta', 'pastas',],
                   ['sesame oil','oil, sesame', 'wines&oils',],
                   ['water','water', ''],
                   ['sour cream','sour cream', 'dairy',],
                   ['orange juice','orange juice', 'produce',],
                   ['spinach','spinach', 'produce',],
                   ['stick cinnamon','cinnamon, stick', 'spices',],
                   ['shrimp paste','shrimp paste', 'international',],
                   ['ground cinnamon','cinnamon, ground', 'spices',],
                   ['salad greens','salad greens', 'produce',],
                   ['garlic','garlic', 'produce',],
                   ['vegetable oil','oil, vegetable', 'wines&oils',],
                   ['peanut butter','peanut butter', 'bread',],
                   ['seeds ajowan','ajowan, seeds', 'spices',],
                   ['apple','apple', 'produce',],
                   ['cayenne','cayenne', 'spices',],
                   ['arugula','arugula', 'produce',],
                   ['linguine pasta','pasta, linguine', 'pastas',],
                   ['scallion','scallion', 'produce',],
                   ['egg','egg', 'dairy',],
                   ['lime','lime', 'produce',],
                   ['olives','olives', 'produce',],
                   ['basil, thai fresh','basil, fresh, thai', 'produce',],
                   ['bean sprouts','bean sprouts', 'produce',],
                   ['ricotta cheese','cheese, ricotta', 'dairy',],
                   ['parsley','parsley', 'produce',],
                   ['acorn squash','squash, acorn', 'produce',],
                   ['yellow onion','onion, yellow', 'produce',],
                   ['chiles, dried red','chiles, red, dried', 'produce',],
                   ['portobello mushroom','mushroom, portobello', 'produce',],
                   ['nappa cabbage','cabbage, nappa', 'produce',],
                   ['lime leaves','lime leaves', 'produce',],
                   ['butter','butter', 'dairy',],
                   ['bell red pepper','bell pepper, red', 'produce',],
                   ['mushroom','mushroom', 'produce',],
                   ['shallot','shallot', 'produce',],
                   ['cheddar cheese','cheese, cheddar', 'dairy',],
                   ['mozzarella cheese','cheese, mozzarella', 'dairy',],
                   ['squash','squash', 'produce',],
                   ['fish sauce','fish sauce', 'international',],
                   ['green curry paste','green curry paste', 'international',],
                   ['curly endive','endive, curly', 'produce',],
                   ['white sugar','sugar, white', 'baking',],
                   ['fresh cheese white goat','cheese, fresh white goat', 'dairy',],
                   ['cilantro stems','cilantro stems', 'produce',],
                   ['yellow cornmeal','cornmeal, yellow', 'baking',],
                   ['paprika','paprika', 'spices',],
                   ['chocolate chips','chocolate chips', 'baking',],
                   ['star anise','star anise', 'spices',],
                   ['brown sugar','sugar, brown', 'baking',],
                   ['roasted peanuts','peanuts, roasted', 'produce',],
                   ['fresh cilantro','cilantro, fresh', 'produce',],
                   ['honey','honey', 'baking',],
                   ['russet potato','potato, russet', 'produce',],
                   ['lemon juice','lemon juice', 'produce',],
                   ['carrot','carrot', 'produce',],
                   ['penne pasta','pasta, penne', 'pastas',],
                   ['red onion','onion, red', 'produce',],
                   ['shredded coconut','coconut, shredded', 'baking',],
                   ['peppered linguini','linguini, peppered', 'pastas',],
                   ['milk','milk', 'dairy',],
                   ['tahitian squash','squash, tahitian', 'produce',],
                   ['baking powder','baking powder', 'baking',],
                   ['tomato sauce','tomato sauce', 'soups&sauces',],
                   ['seeds mustard','mustard, seeds', 'spices',],
                   ['flat rice flour noodles','flat rice flour noodles', 'international',],
                   ['parmesan cheese','cheese, parmesan', 'pastas',],
                   ['mayonnaise','mayonnaise', 'bread',],
                   ['leek','leek', 'produce',],
                   ['zucchini','zucchini', 'produce',],
                   ['smoked cheese Gouda','cheese, smoked Gouda', 'dairy',],
                   ['lime juice','lime juice', 'produce',],
                   ['coconut milk','coconut milk', 'international',],
                   ['eggs','egg', 'dairy',],
                   ['salmon','salmon', 'seafood',],
                   ['lasagna pasta noodles','pasta, lasagna noodles', 'pastas',],
                   ['all purpose flour','flour, all purpose', 'baking',],
                   ['flour','flour, all purpose','baking',],
                   ['all-purpose flour','flour, all purpose','baking',],
                   ['ground cumin','cumin, ground', 'spices',],
                   ['cucumber','cucumber', 'produce',],
                   ['salsa','salsa', 'international',],
                   ['broccoli','broccoli', 'produce',],
                   ['rolled oats','rolled oats', 'pastas',],
                   ['tomato','tomato', 'produce',],
                   ['potato','potato', 'produce',],
                   ['white wine','wine, white', 'wines&oils',],
                   ['black ground pepper','black pepper, ground', 'spices',],
                   ['seeds cumin','cumin, seeds', 'spices',],
                   ['soy sauce','soy sauce', 'international',],
                   ['sesame seeds','sesame seeds', 'international',],
                   ['radicchio','radicchio', 'produce',],
                   ['salt','salt', 'baking',],
                   ['fresh ginger','ginger, fresh', 'produce',],
                   ['turmeric','turmeric', 'spices',],
                   ['chicken breast' ,'chicken, breast' , 'meats',],
                   ['whole chicken' ,'chicken, whole' , 'meats',],
                   ['chicken leg' ,'chicken, leg' , 'meats',],
                   ['beef' ,'beef' , 'meats',],
                   ['ground beef' ,'beef, ground' , 'meats',],
                   ['pork' ,'pork' , 'meats',],
                   ['turkey' ,'turkey' , 'meats',],
                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
# Each unit is of the following format:
# ("unit1","unit2"):conversion_factor, where unit1 contains conversion_factor X unit2
# For example: 1 cup has 16 tablespoons.
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
    ("fl. oz.","tbs."):2,
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
# Translators: You may be best off translating the food names below, since lists
# of food densities can be hard to come by!
DENSITY_TABLE={
    "water":1,
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
UNITS = [["bucket" , ["bucket", "buckets", "bckt."]],
         ["peck", ["peck", "pecks"]],
         ["bushel", ["bushel", "bushels", "bsh.", "bu.", "bu", "bsh", "bshl", "bshl."]],
         ["grains", ["grain", "grains"]],
         ["dram", ["dram", "drams"]],
         ["drop",["drop"]],
         ["fl. oz.",["fl oz","fluid ounce","fluid ounces","fl. oz.","fl oz.","fl. oz"]],
         ['',['each','ea','ea.']],
         ["tsp.", ["teaspoon","tsp", "tsp.","tea spoon", "tsps.", "teaspoons", "tea spoons", "Teaspoon", "Teaspoons","t",'ts',"Ts.","Tsp.","Tsp"]],
         ["Tbs.", ["tablespoon","tbs", "tbsp", "tbs.", "tbsp.", "table spoon", "tbsps.", "tablespoons", "Tablespoon", "T",'tb',"Tbs.", "Tbsp", "Tbsp."]],
         ["lb.", [ "pound", "lb","lb.", "lbs.", "pounds"]],
         ["oz.", [ "ounce", "oz","ounces", "oz."]],
         ["c.", ["cup", "c.", "cups"]],
         ["qt.", ["quart", "qt.", "quarts","Qt","Qt."]],
         ["pt.", ["pint", "pt.", "pints"]],
         ["gallon", ["gallon", "gallons","gal."]],
         ["ml.", ["mililiter","ml", "ml.","mililiters"]],
         ["cl.", ["centiliter","cl", "cl.", "centiliters"]],
         ["dl.", ["deciliter","dl", "dl.","deciliters"]],
         ["l.", ["liter", "l.", "lit.", "liters",'l']],
         ["g.", ["grams", "gram", "g.",'g']],
         ["mg.", ["miligram", "mg.", "mg", "miligrams"]],
         ["kg.", ["kilogram","kg.", "kg", "kilograms"]],
         # These names aren't really convertible, but we want them to
         # be recognized as units...
         ['small',['small','sm','Small','sm.']],         
         ['medium',['medium','med.','Medium']],
         ['large',['large','Large','lg','lg.']],
         ['clove',['clove','cloves','clv.']],
         ['whole',['whole','wh.','whl']],
         ['package',['pkg.','pkg','package','Pkg.','Package','pack']],
         ['box',['Box','box','bx']],
         ['can',['can','Can','cn','cn.']],
         ['slices',['slice','slices']],
         ]

METRIC_RANGE = (1,999)

# The following sets up unit groups. Users will be able to turn
# these on or off (American users, for example, would likely turn
# off metric units, since we don't use them).
# (User choice not implemented yet)
UNIT_GROUPS = {
    'metric mass':[('mg.',METRIC_RANGE),
                   ('g.',METRIC_RANGE),
                   ('kg.',(1,None))],
    'metric volume':[('ml.',METRIC_RANGE),
                     ('cl.',(1,99)),
                     ('dl.',(1,9)),
                     ('l.',(1,None)),],
    'imperial weight':[('grains',(0,27)),
                       ('dram',(0.5,15)),
                       ('oz.',(0.25,32)),
                       ('lb.',(0.25,None)),
                       ],
    'imperial volume':[('drop',(0,3)),
                       ('tsp.',(0.125,3)),
                       ('Tbs.',(1,4)),
                       ('c.',(0.25,6)),
                       ('pt.',(1,1)),
                       ('qt.',(1,3)),
                       ('gallon',(1,None)),
                       ('peck',(1,2)),
                       ('bucket',(1,2)),
                       ('bushel',(1,None)),
                       ('fl oz',(1,None)),
                       ]
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
    ("Tbs.", "oz."):['density',0.5],
    ("c.", "oz."):['density',8],
    ("pt.", "oz."):['density',16],
    ("ml.", "g."):['density',1],
    ('oz.','fl. oz.'):['density',1],
    }

# The units here need to correspond to the standard unit names defined
# in UNITS.  These are some core conversions from mass-to-volume,
# assuming a density of 1 (i.e. the density of water).
VOL_TO_MASS_TABLE = {
    ("pt.", "lb.") : 1,
    ("Tbs.", "oz.") : 0.5,
    ("c.", "oz.") : 8,
    ("pt.", "oz.") : 16,
    ("ml.", "g.") : 1,
    ("ml.", "mg.") : 1000,
    ("ml.", "kg."): 0.001,
    ("cl.", "kg."): 0.01,
    ("cl.", "g.") : 10,
    ("dl.", "kg.") : 0.1,
    ("dl.", "g.") : 100,    
    ("l.", "kg.") : 1}

# TIME ABBREVIATIONS (this is new!)
TIME_ABBREVIATIONS = {
    'sec':'seconds',
    'min':'minutes',
    'hr':'hours'
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
    (1.0/8):['eighth','an eigth'],
    (1.0/4):['quarter','a quarter'],
    (3.0/4):['three quarters'],
    (2.0/3):['two thirds'],
    (1.0/3):['third','a third'],
    (1.0/2):['one half','a half','half'],
    1:['an','a','one'],
    2:['two','a couple','a couple of','a pair of'],
    3:['three'],
    4:['four'],
    5:['five'],
    6:['six'],
    7:['seven'],
    8:['eight'],
    9:['nine'],
    10:['ten'],
    11:['eleven'],
    12:['twelve','a dozen'],
    20:['twenty'],
    30:['thirty'],
    40:['forty'],
    50:['fifty'],
    60:['sixty'],
    }
