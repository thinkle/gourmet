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

recipe_intro_tag = {'tag':'div',
                    'attributes':{'id':'recipeIntro'}
                    }

RULES = [
    ['title',
     #path
     [{'tag':'h1'}],
     # type
     'text',
     # post-processing
     lambda x,tag: x and x.title() or ''],
    ['image',
     [recipe_intro_tag,
      {'tag':'img'},
      ],
     'src',
     lambda src,tag: src.replace('thumb','full') # URL to THUMB is similar to URL for FULL image...
     ],
    ['ingredient_block',
     [{'tag':'img',
       'attributes':{'src':'/images/recipes/recipe_results/ingredients_hed.gif'},
       'firstNext':'div'},
      ],
     'text'
     ],
    ['instructions',
     [{'tag':'img',
       'attributes':{'src':'/images/recipes/recipe_results/preperation_hed.gif'},
       'firstNext':'div'},
      {'tag':'p',
       'index':[0,None]}
      ],
     'text',
     ],
    ['source',
     [{'tag':'span',
       'attributes':{'class':'source'}}],
     'text',
     lambda txt,tag: txt.strip()
     ],
    ['source',
     [{'tag':'span',
       'attributes':{'class':'copyright'}}],
     'text',
     lambda txt,tag: re.sub('\s+',' ',txt).strip()
     ],
#     ['ingredient_block',
#      [{'tag':'div',
#        'attributes':{'class':'copy'},
#        'index':1,
#        }],
#      'text'],
#     ['source',
#      [{'tag':'span',
#        'attributes':{'class':'source'},
#        }],
#      'text'],
#     ['source',
#      [{'tag':'div',
#        'attributes':{'class':'magname'},
#        }],
#      'text'],
#     ['source',
#      [{'tag':'div',
#        'attributes':{'class':'date'},
#        }],
#      'text'],
     ['servings',
      [{'regexp':'Makes\s+%(num)s+\s+servings?'%{'num':convert.NUMBER_REGEXP}}],
      'text',
      ('Makes\s+(%(num)s+)\s+servings?'%{'num':convert.NUMBER_REGEXP},True)],
    ['servings',
      [{'regexp':'Makes\s+%(num)s\s+to\s+%(num)s+\s+servings?'%{'num':convert.NUMBER_REGEXP}}],
      'text',
      ('Makes\s+%(num)s\s+to\s+(%(num)s+)\s+servings?'%{'num':convert.NUMBER_REGEXP},True)],
     ['servings',
      [{'regexp':'Serves\s+%(num)s+'%{'num':convert.NUMBER_REGEXP}}],
      'text',
      ('Serves\s+(%(num)s+)'%{'num':convert.NUMBER_REGEXP},True)],
#     # the epicurious folks have mispelt preparation... we'll allow for them to correct it..
#     ['instructions',
#      [{'regexp':'<!-- prep[ea]ration -->',
#       'moveto':'parent',}],
#      'text'],
#     ['modifications',
#      [{'regexp':'<!-- reviews -->',
#       'moveto':'parent'},],
#      'text',
#      filter_epicurious_notes
#      ],
#     ['instructions',
#      [{'tag':'div',
#        'attributes':{'class':'copy'},
#        'index':2,}],
#      'text'],
    ]
