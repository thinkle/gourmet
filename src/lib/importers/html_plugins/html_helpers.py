import re
from gourmet import convert

ing_match = re.compile('(^|\n)\s*%(num)s+[^.].*'%{'num':convert.NUMBER_REGEXP})

def keep_ing (txt,tag):
    if ing_match.search(txt):
        return txt

def reject_ing (txt,tag):
    if not ing_match.search(txt):
        return txt

class IngredientParser:
    """Create an ingredient parser that will iterate through a container when called.

    We match either ingredients or groups. This makes it very simple
    to parse something like a DIV that contains bolded ingredient
    groups
    """

    COMMENT_MATCHER = re.compile('<!--.*?-->')
    
    def __init__ (self,
                  group_match = {'tag':re.compile('^b$',re.IGNORECASE)},
                  ing_block_match={'tag':re.compile('.*')},
                  ing_match = {'tag':re.compile('.*')},
                  exclude_comments = True
                  ):
        self.group_match = group_match
        self.ing_block_match = ing_match
        self.ing_match = ing_match

    def remove_comments (self, text):
        m =  self.COMMENT_MATCHER.search(text)
        while m:
            text = text[0:m.start()]+text[m.end():]
            m =  self.COMMENT_MATCHER.search(text)
        return text
    
    def __call__ (self, text, container):
        ret = []
        self.group = None
        items = container.contents
        items.reverse()
        while items:
            itm = items.pop()
            added = False
            if self.test_match(self.group_match,itm):
                self.group = itm.string
                added = True
            elif self.test_match(self.ing_block_match,itm):
                for i in self.remove_comments(itm).split('\n'):
                    if i:
                        ing = {'text':i}
                        if self.group: ing['inggroup']=self.group
                        ret.append(ing)
                        added=True
            elif self.test_match(self.ing_match,itm):
                txt = itm.string and self.remove_comments(itm.string)
                if txt:
                    ing = {'text':itm.string}
                    if self.group:
                        ing['inggroup']=self.group
                    ret.append(ing)
                    added = True
            if not added and hasattr(itm,'contents'):
                sub_items = itm.contents
                sub_items.reverse()
                items.extend(sub_items)
        return ret

    def test_match (self, matcher_dic, tag):
        ret = True
        if not matcher_dic:
            return False
        if matcher_dic.get('tag'):
            if not hasattr(tag,'name'):
                ret = False
            elif not matcher_dic['tag'].match(tag.name):
                return False
            else:
                ret = True
        if matcher_dic.get('string'):
            if not hasattr(tag,'string') or not tag.string:
                ret = False
            elif not matcher_dic['string'].match(tag.string):
                return False
            else:
                ret = True
        return ret
    
                
        
            
            
