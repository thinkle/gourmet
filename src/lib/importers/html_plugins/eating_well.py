from gourmet import convert
import re
from html_helpers import *

SUPPORTED_URLS = ['www.eatingwell.com']
SUPPORTED_URLS_REGEXPS = ['.*eatingwell\.com']

eating_well_mainrec = {'tag':'div',
                       'attributes':{'align':'center'},
                       'index':1}

RULES = [
    ['image',
     [{'tag':'img','index':2}],
     'src',
     ],
    ['title',
     [{'tag':'title'}],
     'text',
     ('EatingWell (.*)',False)
     ],
    ['source',
     [{'tag':'font',
       'attributes':{'face':'Arial, Helvetica, sans-serif','color':'#000000'},}],
     'text',
     lambda txt,tag: 'Eating Well %s'%txt
     ],
    ['instructions',
     [eating_well_mainrec,
      {'tag':'p',
       'attributes':{'align':'left'},
       'index':[0,None]},
      ],
     'text',
     reject_ing,
     ],
    ['ingredient_block',
     [eating_well_mainrec,
      {'tag':'p',
       'attributes':{'align':'left'},
       'index':[0,None]},
      ],
     'text',
     keep_ing,
     ],
    ['servings',
     [eating_well_mainrec,
      {'regexp':'%(num)s+ [Ss]ervings?'%{'num':convert.NUMBER_REGEXP}},
      ],
     'text',
     ('(%(num)s+) [Ss]ervings?'%{'num':convert.NUMBER_REGEXP},True)],
    ['preptime',
     [eating_well_mainrec,
      {'regexp':'(Prep(aration)|Active)?\s*[tT]ime.*minutes','index':0}],
     'text',
     ('(%(num)s+ (minutes|hours|days))'%{'num':convert.NUMBER_REGEXP},True),
     ],
    ['cooktime',
     [eating_well_mainrec,
      {'regexp':'(Start\s*to\s*finish|Total).*minutes','index':0}],
     'text',
     ('(%(num)s+ (minutes|hours|days))'%{'num':convert.NUMBER_REGEXP},True)
     ],
    # newer format preptime and cooktime...
    ['preptime',
     [{'tag':'i'},
      {'regexp':'.*minutes','index':0}],
     'text',
     ('\s*(%(num)s+ (minutes|hours|days))'%{'num':convert.NUMBER_REGEXP},True)
     ],
    ['cooktime',
      [{'tag':'i'},
       {'regexp':'.*minutes','index':1}],
     'text',
     ('\s*(%(num)s+ (minutes|hours|days))'%{'num':convert.NUMBER_REGEXP},True)
     ],
    ]
