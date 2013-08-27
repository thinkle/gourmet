"""
Parser for web pages that use the http://schema.org/Recipe microformat
"""

class Excluder(object):
    def __init__(self, url):
        self.url = url
    def search(self, other_url):
        return not (other_url.endswith(self.url))

def generate(BaseParser):
    class SchemaOrgParser (BaseParser):
    
        schema_org_mappings = {'name': 'recipe',
                               'cookTime': 'cooktime',
                               'ingredients': 'ingredients',
                               'recipeInstructions': 'instructions'
                               }
    
        imageexcluders = []
    
        def preparse (self):
            self.preparsed_elements = []
            for tag in self.soup.findAll(itemprop=True):
                itemprop = tag["itemprop"]
                for k, v in self.schema_org_mappings.iteritems():
                    if itemprop == k:
                        self.preparsed_elements.append((tag,v))                            
    
                if itemprop == "image":
                    self.imageexcluders.append(Excluder(tag["src"]))
    
            if self.preparsed_elements:
                self.ignore_unparsed = True
            else:
                BaseParser.preparse(self)

    return SchemaOrgParser

