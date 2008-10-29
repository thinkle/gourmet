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
    global recipezaar_group
    ret = {}
    if recipezaar_group: ret['inggroup']=recipezaar_group
    grouptag = tag.fetch('td',{'colspan':'3'})
    # And groups are in <h4> tags
    if grouptag: grouptag = grouptag[0].fetch('h4')
    if grouptag:
        recipezaar_group = html_importer.get_text(grouptag[0])
        return
    keytag = tag.fetch('span','food')
    if keytag:
        keytag = keytag[0]
        ret['ingkey'] = html_importer.get_text(keytag)
    amttag = tag.fetch('td','amt')
    if amttag:
        amttag = amttag[0]
        ret['amount'] = html_importer.get_text(amttag)
    ret['text'] = ret.get('amt','')+' '+html_importer.get_text(tag.fetch('td')[-1])
    ret['text'] = ret['text'].strip()
    ret['text'] = re.sub('\s+',' ',ret['text'])
    print 'ingparser',text,'->',ret
    return ret

def cut_title (title, tagname):
    """Cut recipe # from title

    Title's are often followed by the recipezaar recipe # which we
    don't really want.
    """
    i = title.find(' Recipe #')
    if i > -1:
        return title[:i]
    else:
        return title

RULES = [
    ['title',
     [{'tag':'h1'}],
     'text',
     cut_title
     ],
    ['source',
     [{'tag':'div',
       'attributes':{'class':'submitter'},
       },
      {'tag':'a',
       'index':0,},
      ],
     'text',
     ],
    ['image',
     [{'tag':'img',
       'attributes':{'alt':'Recipe Photo'}}],
     'src',
     ],
    ['servings',
     [{'tag':'input',
       'attributes':{'name':'scaleto'}}],
     'value'],
    ['instructions',
     [{'tag':'div',
       'attributes':{'class':'recipetext'},
       }],
     'text'],
    ['ingredient_parsed',
     [{'tag':'table',
       'attributes':{'class':'ingredients'}},
      {'tag':'tr',
       'index':[0,None]}],
     'text',
     recipezaar_ingredient_parser,
     ],
    ['servings',
     #[{'regexp':'%(num)s+\s+servings?'%{'num':convert.NUMBER_REGEXP}}],
     [{'tag':'div',
       'attributes':{'id':'servings'}},
      {'tag':'div',
       'attributes':{'class':'qty'}},
      ],
     'text',
     ('(%(num)s+).+'%{'num':'[\d/]'},True)],
    ['cooktime',
     [{'tag':'div',
       'attributes':{'id':'time'},
       'index':[0,None]},
      ],
     'text',
     ],
    ['preptime',
     [{'tag':'div',
       'attributes':{'id':'time'},
       },
      {'tag':'span',
       'attributes':{'class':'prep'},
       },
      ],
     'text',
     ('(.*)\s+prep',False),
     ],
    ['instructions',
     [{'tag':'span',
       'attributes':{'class':'recipetext'},
       'index':[0,None]
       }],
     'text',
     ],
    ['instructions',
     [{'tag':'div',
       'attributes':{'class':'steps'},
       'index':[0,None],
       },],
     'text'],
    ['category',
     [{'tag':'div',
       'attributes':{'id':'recipecats'},},
      {'tag':'li',
       'regexp':'Course',
       'moveto':'parent'
       },
      {'tag':'a',
       'index':-1}],
     'text'
     ],
    ['cuisine',
     [{'tag':'div',
       'attributes':{'id':'recipecats'},},
      {'tag':'li',
       'regexp':'Cuisine',
       'moveto':'parent'
       },
      {'tag':'a',
       'index':-1}],
     'text',
     ],
    ]
    
    
      
