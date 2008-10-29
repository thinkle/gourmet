SUPPORTED_URLS = ['www.foodnetwork.com']
SUPPORTED_URLS_REGEXPS = ['.*foodnetwork\.com']

recipe_summary = {'tag':'span',
                  'attributes':{'class':'guttertableheader2'},
                  'regexp':'Recipe Summary',
                  'moveto':'nextSibling'}

RULES = [
    ['title',
     [{'tag':'span',
       'attributes':{'class':'headline1'}
       }],
     'text',
     ],
    ['source',
     [{'tag':'tr',
       'attributes':{'class':'small_text'}},
      {'tag':'td',
       'regexp':'Recipes? courtesy.*'}],
     'text',
     ('Recipes?\s+courtesy\s+(.*)',True),
     ],
    ['instructions',
     [{'tag':'tr',
       'attributes':{'class':'small_text'}},
      ],
     'text',
     ],
    ['ingredient_block',
     [#{'tag':'table'},
      #{'tag':'tr',
       #'attributes':{'valign':'top'},
      # 'index':0},
      {'tag':'td',
       'attributes':{'class':'bodytext'},
       },
      {'tag':'span',
       'attributes':{'class':'bodytext'},
       #'index':0
       }
       ],
     'text'],
    ['instructions',
     [{'tag':'td',
       'attributes':{'class':'bodytext'},
       },
      {'tag':'p'}],
     'text'
     ],
    ['preptime',
     [recipe_summary],
     'text',
     ('Prep Time:\s*(.*)',True)],
    ['cooktime',
     [recipe_summary],
     'text',
     ('Cook Time:\s*(.*)',True)],
    ['servings',
     [recipe_summary],
     'text',
     ('Yield:\s*(.*)\s*servings?',True)],
    #['instructions',
    # [recipe_summary],
    # 'text',
    # ],
    ['image',
     [{'tag':'img',
       'attributes':{'alt':'Click here to view a larger image.'}
       }],
     'src',
     ],
    ['instructions',
     [{'tag':'span',
       'attributes':{'class':'bodytext'},
       'index':(1,None)},
      ],
     'text'
     ],
    ['instructions',
     [{'tag':'p',
       #'index':(0,None)
       }
       ],
     'text'
     ]
    # end RULES
    ]

