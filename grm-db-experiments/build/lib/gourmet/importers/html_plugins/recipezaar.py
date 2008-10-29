from gourmet import convert
import re
import os.path,sys
sys.path.append(os.path.split(os.path.split(__file__)[0])[0])
import html_importer
from html_helpers import *

SUPPORTED_URLS = ['www.recipezaar.com']
SUPPORTED_URLS_REGEXPS = []

recipezaar_group = None

# UNICODE was causing some nasty hanging w/ recipezaar...
NON_UNICODE_NUMBER_REGEXP = '([\d/]([\d/ ]*[\d])?)'

def recipezaar_ingredient_parser (text, tag):
    """Do the right thing when handed something like... 
    <td class="amt" align="right" nowrap="nowrap" valign="top">
    1
    </td>
    <td valign="top">
    dozen
    medium sized <b>prawns</b>, peeled and deveined		 	 	 	 			 </td>
    </tr>"""
    global recipezaar_group
    ret = {}
    if recipezaar_group: ret['inggroup']=recipezaar_group
    # groups are in B in DIV
    grouptag = tag.fetch('div')
    if grouptag: grouptag = grouptag[0].fetch('b')
    if grouptag:
        recipezaar_group = html_importer.get_text(grouptag[0])
        return
    keytag = tag.fetch('b')
    if keytag:
        keytag=keytag[0]
        ret['ingkey']=html_importer.get_text(keytag)
    amttag = tag.fetch('td','amt')
    if amttag:
        amttag = amttag[0]
        ret['amount']=html_importer.get_text(amttag)
    txt=html_importer.get_text(tag.fetch('td')[-1])
    words = re.split('\s+',txt)
    if len(words)>1 and words[0] not in ret['ingkey']:
        ret['unit']=words[0]
        ret['item']=" ".join(words[1:])
    else:
        ret['item']=" ".join(words)
    return ret

RULES = [
    ['title',
     [{'tag':'h1'}],
     'text',
     ],
    ['image',
     [{'tag':'img',
       'attributes':{'alt':'Recipe Photo'}}],
     'src',
     ],
    ['instructions',
     [{'tag':'div',
       'attributes':{'class':'recipetext'},
       }],
     'text'],
    ['ingredient_parsed',
     [{'tag':'table',
       'attributes':{'class':'ingred'}},
      {'tag':'tr',
       'index':[0,None]}],
     'text',
     recipezaar_ingredient_parser,
      ],
    ['servings',
     #[{'regexp':'%(num)s+\s+servings?'%{'num':convert.NUMBER_REGEXP}}],
     [{'regexp':'%(num)s+\s+servings?'%{'num':NON_UNICODE_NUMBER_REGEXP}}],
     'text',
     #('(%(num)s+).+'%{'num':NON_UNICODE_NUMBER_REGEXP},True)],
     ('(%(num)s+).+'%{'num':'[\d/]'},True)],
    ['preptime',
     [{'regexp':'\s*(%(num)s+\s*(minutes?|hours?|days?|weeks?|months?))'%{'num':NON_UNICODE_NUMBER_REGEXP}}],
     'text',
     ('\s*(%(num)s+\s*(minutes?|hours?|days?|weeks?|months?))'%{'num':NON_UNICODE_NUMBER_REGEXP},False)
     #[{'tag':'h4',
     #  'attributes':{'style':'font-weight: normal;'},
     #  'index':[0,None]},],
     #'text',
     #('\s*(%(num)s+\s*(minutes?|hours?|days?|weeks?|months?))'%{'num':NON_UNICODE_NUMBER_REGEXP},True)
    ],
    ['instructions',
     [{'tag':'span',
       'attributes':{'class':'recipetext'},
       'index':[0,None]
       }],
     'text',
     ],
    ]
      
