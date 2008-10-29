from gourmet import convert
import re
from html_helpers import *

SUPPORTED_URLS = ['www.recipebookonline.com']
SUPPORTED_URLS_REGEXPS = ['.*\.recipebookonline.com','recipebookonline.com.*']

RULES = [
    ['title',
     [{'tag':'font',
       'attributes':{'size':'4'}
       }],
     'text',
     ],
    ['ingredient_block',
     [{'tag':'td',
       'attributes':{'width':'100%',
                     'align':'center'},
       'index':[0,None],
       }],
     'text',
     ],
    ['instructions',
     [{'tag':'td',
       'attributes':{'width':'396'},
       'index':4,
       }],
     'text',
     ('Directions:\s+((.*\n)+)',False) # chop off "Directions: "
     ],
    ['instructions',
     [{'tag':'td',
       'attributes':{'width':'396'},
       'index':6,
       }],
     'text',
    ],
    ['source',
     [{'tag':'td',
       'attributes':{'width':'396'},
       'index':6,
       }],
     'text',
     ('Submitted\s+By:\s+(.*)\n',True),
     ],
    ['preptime',
     [{'tag':'font',
       'attributes':{'size':'2'},}],
     'text',
     ('Preparation Time: (.*)',True)
     ],
    ['cooktime',
     [{'tag':'font',
       'attributes':{'size':'2'},}],
     'text',
     ('Cooking Time: (.*)',True)
     ],
    ['servings',
     [{'tag':'font',
       'attributes':{'size':'2'},}],
     'text',
     ('Number\s+of\s+Servings\s*:\s*(%(num)s+).*'%{'num':convert.NUMBER_REGEXP},True)
     ] ,   
    ]

