from gourmet import convert
import re
from html_helpers import *

SUPPORTED_URLS = ['www.epicurious.com']
SUPPORTED_URLS_REGEXPS = []

ingredient_parser = IngredientParser(group_match={'tag':re.compile('^b$',re.IGNORECASE),},
                                     ing_block_match={'string':re.compile('(.*\n?)+')},
                                     ing_match={'tag':re.compile('.*'),
                                                'string':re.compile('.*'),
                                                }
                                     )

STOCK_NOTES_REGEXPS = [re.compile(regexp.replace(' ','(&nbsp|\s+)*'),re.IGNORECASE) for regexp in [
    'rate this recipe',
    """This is your personal place to write notes about the recipes, such as substitutions or modifications\.  Only you will be able to print, view, and edit your notes\.""",
    "Add a note (&gt;|>)",
    'print review with recipe',
    ]
                       ]
def filter_epicurious_notes (text, markup):
    for regexp in STOCK_NOTES_REGEXPS:
        m=regexp.search(text)
        while m:
            text = text[0:m.start()]+text[m.end():]
            m=regexp.search(text)
    text = text.strip()
    return text


RULES = [
    ['title',
     [{'tag':'div',
       'attributes':{'class':'recipehed'},}],
     'text',
     lambda s,t: s.capitalize()],
    # we add a new title element -- the previous markup seems outdated
    # but I'll keep it around in case it's used on some of their old
    # pages or comes back (7/25/05)
    ['title',
     [{'tag':'div',
       'attributes':{'id':'recipeIntro'},},
      {'tag':'h1'},
      ],
     'text',
     lambda s,t: s.capitalize()],
    ['image',
     [{'tag':'img',
       'attributes':{'class':'recipeimg'},}],
     'src',
     ],
    # and a new image tag...
    ['image',
     [{'tag':'div',
       'attributes':{'id':'recipeIntro'},},
      {'tag':'a'},
      {'tag':'img'},],
     'src',
     ],
    ['ingredient_parsed',
     [{'regexp':'<!-- ingredients -->',
       'moveto':'parent'},
      ],
     'text',
     ingredient_parser],
    ['ingredient_block',
     [{'tag':'div',
       'attributes':{'class':'copy'},
       'index':1,
       }],
     'text'],
    ['source',
     [{'tag':'span',
       'attributes':{'class':'source'},
       }],
     'text'],
    ['source',
     [{'tag':'div',
       'attributes':{'class':'magname'},
       }],
     'text'],
    ['source',
     [{'tag':'div',
       'attributes':{'class':'date'},
       }],
     'text'],
    ['servings',
     [{'regexp':'Makes\s+%(num)s+\s+servings?'%{'num':convert.NUMBER_REGEXP}}],
     'text',
     ('Makes\s+(%(num)s+)\s+servings?'%{'num':convert.NUMBER_REGEXP},True)],
    ['servings',
     [{'regexp':'Serves\s+%(num)s+'%{'num':convert.NUMBER_REGEXP}}],
     'text',
     ('Serves\s+(%(num)s+)'%{'num':convert.NUMBER_REGEXP},True)],
    # the epicurious folks have mispelt preparation... we'll allow for them to correct it..
    ['instructions',
     [{'regexp':'<!-- prep[ea]ration -->',
      'moveto':'parent',}],
     'text'],
    ['modifications',
     [{'regexp':'<!-- reviews -->',
      'moveto':'parent'},],
     'text',
     filter_epicurious_notes
     ],
    ['instructions',
     [{'tag':'div',
       'attributes':{'class':'copy'},
       'index':2,}],
     'text'],
    ]
