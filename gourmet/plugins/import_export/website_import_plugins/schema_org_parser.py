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
    
        schema_org_mappings = {# Properties from Thing (not all given)
                               'name': 'recipe',
                               'description': 'modifications',
                               # Properties from CreativeWork (none)
                               # Properties from Recipe
                               #'cookingMethod'
                               'ingredients': 'ingredients',
                               #'nutrition'
                               'recipeCategory': 'category',
                               'recipeCuisine': 'cuisine',
                               'recipeInstructions': 'instructions',
                               'recipeYield': 'yields',
                               #'totalTime'
                               }
        #FIXME: Currently not evaluated
        schema_org_duration_mappings = {# Properties from Recipe
                                        'cookTime': 'cooktime',
                                        'prepTime': 'preptime'
                                        }
    
        imageexcluders = []
    
        def preparse (self):
            self.preparsed_elements = []
            self.recipe_schema_scope = self.soup.find(itemscope = True,
                                                      itemtype =
                                                      'http://schema.org/Recipe')
            for tag in self.recipe_schema_scope.findAll(itemprop=True):
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

