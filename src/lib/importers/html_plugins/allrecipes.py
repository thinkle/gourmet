from gourmet import convert
import re
from html_helpers import *

SUPPORTED_URLS = ['www.allrecipes.com']
SUPPORTED_URLS_REGEXPS = ['.*\.allrecipes\.com']

RULES = [
    ['title',
     [{'tag':'h2','index':0}],
     'text'],
    ['source',
     [{'tag':'div',
      'attributes':{'class':'V10color'},}],
     'text',
     ('Submitted\s+by:\s+(.*)',True)
     ],
    ['ingredient_block',
     [{'tag':'ul',
       'attributes':{'class':'arlist','style':'list-style: none;'}
       },
      {'tag':'li',
       'index':[0,None]}
      ],
     'text'],
    ['instructions',
     [{'tag':'meta',
       'attributes':{'name':'description'},
       }],
     'content',
     ],
    ['instructions',
     [{'tag':'ol',
       'attributes':{'class':'arlist'},
       },
      {'tag':'li',
       'index':[0,None],
       },
      ],
     'text',],
    ['preptime',
     [{'tag':'dt',
       'regexp':'.*Prep.*Time:.*',
       'moveto':'nextSibling'}],
     'text'],
    ['cooktime',
     [{'tag':'dt',
       'regexp':'.*Ready In:.*',
       'moveto':'nextSibling'}],
     'text'],
    ['servings',
     [{'tag':'dt',
       'regexp':'.*Servings.*:.*',
       'moveto':'nextSibling',
       }],
     'text',
     '(%(num)s+).*'%{'num':convert.NUMBER_REGEXP}],
    ]
