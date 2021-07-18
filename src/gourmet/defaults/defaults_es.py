# -*- coding: utf-8 -*-
#
# we set up default information for our locale (Spanish)
# Translators should use this file as the basis of their translation.
# Copy this file and rename it for you locale.
#
# Language: Spanish
# Translator: Thomas M. Hinkle
# Last-updated: 4/27/05

from typing import Collection, List, Mapping

from .abstractLang import AbstractLanguage


class Language(AbstractLanguage):

    CREDITS="Thomas M. Hinkle"

    ## first, easy to maintain lists which can eventually be moved to
    ## files.

    # TRANSLATOR WARNING: DO NOT TRANSLATE THE FIELD NAMES: ONLY THE VALUES!!!
    fields={'cuisine': ['Española','Mejicana','Cubana','Argentina','Brazileña','Italiana','Griega',
                       'China','Francesa','Vasca','India', 'Inglesa'],
            'rating' : ['Excelente','Muy Bueno','Bueno','Así Así','Malo'],
            'source' : [],
            'category' : ['Postre','Aperitivo','Ensalada','Sopa',
                          'Desayuno','Plato principal','Tapa'],
                      }

    SYNONYMS=[
        # the first item of each list is the most common
        # word, the others are synonyms
        ['durazno','melocotón'],
        ['camarón','gamba'],
        ]

    # a dictionary key=ambiguous word, value=list of terms
    AMBIGUOUS: Mapping[str, List[str]] = {}


    # triplicates ITEM, KEY, SHOPPING CATEGORY
    INGREDIENT_DATA = [
        ("albahaca","albahaca",'especias'),
        ("ajedrea","ajedrea",'especias'),
        ("estragón","estragón",'especias'),
        ("laurel","laurel",'especias'),
        ("menta","menta",'especias'),
        ("salvia","salvia",'especias'),
        ("orégano","orégano",'especias'),
        ("romero","romero",'especias'),
        ("salvia","salvia",'especias'),
        ("tomillo","tomillo",'especias'),
        ("amapola","amapola",'especias'),
        ("anís","anís",'especias'),
        ("comino","comino",'especias'),
        ("mostaza","mostaza",'especias'),
        ("nuez moscada","moscada",'especias'),
        ("pimienta","pimienta",'especias'),
        ("el sésamo","sésamo",'especias'),
        ("canela","canela",'especias'),
        ("azafrán","azafrán",'especias'),
        ("clavo de olor","olor",'especias'),
        ("vainilla","vainilla",'especias'),
        ("rizoma","rizoma",'especias'),
        ("cúrcuma","cúrcuma",'especias'),
        ("jengibre","jengibre",'especias'),
        ("aceite","aceite",""),
        ("aceituna","aceituna",""),
        ("acelga","acelga",""),
        ("aguacate","aguacate",""),
        ("ají","ají",""),
        ("ajo","ajo",""),
        ("albaricoque","albaricoque",""),
        ("alcachofa","alcachofa",""),
        ("almeja","almeja",""),
        ("almendra","almendra",""),
        ("ananá","ananá",""),
        ("anchoa","anchoa",""),
        ("anguila","anguila",""),
        ("angula","angula",""),
        ("apio","apio",""),
        ("arándano","arándano",""),
        ("arenque","arenque",""),
        ("arroz","arroz",""),
        ("atún","atún",""),
        ("avellana","avellana",""),
        ("avena","avena",""),
        ("azúcar","azúcar",""),
        ("bacaladilla","bacaladilla",""),
        ("bacalao","bacalao",""),
        ("bacon","bacon",""),
        ("banana","banana",""),
        ("barbo","barbo",""),
        ("batata","batata",""),
        ("berberecho","berberecho",""),
        ("berenjena","berenjena",""),
        ("berro","berro",""),
        ("besugo","besugo",""),
        ("bogavante","bogavante",""),
        ("boniato","boniato",""),
        ("bonito","bonito",""),
        ("boquerón","boquerón",""),
        ("breca","breca",""),
        ("breva","breva",""),
        ("bróculi","bróculi",""),
        ("caballa","caballa",""),
        ("caballo","caballo",""),
        ("cabrito","cabrito",""),
        ("cacahuete","cacahuete",""),
        ("cacao","cacao",""),
        ("café","café",""),
        ("calabacín","calabacín",""),
        ("calabaza","calabaza",""),
        ("calamar","calamar",""),
        ("camarón","camarón",""),
        ("cangrejo","cangrejo",""),
        ("caracol","caracol",""),
        ("caramelo","caramelo",""),
        ("cardillo","cardillo",""),
        ("cardo","cardo",""),
        ("carpa","carpa",""),
        ("castaña","castaña",""),
        ("caviar","caviar",""),
        ("cebolla","cebolla",""),
        ("cebolleta","cebolleta",""),
        ("cecina","cecina",""),
        ("centeno","centeno",""),
        ("centollo","centollo",""),
        ("cerdo","cerdo",""),
        ("cereza","cereza",""),
        ("champiñón","champiñón",""),
        ("chile","chile",""),
        ("chiria","chiria",""),
        ("chirimoya","chirimoya",""),
        ("chirivia","chirivia",""),
        ("chirla","chirla",""),
        ("chocolate","chocolate",""),
        ("choclo","choclo",""),
        ("chorizo","chorizo",""),
        ("ciervo","ciervo",""),
        ("cigala","cigala",""),
        ("ciruela","ciruela",""),
        ("coco","coco",""),
        ("codorniz","codorniz",""),
        ("col","col",""),
        ("col de Bruselas","col de Bruselas",""),
        ("col lombarda","col lombarda",""),
        ("coliflor","coliflor",""),
        ("conejo","conejo",""),
        ("congrio","congrio",""),
        ("cuajada","cuajada",""),
        ("dátil","dátil",""),
        ("dorada","dorada",""),
        ("endibia","endibia",""),
        ("escarola","escarola",""),
        ("espárrago","espárrago",""),
        ("espagueti","espagueti",""),
        ("espinaca","espinaca",""),
        ("faisán","faisán",""),
        ("fiambre","fiambre",""),
        ("fideo","fideo",""),
        ("foie-gras","foie-gras",""),
        ("frambuesa","frambuesa",""),
        ("fresa","fresa",""),
        ("fresón","fresón",""),
        ("frutilla","frutilla",""),
        ("gallina","gallina",""),
        ("gallo","gallo",""),
        ("gamba","gamba",""),
        ("ganso","ganso",""),
        ("garbanzo","garbanzo",""),
        ("gofio","gofio",""),
        ("granada","granada",""),
        ("grelo","grelo",""),
        ("grosella","grosella",""),
        ("guinda","guinda",""),
        ("guisante","guisante",""),
        ("haba","haba",""),
        ("harina de arroz","harina de arroz",""),
        ("harina de avena","harina de avena",""),
        ("harina de centeno","harina de centeno",""),
        ("harina de maíz","harina de maíz",""),
        ("harina de soja","harina de soja",""),
        ("harina de trigo","harina de trigo",""),
        ("higo","higo",""),
        ("hueva","hueva",""),
        ("huevo","huevo",""),
        ("jabalí","jabalí",""),
        ("jamón","jamón",""),
        ("judía blanca","judía blanca",""),
        ("judía pinta","judía pinta",""),
        ("judía verde","judía verde",""),
        ("jurel","jurel",""),
        ("kiwi","kiwi",""),
        ("langosta (crustáceo)","langosta (crustáceo)",""),
        ("leche","leche",""),
        ("lechuga","lechuga",""),
        ("lenguado","lenguado",""),
        ("lenteja","lenteja",""),
        ("levadura","levadura",""),
        ("liebre","liebre",""),
        ("limón","limón",""),
        ("lubina","lubina",""),
        ("macarrón","macarrón",""),
        ("maíz","maíz",""),
        ("malta","malta",""),
        ("mandarina","mandarina",""),
        ("mandioca","mandioca",""),
        ("mango","mango",""),
        ("manteca","manteca",""),
        ("mantequilla","mantequilla",""),
        ("manzana","manzana",""),
        ("margarina","margarina",""),
        ("mazorca","mazorca",""),
        ("mejillón","mejillón",""),
        ("melaza","melaza",""),
        ("melocotón","melocotón",""),
        ("melón","melón",""),
        ("membrillo","membrillo",""),
        ("merluza","merluza",""),
        ("mero","mero",""),
        ("miel","miel",""),
        ("mora","mora",""),
        ("morcilla","morcilla",""),
        ("mortadela","mortadela",""),
        ("nabo","nabo",""),
        ("naranja","naranja",""),
        ("nata","nata",""),
        ("navaja","navaja",""),
        ("nécora","nécora",""),
        ("níspero","níspero",""),
        ("nuez","nuez",""),
        ("ostra","ostra",""),
        ("paloma","paloma",""),
        ("palometa","palometa",""),
        ("pan","pan",""),
        ("panceta","panceta",""),
        ("papa","papa",""),
        ("pasta","pasta",""),
        ("paté","paté",""),
        ("pato","pato",""),
        ("pavo","pavo",""),
        ("pepino","pepino",""),
        ("pera","pera",""),
        ("perca","perca",""),
        ("percebe","percebe",""),
        ("perdiz","perdiz",""),
        ("pescadilla","pescadilla",""),
        ("pez espada","pez espada",""),
        ("pimiento","pimiento",""),
        ("piña","piña",""),
        ("piñón","piñón",""),
        ("pistacho","pistacho",""),
        ("plátano","plátano",""),
        ("platija","platija",""),
        ("pollo","pollo",""),
        ("pomelo","pomelo",""),
        ("puerro","puerro",""),
        ("pulpo","pulpo",""),
        ("queso","queso",""),
        ("rábano","rábano",""),
        ("rape","rape",""),
        ("raya","raya",""),
        ("remolacha","remolacha",""),
        ("repollo","repollo",""),
        ("rodaballo","rodaballo",""),
        ("salchicha","salchicha",""),
        ("salchichón","salchichón",""),
        ("salmón","salmón",""),
        ("salmonete","salmonete",""),
        ("sandía","sandía",""),
        ("sardinas","sardinas",""),
        ("sargo","sargo",""),
        ("sémola","sémola",""),
        ("setas","setas",""),
        ("soda","soda",""),
        ("soja","soja",""),
        ("tapioca","tapioca",""),
        ("tomate","tomate",""),
        ("toronja","toronja",""),
        ("trucha","trucha",""),
        ("uva","uva",""),
        ("vieira","vieira",""),
        ("yoghurt","yoghurt",""),
        ("yuca","yuca",""),
        ]

    CONVERTER_TABLE = {
        ("tazas", "tbs."):16,
        ("libra", "onza"):16,
        ("cucharada", "cucharadita"):3,
        ("pt.", "tazas"):2,
        ("qt.", "tazas"):4,
        ("galón", "quarto de galón"):4,
        ("l", "quarto de galón"):1.057,
        ("l", "ml"):1000,
        ("l", "cl"):100,
        ("l", "dl"):10,
        ("onza", "g"):28.35,
        ("kg", "g"):1000,
        ("g", "mg"):1000,
        ("cucharadita", "drop"):76,
        # Are there translations for these units?   Not really, they're english-imperial units, not adopted by Spain...  :-)
        # ("onza", "dram"):16,
        # ("dram", "grains"):27.34375,
        # ("peck", "galón"):2,
        # ("bucket", "peck"):2,
        # ("bushel", "bucket"):2,
        # ("lb.", "grains"):7000,
        }

    METRIC_RANGE = (1,999)

    UNIT_GROUPS = {
        'metric mass':[('mg',METRIC_RANGE),
                       ('g',METRIC_RANGE),
                       ('kg',(1,None))],
        'metric volume':[('ml',METRIC_RANGE),
                         ('cl',(1,99)),
                         ('dl',(1,9)),
                         ('l',(1,None)),],
        'imperial weight':[
        # ('grain',(0,27)),
        # ('dram',(0.5,15)),
        ('onza',(0.25,15)),
        ('libra',(0.25,None)),
        ],
        'imperial volume':[
        #('drop',(0,10)),
        ('cucharadita',(0.125,3)),
        ('cucharada',(1,4)),
        ('taza',(0.25,4)),
        # ('pt.',(1,1)),
        ('quarto de galón',(1,3)),
        ('galón',(1,None)),
        # ('peck',(1,2)),
        # ('bucket',(1,2)),
        # ('bushel',(1,None))
        ]
        }

    DENSITY_TABLE={
        "agua":1,
        "zumo":1.03,
        "caldo":1,
        "leche":1.029,
        "leche entera":1.029,
        "leche desnatada":1.033,
        # "milk, 2%":1.031,
        # "milk, 1%":1.03,
        "leche de coco":0.875,
        "suero de la leche":1.03,
        # heavy cream -- I don't know the differences in Sp.
        "crema":0.994,
        # "light cream":1.012,
        # "half and half":1.025,
        "miel":1.420,
        "azúcar":1.550,
        "sal":2.165,
        "mantequilla":0.911,
        "aceite vegetal":0.88,
        "aceite de oliva":0.88,
        "aceite de sésame":0.88,
        "harina": 0.6,
        "harina de trigo entero": 0.6,
        "almidón de maíz": 0.6,
        "azúcar impalpable": 0.6,
                }

    UNITS = [
        ("ml", ["ml.", "mL", "mL.", "ml"]),
        # ["bucket" , ["bucket", "buckets", "bckt."]],
        # ["peck", ["peck", "pecks"]],
        # ["bushel", ["bushel", "bushels", "bsh.", "bu.", "bu", "bsh", "bshl", "bshl."]],
        # ["grains", ["grain", "grains"]],
        # ["dram", ["dram", "drams"]],
        ("cucharadita", ["cucharadita"]),
        ("cucharada", ["cucharada","tbs", "tbsp","tbsp.", "tablespoon", "table spoon", "tbsps.", "tablespoons", "Tablespoon", "T"]),
        ("libra", ["libra","libras"]),
        ("onza", ["onza","onzas"]),
        ("taza", ["taza","tazas"]),
        ("quarto de galón", ["quarto de galón","quarto"]),
        # ["pt.", ["pint", "pt.", "pints"]],
        ("galón", ["galón", "galones", "gal."]),
        ("ml", ["ml", "ml.", "mililitro", "mililitros"]),
        ("cl", ["cl", "cl.", "centilitro", "centilitros"]),
        ("dl", ["dl", "dl.", "decilitro", "decilitros"]),
        ("l", ["litro", "l.", "lit.", "litros"]),
        ("g", ["gramos", "gramo", "g.","gr.","g","gr"]),
        ("mg", ["mg.", "mg", "miligramo", "miligramos"]),
        ("kg", ["kg.", "kg", "kilogramo", "kilogramos"]),
        ]

    CROSS_UNIT_TABLE = {
        ## This if for units that require an additional
        ## bit of information -- i.e. to convert between
        ## volume and mass you need the density of an
        ## item.  In these cases, the additional factor
        ## will be provided as an 'item' that is then looked
        ## up in the dictionary referenced here (i.e. the density_table)
        ## currently, 'density' is the only keyword used
        ("pt.", "lb."):('density',1),
        ("cucharada", "onza"):('density',0.5),
        ("taza", "onza"):('density',8),
        # ("pt.", "onza"):('density',16),
        ("ml", "g"):('density',1)}

    VOL_TO_MASS_TABLE = {
        ("pt.", "lb.") : 1,
        ("cucharada", "onza") : 0.5,
        ("tazas", "onza") : 8,
        ("pt.", "onza") : 16,
        ("ml", "g") : 1,
        ("ml", "mg") : 1000,
        ("ml", "kg"): 0.001,
        ("cl", "kg"): 0.01,
        ("cl", "g") : 10,
        ("dl", "kg") : 0.1,
        ("dl", "g") : 100,
        ("l", "kg") : 1}

    TIME_ABBREVIATIOSN = {
        'hrs' : 'horas',
        'hra' : 'horas',
        'mntas' : 'minutas',
        'mnta' : 'minutas',
        }

    # These functions are rather important! Our goal is simply to
    # facilitate look ups -- if the user types in "tomatoes", we want to
    # find "tomato." Note that the strings these functions produce will
    # _never_ be shown to the user, so it's fine to generate nonsense
    # words as well as correct answers -- our goal is to generate a list
    # of possible hits rather than to get the plural/singular form "right".

    @staticmethod
    def guess_singulars (s):
        if len(s)<3: return []
        rets = []
        if s[-1]=='s':
            rets.append(s[0:-1])
            if s[-2]=='e':
                rets.append(s[0:-2])
        return rets

    @staticmethod
    def guess_plurals (s):
        return [s+'s',s+'es']

    IGNORE: Collection[str] = []

    NUMBERS = {
        (1.0/8):['octavo','un octavo'],
        (1.0/4):['cuarto','un cuarto'],
        (3.0/4):['tres cuartos'],
        (2.0/3):['dos tercios'],
        (1.0/3):['un tercio',],
        (1.0/2):['una mitad','la mitad'],
        1:['un','una','uno'],
        2:['dos','un par','un par de'],
        3:['tres'],
        4:['cuatro'],
        5:['cinco'],
        6:['seis'],
        7:['siete'],
        8:['ocho'],
        9:['nueve'],
        10:['diez'],
        11:['once'],
        12:['doce','una docena','una dozena','una docena de','una dozena de'],
        20:['veinte'],
        30:['treinta'],
        40:['cuarenta'],
        50:['cincuenta'],
        60:['sesenta'],
        100:['cien'],
        }
