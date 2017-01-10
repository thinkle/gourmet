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

# Language: Russian
# Translator: Alexandre Prokoudine <alexandre.prokoudine[NOSPAM]gmail.com
# Last-updated: July 12, 2009

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

fields={'cuisine': ['Американская','Итальянская','Мексиканская',
                    'Юго-западная','Азиатская/Тайская','Азиатская/Вьетнамская',
                    'Азиатская/Китайская','Азиатская/Японская',],
        'rating' : ['Превосходно','Отлично','Хорошо','Сойдет','Ужасно'],
        'source' : [],
        'category' : ['Десерт','Основное блюдо','Салат','Суп',
                      'Завтрак'],
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
    ['sugar, granulated','sugar'],
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

INGREDIENT_DATA = [["авокадо","авокадо","produce"],
                   ["анис","анис","produce"],
                   ["артишок","артишок","produce"],
                   ["арум","аронник","produce"],
                   ["баклажан","баклажан","produce"],
                   ["брокколи","капуста спаржевая","produce"],
                   ["брюква","брюква","produce"],
                   ["васаби","васаби","produce"],
                   ["горох","горох","produce"],
                   ["грибы","грибы","produce"],
                   ["зеленый перец","bell pepper, green","produce"],
                   ["имбирь","имбирь","produce"],
                   ["капуста брюссельская","капуста брюссельская","produce"],
                   ["капуста кормовая","капуста кормовая","produce"],
                   ["капуста кочанная","капуста кочанная","produce"],
                   ["капуста цветная","капуста цветная","produce"],
                   ["картофель","картофель","produce"],
                   ["кольраби","кольраби","produce"],
                   ["кормовые бобы","кормовые бобы","produce"],
                   ["крапива","крапива","produce"],
                   ["кресс водяной","кресс водяной","produce"],
                   ["лимская фасоль","butter bean","produce"],
                   ["лук-порей","лук-порей","produce"],
                   ["лук-резанец","лук-резанец","produce"],
                   ["лук репчатый","лук репчатый","produce"],
                   ["лук-шалот","лук-шалот","produce"],
                   ["мангольд","мангольд","produce"],
                   ["маниока","маниока","produce"],
                   ["морковь","морковь","produce"],
                   ["новозеландский шпинат","новозеландский шпинат","produce"],
                   ["огурец","огурец","produce"],
                   ["окра","окра","produce"],
                   ["пастернак","пастернак","produce"],
                   ["петрушка","петрушка","produce"],
                   ["плод хлебного дерева","плод хлебного дерева","produce"],
                   ["ревень","ревень","produce"],
                   ["редис белый","редис белый","produce"],
                   ["редис","редис","produce"],
                   ["репа","репа","produce"],
                   ["реснички","реснички","produce"],
                   ["салат-латук","салат-латук","produce"],
                   ["свекла","свекла","produce"],
                   ["сельдерей корневой","сельдерей корневой","produce"],
                   ["сельдерей","сельдерей","produce"],
                   ["сладкий картофель","сладкий картофель","produce"],
                   ["сладкий укроп","фенхель обыкновенный","produce"],
                   ["соевые бобы","соевые бобы","produce"],
                   ["спаржа","спаржа","produce"],
                   ["таро","таро","produce"],
                   ["томат","томат","produce"],
                   ["топинамбур","топинамбур","produce"],
                   ["турецкий горох","турецкий горох","produce"],
                   ["тыква","тыква","produce"],
                   ["фасоль обыкновенная","фасоль обыкновенная","produce"],
                   ["цукини","zucchini","produce"],
                   ["чеснок","чеснок","produce"],
                   ["чечевица","чечевица","produce"],
                   ["чилийский перец","перец, чилийский","produce"],
                   ["шпинат","шпинат","produce"],
                   ["эндивий","эндивий","produce"],
                   ["ям","ям","produce"],
#                   ["alfalfa sprouts","alfalfa sprouts","produce"].
#                   ["acorn squash","squash, acorn","produce"],
#                   ["azuki beans","azuki beans","produce"],
#                   ["bean sprouts","bean sprouts","produce"],
#                   ["black beans","black beans","produce"],
#                   ["black-eyed peas","black-eyed peas","produce"],
#                   ["bok choy","bok choy","produce"],
#                   ["borlotti beans","borlotti beans","produce"],
#                   ["broccoflower","broccoflower","produce"],
#                   ["butternut squash","squash, butternut","produce"],
#                   ["calabrese","calabrese","produce"],
#                   ["collard greens","collard greens","produce"],
#                   ["corn","corn","produce"],
#                   ["corn salad","corn salad","produce"],
#                   ["daikon","daikon","produce"],
#                   ["fiddleheads","fiddleheads","produce"],
#                   ["frisee","frisee","produce"],
#                   ["gem squash","squash, gem","produce"],
#                   ["green beans","green beans","produce"],
#                   ["green beans","green beans","produce"],
#                   ["habanero pepper","pepper, habanero","produce"],
#                   ["jalapeño pepper","pepper, jalapeño","produce"],
#                   ["jicama","jicama","produce"],
#                   ["lemon grass","lemon grass","produce"],
#                   ["mung beans","mung beans","produce"],
#                   ["mustard greens","mustard greens","produce"],
#                   ["navy beans","navy beans","produce"],
#                   ["onion family","onion family","produce"],
#                   ["patty pans","patty pans","produce"],
#                   ["radicchio","radicchio","produce"],
#                   ["rapini","rapini","produce"],
#                   ["red bell pepper","bell pepper, red","produce"],
#                   ["root vegetables","root vegetables","produce"],
#                   ["runner beans","runner beans","produce"],
#                   ["scallion","scallion","produce"],
#                   ["skirret","skirret","produce"],
#                   ["snap peas","snap peas","produce"],
#                   ["spaghetti squash","squash, spaghetti","produce"],
#                   ["tat soi","tat soi","produce"],
#                   ["water chestnut","water chestnut","produce"],
                   # fruits, from wikipedia list
#                   ["bilberry","bilberry","produce"],
#                   ["buffaloberry","buffaloberry","produce"],
#                   ["camucamu","camucamu","produce"],
#                   ["cempedak","cempedak","produce"],
#                   ["cherimoya","cherimoya","produce"],
#                   ["citron","citron","produce"],
#                   ["clementine","clementine","produce"],
#                   ["custard apple","custard apple","produce"],
#                   ["dragonfruit","dragonfruit","produce"],
#                   ["elderberry ","elderberry ","produce"],
#                   ["gooseberry ","gooseberry ","produce"],
#                   ["goumi","goumi","produce"],
#                   ["green apple","green apple","produce"],
#                   ["honeydew","honeydew","produce"],
#                   ["huckleberry","huckleberry","produce"],
#                   ["keppel fruit","keppel fruit","produce"],
#                   ["key lime","key lime","produce"],
#                   ["langsat","langsat","produce"],
#                   ["longan","longan","produce"],
#                   ["mamey sapote","mamey sapote","produce"],
#                   ["mamoncillo","mamoncillo","produce"],
#                   ["nannyberry","nannyberry","produce"],
#                   ["passion fruit","passion fruit","produce"],
#                   ["pawpaw","pawpaw","produce"],
#                   ["peanut butter fruit","peanut butter fruit","produce"],
#                   ["pitaya","pitaya","produce"],
#                   ["poha","poha","produce"],
#                   ["pommelo","pommelo","produce"],
#                   ["prickly pear ","prickly pear ","produce"],
#                   ["rose apple","rose apple","produce"],
#                   ["salak","salak","produce"],
#                   ["sapodilla","sapodilla","produce"],
#                   ["sea-buckthorn","sea-buckthorn","produce"],
#                   ["star fruit","star fruit","produce"],
#                   ["sugar apple","sugar apple","produce"],
#                   ["sunberry","sunberry","produce"],
#                   ["ugli fruit","ugli fruit","produce"],
#                   ["wineberry","wineberry","produce"],
                   ["абрикос","абрикос","produce"],
                   ["айва","айва","produce"],
                   ["американская хурма","хурма, американская","produce"],
                   ["ананас","ананас","produce"],
                   ["ангелика","ангелика","produce"],
                   ["анона игольчатая","анона игольчатая","produce"],
                   ["апельсин","апельсин","produce"],
                   ["арбуз","арбуз","produce"],
                   ["арония","арония","produce"],
                   ["банан","банан","produce"],
                   ["барбарис","барбарис","produce"],
                   ["бархатная хурма","хурма, бархатная","produce"],
                   ["белая смородина","смородина, белая","produce"],
                   ["бойзенова ягода","бойзенова ягода","produce"],
                   ["боярышник","боярышник","produce"],
                   ["брусника","брусника","produce"],
                   ["виноград","виноград","produce"],
                   ["вишня","вишня","produce"],
                   ["водосбор","водосбор","produce"],
                   ["волчья ягода","волчья ягода","produce"],
                   ["вороника","вороника","produce"],
                   ["голубика","голубика","produce"],
                   ["гранат","гранат","produce"],
                   ["гранат","гранат","produce"],
                   ["грейпфрут","грейпфрут","produce"],
                   ["гуава","гуава","produce"],
                   ["гуарана","гуарана","produce"],
                   ["джекфрут","джекфрут","produce"],
                   ["дуриан","дуриан","produce"],
                   ["ежевика","ежевика","produce"],
                   ["индийский финик","индийский финик","produce"],
                   ["ирга","ирга","produce"],
                   ["киви","киви","produce"],
                   ["клубника ","клубника ","produce"],
                   ["клюква","клюква","produce"],
                   ["кокосовый орех","кокосовый орех","produce"],
                   ["красная смородина","смородина, красная","produce"],
                   ["кумкват","кумкват","produce"],
                   ["лайм","лайм","produce"],
                   ["лимон","лимон","produce"],
                   ["локва","локва","produce"],
                   ["малина","малина","produce"],
                   ["манго","манго","produce"],
                   ["мангустан","мангустан","produce"],
                   ["мандарин","мандарин","produce"],
                   ["марабу","марабу","produce"],
                   ["медвежья ягода","медвежья ягода","produce"],
                   ["морошка","морошка","produce"],
                   ["мускусная дыня","мускусная дыня","produce"],
                   ["мушмула","мушмула","produce"],
                   ["нектарин","нектарин","produce"],
                   ["нефелиум","нефелиум","produce"],
                   ["нефелиум","нефелиум","produce"],
                   ["папайя","папайя","produce"],
                   ["персик","персик","produce"],
                   ["плод хлебного дерева","плод хлебного дерева","produce"],
                   ["плод шиповника","плод шиповника","produce"],
                   ["подорожник","подорожник","produce"],
                   ["ревень","ревень","produce"],
                   ["рябина","рябина","produce"],
                   ["слива","слива","produce"],
                   ["танжело","танжело","produce"],
                   ["танжерин","танжерин","produce"],
                   ["фейхоа","фейхоа","produce"],
                   ["фига","фига","produce"],
                   ["финик","финик","produce"],
                   ["хурма","хурма","produce"],
                   ["цереус гигантский","цереус гигантский ","produce"],
                   ["черная смородина","смородина, черная","produce"],
                   ["черная шелковица","черная шелковица","produce"],
                   ["шелковица","шелковица","produce"],
                   ["ююба","ююба","produce"],
                   ["яблоко-кислица","яблоко-кислица","produce"],
                   ["яблоко","яблоко","produce"],
                   ## seafood, from wikipedia list
#                   ["black cod","black cod","морепродукты"],
#                   ["blowfish","blowfish","морепродукты"],
#                   ["catfish","catfish","морепродукты"],
#                   ["clam","clam","морепродукты"],
#                   ["dungness crab","dungness crab","морепродукты"],
#                   ["halibut","halibut","морепродукты"],
#                   ["king crab","king crab","морепродукты"],
#                   ["lingcod","lingcod","морепродукты"],
#                   ["mahi mahi","mahi mahi","морепродукты"],
#                   ["monkfish","monkfish","морепродукты"],
#                   ["orange roughy","orange roughy","морепродукты"],
#                   ["pacific snapper","pacific snapper","морепродукты"],
#                   ["prawns","prawns","морепродукты"],
#                   ["red snapper","red snapper","морепродукты"],
#                   ["rock cod","rock cod","морепродукты"],
#                   ["rockfish","rockfish","морепродукты"],
#                   ["roe","roe","морепродукты"],
#                   ["snapper","snapper","морепродукты"],
#                   ["sole","sole","морепродукты"],
#                   ["surimi","surimi","морепродукты"],
#                   ["tilapia","tilapia","морепродукты"],
#                   ["tilefish","tilefish","морепродукты"],
#                   ["whitefish","whitefish","морепродукты"],
                   ["акула","акула","морепродукты"],
                   ["анчоус","анчоус","морепродукты"],
                   ["гребешок","гребешок","морепродукты"],
                   ["икра","икра","морепродукты"],
                   ["икра лосося","икра лосося","морепродукты"],
                   ["кальмар","кальмар","морепродукты"],
                   ["камбала","камбала","морепродукты"],
                   ["камбала-лиманда","камбала-лиманда","морепродукты"],
                   ["краб","краб","морепродукты"],
                   ["креветка","креветка","морепродукты"],
                   ["мерланг","мерланг","морепродукты"],
                   ["меч-рыба","меч-рыба","морепродукты"],
                   ["мидия","мидия","морепродукты"],
                   ["морское ушко","морское ушко","морепродукты"],
                   ["морской окунь","морской окунь","морепродукты"],
                   ["окунь","окунь","морепродукты"],
                   ["омар","омар","морепродукты"],
                   ["осетр","осетр","морепродукты"],
                   ["осьминог","осьминог","морепродукты"],
                   ["пикша","пикша","морепродукты"],
                   ["полосатый окунь","полосатый окунь","морепродукты"],
                   ["речной рак","речной рак","морепродукты"],
                   ["сайда","сайда","морепродукты"],
                   ["сардина","сардина","морепродукты"],
                   ["семга","семга","морепродукты"],
                   ["снежный краб","снежный краб","морепродукты"],
                   ["треска","треска","морепродукты"],
                   ["тунец","тунец","морепродукты"],
                   ["угорь","угорь","морепродукты"],
                   ["улитка","улитка","морепродукты"],
                   ["устрица","устрица","морепродукты"],
                   ["форель","форель","морепродукты"],
                   ["чилийский морской окунь","чилийский морской окунь","морепродукты"],
                   ["щука","щука","морепродукты"],
                   ## meats (garnered from wikipedia lists)
                   ["fuet","fuet","мясо"],
                   ["veal","veal","мясо"],
                   ["баранина","баранина","мясо"],
                   ["бекон","бекон","мясо"],
                   ["ветчина","ветчина","мясо"],
                   ["гамбургер","гамбургер","мясо"],
                   ["гусь","гусь","мясо"],
                   ["индейка","индейка","мясо"],
                   ["молодая баранина","молодая баранина","мясо"],
                   ["ростбиф","ростбиф","мясо"],
                   ["салями","салями","мясо"],
                   ["стейк","steak","мясо"],
                   ["утка","утка","мясо"],
                   ["цыпленок","цыпленок","мясо"],
                   ["чоризо","чоризо","мясо"],
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
                   ['whole rock cod or snapper','whole rock cod or snapper', 'морепродукты',],
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
                   ['monkfish','monkfish', 'морепродукты',],
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
                   ['granulated sugar','sugar, granulated', 'baking',],
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
                   ['salmon','salmon', 'морепродукты',],
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
                   ['chicken breast' ,'chicken, breast' , 'мясо',],
                   ['whole chicken' ,'chicken, whole' , 'мясо',],
                   ['chicken leg' ,'chicken, leg' , 'мясо',],
                   ['beef' ,'beef' , 'мясо',],
                   ['ground beef' ,'beef, ground' , 'мясо',],
                   ['pork' ,'pork' , 'мясо',],
                   ['turkey' ,'turkey' , 'мясо',],
                   ]

# THESE ARE STANDARD UNIT CONVERSIONS. You can simply translate unit names where
# you know them. Eliminate entries that are untranslatable or don't exist in your
# locale. And please add any additional units that you know of.
# Each unit is of the following format:
# ("unit1","unit2"):conversion_factor, where unit1 contains conversion_factor X unit2
# For example: 1 cup has 16 tablespoons.
CONVERTER_TABLE = {
    ("c", "Tbs"):16,
    ("lb", "oz"):16,
    ("Tbs", "tsp"):3,
    ("pt", "c"):2,
    ("qt", "c"):4,
    ("gallon", "qt"):4,
    ("l", "qt"):1.057,
    ("l", "ml"):1000,
    ("l", "cl"):100,
    ("l", "dl"):10,
    ("oz", "g"):28.35,
    ("fl oz","Tbs"):2,
    ("kg", "g"):1000,
    ("g", "mg"):1000,
    ("tsp", "drop"):76,
    ("oz", "dram"):16,
    ("dram", "grains"):27.34375,
    ("peck", "gallon"):2,
    ("bucket", "peck"):2,
    ("bushel", "bucket"):2,
    ("lb", "grains"):7000}

# DENSITIES of common foods. This allows us to convert between mass and volume.
# Translators: You may be best off translating the food names below, since lists
# of food densities can be hard to come by!
DENSITY_TABLE={
    "вода":1,
    "сок, виноградный":1.03,
    "vegetable broth":1,
    "broth, vegetable":1,
    "бульон, куриный":1,
    "молоко":1.029,
    "молоко, цельное":1.029,
    "молоко, пена":1.033,
    "молоко, 2%":1.031,
    "молоко, 1%":1.03,
    "кокосовое молоко":0.875,
    "пахта":1.03,
    "жирные сливки":0.994,
    "light cream":1.012,
    "half and half":1.025,
    "мед":1.420,
    "сахар-песок":1.550,
    "соль":2.165,
    "масло":0.911,
    "масло растительное":0.88,
    "масло оливковое":0.88,
    "кукурузное масло":0.88,
    "кунжутное масло":0.88,
    "мука общего назначения": 0.6,
    "мука пшеничная": 0.6,
    "крахмал кукурузный": 0.6,
    "сахарная пудра": 0.6
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
         ["fl oz",["fl oz","fluid ounce","fluid ounces","fl. oz.","fl oz.","fl. oz"]],
         ['',['each','ea','ea.']],
         ["tsp", ["teaspoon","tsp", "tsp.","tea spoon", "tsps.", "teaspoons", "tea spoons", "Teaspoon", "Teaspoons","t",'ts',"Ts.","Tsp.","Tsp"]],
         ["Tbs", ["tablespoon","tbs", "tbsp", "tbs.", "tbsp.", "table spoon", "tbsps.", "tablespoons", "Tablespoon", "T",'tb',"Tbs.", "Tbsp", "Tbsp."]],
         ["lb", [ "pound", "lb","lb.", "lbs.", "pounds"]],
         ["oz", [ "ounce", "oz","ounces", "oz."]],
         ["c", ["cup", "c.", "cups"]],
         ["qt", ["quart", "qt.", "quarts","Qt","Qt."]],
         ["pt", ["pint", "pt.", "pints"]],
         ["gallon", ["gallon", "gallons","gal."]],
         ["мл", ["миллилитр","мл", "мл","миллилитр"]],
         ["сл", ["сантилитр","сл", "сл", "сантилитр"]],
         ["дл", ["децилитр","дл", "дл","децилитр"]],
         ["л", ["литр", "л", "л", "литров",'литр']],
         ["г", ["грамм", "грамм", "г",'г','г','грамм']],
         ["мг", ["миллиграмм", "мг", "мг", "миллиграмм"]],
         ["кг", ["килограмм","кг", "кг", "килограмм"]],
         # These names aren't really convertible, but we want them to
         # be recognized as units...
         ['мало', ['мало']],
         ['средне', ['средне']],
         ['много', ['много']],
         ['луковица', ['луковица','луковиц']],
         ['целый', ['целый','целое','целая']],
         ['упаковка',['упаковка','пакет']],
         ['ящик', ['ящик']],
         ['банка', ['банка']],
         ['ломтей', ['ломтей','ломоть','ломти']],
         ]

METRIC_RANGE = (1,999)

# The following sets up unit groups. Users will be able to turn
# these on or off (American users, for example, would likely turn
# off metric units, since we don't use them).
# (User choice not implemented yet)
UNIT_GROUPS = {
    'metric mass':[('мг',METRIC_RANGE),
                   ('г',METRIC_RANGE),
                   ('кг',(1,None))],
    'metric volume':[('мл',METRIC_RANGE),
                     ('сл',(1,99)),
                     ('дл',(1,9)),
                     ('л',(1,None)),],
#    'imperial weight':[('grains',(0,27)),
#                       ('dram',(0.5,15)),
#                       ('oz',(0.25,32)),
#                       ('lb',(0.25,None)),
#                       ],
#    'imperial volume':[('drop',(0,3)),
#                       ('tsp',(0.125,5.9)),
#                       ('Tbs',(1,4)),
#                       ('c',(0.25,6)),
#                       ('pt',(1,1)),
#                       ('qt',(1,3)),
#                       ('gallon',(1,None)),
#                       ('peck',(1,2)),
#                       ('bucket',(1,2)),
#                       ('bushel',(1,None)),
#                       ('fl oz',(1,None)),
#                       ]
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
    ("pt", "lb"):['density',1],
    ("Tbs", "oz"):['density',0.5],
    ("c", "oz"):['density',8],
    ("pt", "oz"):['density',16],
    ("ml", "g"):['density',1],
    ('oz','fl oz'):['density',1],
    }

# The units here need to correspond to the standard unit names defined
# in UNITS.  These are some core conversions from mass-to-volume,
# assuming a density of 1 (i.e. the density of water).
VOL_TO_MASS_TABLE = {
    ("pt", "lb") : 1,
    ("Tbs", "oz") : 0.5,
    ("c", "oz") : 8,
    ("pt", "oz") : 16,
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
    'с':'секунд',
    'мин':'минут',
    'ч':'часов'
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
