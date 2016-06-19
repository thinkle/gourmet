from __future__ import print_function

import re
import gourmet.convert as convert
import unittest
from gettext import gettext as _

def parse_group (match, text, group_number, tag):
    start,end = match.span(group_number)
    if start==-1:
        return None
    else:
        retv = []
        if start > 0:
            retv.append((text[0:start],None))
        retv.append((text[start:end],tag))
        if end < len(text):
            retv.append((text[end:],None))
        return retv

class RecipeParser:

    """A generic parser for doing rough mark up of unformatted recipes

    We pre-parse the text based on a set of rules which look a bit
    like the rules we use for HTML parsing (see
    html_plugins/__init__.py).

    Each rule is
    [recipe_part,regexp_matcher,post_processing]

    recipe_part is a string describing what part of the recipe
    ('ingredient','ingredients', 'serving', etc.)

    regexp_matcher is a compiled regular expression to match our part.

    By default, we simply mark the whole line as being the recipe_part.

    post_processing can refine our match:

    If post_processing is an integer, it is the number of the regexp
    group which should actually be labelled (the rest of the line will
    be marked"ignore")

    Otherwise, post_processing should be a function of the following form.

    def (match_object, full_text, attribute):
        ...
        return [(chunk, tag),(chunk, tag),...]
    the matcher and text as arguments and should return a list of
    chunks/tag with marked up text from our line.

    [(chunk, tag),(chunk, tag),...]
    """

    LONG_LINE = 80
    SHORT_LINE = 40

    ATTRIBUTES = ['servings',
                  'category',
                  'cuisine',                  
                  'rating',
                  'source',
                  'ignore',
                  'yields',
                  'yield_unit',
                  'modifications',
                  ]

    ALIASES = [('cooking time','cooktime'),
               ('preparation time','preptime'),
               ('time','preptime'),
               ('author','source'),
               ('by','source'),
               ('yield','yields'),
               ('notes','modifications'),
               ('note','modifications'),               
               ]

    IGNORE_ON_OWN = ['instructions','ingredients','directions']

    joinable_tags = ['instructions','ingredient','ingredients',None]
    change_on_join = {'ingredient':'ingredients'}

    ing_matcher = re.compile(u"^\s*\u2022?\u2023?\u2043?\u204C?\u204D?\u2219?\u25C9?\u25D8?\u25E6?\u2619?\u2765?\u2767?\u29BE?\u29BF?\s*(%s\s+\w+.*)"%convert.NUMBER_REGEXP)

    def __init__ (self):
        self.title_parsed = False
        self.make_rules()
    
    #INGREDIENT = 'ING'
    #INSTRUCTIONS = 'INSTRUCTIONS'
    #ATTRIBUTE = 'ATT'
    #TITLE = 'TIT'
    #IGNORE = 'IGN'
    def make_rules (self):
        self.rules = [
            ['ingredients',
             self.ing_matcher,
             1],
            ['servings',
             re.compile("serv(ing|e)s?:?\s*%(num)s|%(num)s\s*servings?"%{
            'num':convert.NUMBER_REGEXP},re.IGNORECASE),
             lambda m,txt,attr: (parse_group(m,txt,2,attr)
                                 or
                                 parse_group(m,txt,3,attr))
             ],]
        for a in self.ATTRIBUTES:
            self.rules.append([a,re.compile('\s*%s\s*:\s*(.*)'%a,
                                            re.IGNORECASE),
                               1])
        for name,attr in self.ALIASES:
            self.rules.append([attr,re.compile('\s*%s\s*:\s*(.*)'%name,
                                               re.IGNORECASE),
                               1])
        for ig in self.IGNORE_ON_OWN:
            self.rules.append([None,
                               re.compile('^\W*%s\W*$'%ig,re.IGNORECASE),
                               None])
        self.rules.append([
            # instructions are our generic fallback
            'instructions',
            re.compile('.*'),
            None])
        def parse_yield (match_obj, full_text, attr):
            colon,amt,unit = match_obj.groups()
            return [(amt.strip(),'yields'),(unit.strip(),'yield_unit')]
        self.rules = [[
                'yield',
                re.compile('%(yield)s(:|s|\s-)\s-*%(num)s\s-*(.*)'%{
                    'yield':_('yield'),
                    'num':convert.NUMBER_REGEXP
                    },re.IGNORECASE),
                parse_yield
                ]] + self.rules                    

    def break_into_paras (self):
        self.long_lines = False
        for l in self.txt.split('\n'):
            if len(l)>self.LONG_LINE:
                self.long_lines = True
                break
        if self.long_lines:
            self.paras = self.txt.split('\n')
        else:
            # Try to deal with wrapped lines reasonably...
            self.paras = []
            start_new_para = True
            for l in self.txt.split('\n'):                
                if start_new_para or self.ing_matcher.match(l):
                    self.paras.append(l)
                    if len(l) > self.SHORT_LINE: start_new_para = False
                else:
                    self.paras[-1] = self.paras[-1]+' '+l
                    start_new_para = (len(l) < self.SHORT_LINE)

    def parse (self, txt, parentThread=None):
        self.txt = txt
        self.parsed = []
        self.break_into_paras()
        tot=len(self.paras)
        n = 1
        for p in self.paras:
            # update a progress bar if necessary...
            if parentThread:
                parentThread.emit('progress',
                                  float(n)/tot,
                                  'Parsing unformatted recipe')
                n+=1
            self.parsed.append(('\n',None))
            # genericly guess that the title is the first line!
            if not self.title_parsed and p.strip():
                self.parsed.append((p,'title'))
                self.title_parsed = True
            elif not p.strip():
                self.parsed.append((p,None))
            else:
                for attr,regexp,postproc in self.rules:
                    m = regexp.search(p)
                    if m:
                        if postproc:
                            if type(postproc)==int:
                                proced = parse_group(
                                    m, p, postproc, attr
                                    )
                                if not proced:                                    
                                    continue
                            else:
                                proced = postproc(m,p,attr)
                            if proced:
                                self.parsed.extend(proced)
                                break
                        else:
                            self.parsed.append((p,attr))
                            break
        self.join_the_joinable()
        return self.parsed

    def join_the_joinable (self):
        """Go through self.parsed and join joinable elements.

        This means: produce fewer elements to jump through for the
        user if possible.
        """
        parsed = self.parsed[0:]
        self.parsed = []
        for chunk,tag in parsed:
            if tag not in self.joinable_tags or len(self.parsed)==0:
                self.parsed.append([chunk,tag])
                continue
            if self.change_on_join.has_key(tag):
                look_for = [tag,self.change_on_join[tag]]
            else:
                look_for = [tag]
            add_on = ''
            added = False
            for n in range(1,len(self.parsed)+1):
                oldchunk,oldtag = self.parsed[-n]
                if oldtag in look_for:
                    self.parsed[-n][0] = oldchunk+add_on+chunk
                    added = True
                    if self.change_on_join.has_key(oldtag):
                        self.parsed[-n][1] = self.change_on_join[oldtag]
                    # Strip off any added junk...
                    if n > 1:
                        self.parsed = self.parsed[0:-(n-1)]
                    break
                if oldtag == None:
                    add_on += oldchunk
                else:
                    break
            if not added:
                self.parsed.append([chunk,tag])

class RecipeTestCase (unittest.TestCase):
    def setUp (self):
        self.recipe = """
My Recipe

This is a test recipe. I hope it is really good.

This recipe serves 8
Category: dessert, quick, snack
Cuisine: Classic American!
Yield: 2 cups        

   1 tbs. milk
   3 tbs. unsweetened bakers chocolate
   2 tbs. sugar
   1/4 tsp. almond extract

   1 c. milk

   2 tbs. whipped cream (for garnish)
        
   Mix the first four ingredients together into a thick slurry.
   Add the milk. Heat and stir.

   Enjoy!!!
   """
        self.rp = RecipeParser()

    def testParser (self):
        parsed = self.rp.parse(self.recipe)

if __name__ == '__main__':
    unittest.main()
