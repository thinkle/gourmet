from gourmet.importers.interactive_importer import ConvenientImporter
from gourmet.threadManager import NotThreadSafe
import requests
import gettext

from scrapy.selector import Selector

class ScrapyImporter(ConvenientImporter, NotThreadSafe):
    """ This importer is a meta plugin which can be extended by implementing 
    subplugins which parses a website using scrapy selector class with xpath
    support (http://doc.scrapy.org/en/latest/topics/selectors.html).
    
    The plugin has to return a dictionary of the following elements:
    
    'cuisine', 'category', 'title' 'preptime', 'cooktime', 'instructions',
    ' modifications': No special considerations, just strings
    'image': This must contain a downloaded image of type jpeg
    'imageUrl': If this is set, the 'image' will be filled with the image
        downloaded from this url.
    'link': This will be auto filled if not set, or otherwise set to a maybe
        permanent url by the parser
    'servings': This can be used to fill the yields and yield_unit correctly
        without too much boilerplate code.
    'yields', 'yield_unit': The yield of the recipe, if something else than
        servings is needed. If servings are meant, the 'servings' field should
        be used because this also handles singular / plural correctly.
    'ingredients': The ingredients can have a grouped or a ungrouped format:
        ungrouped format: A list of all ingredients as a string. Every 
            ingredient has its own list entry.
        grouped format: [ dict('name':'groupname', 'ingredients': [ <ingredients> ]), ... ]
            The dict contains the information about the group and the ingredeints
            in the same format as the ungrouped format. The dicts are stored
            to a list itself.
    """
    def __init__ (self, url, data, parser):
        ConvenientImporter.__init__(self)
        self.parser = parser
        self.selector = Selector(text=data)
        self.url = url
        
    def do_run (self):
        recipe = self.parser.parse(self.selector)
        
        if 'imageUrl' in recipe:
            imageUrl = recipe['imageUrl']
            del recipe['imageUrl']
            # TODO: load image from url and attach
            
            r = requests.get(imageUrl)
            if r.status_code == 200 and r.headers['content-type'] == 'image/jpeg':
                recipe["image"] = r.content
                
        if 'link' not in recipe and self.url:
            recipe['link'] = self.url
            
        if 'servings' in recipe:
            # The code doing the translation in importer seems to be in conflict
            # with some database code. if yields and servings is set only servings is
            # written to db
            servs = float(recipe['servings'])
            del recipe['servings']
            recipe['yields'] = servs
            recipe['yield_unit'] = gettext.ngettext('serving', 'servings', servs)
        
        self.start_rec( recipe )
        
        if 'ingredients' in recipe:
            self._add_ingredients( recipe['ingredients'] )
            del recipe['ingredients']
        self.commit_rec()
        
        return ConvenientImporter.do_run(self)

    def _add_ingredients(self, ingredients):
        """ This method will add ingredients which may or may not contain grouping
        in the file. We will check if the grouping is needed by ourself.
        @param ingredients The ingredients in grouped style or as bare list.
        """         
        if len(ingredients) == 0:
            return
        
        if isinstance( ingredients[0], dict ):
            self._add_ingredients_with_groups( ingredients )
        else:
            self._add_ingredients_without_groups( ingredients )
        
    def _add_ingredients_with_groups(self, ingredients):
        """ Add ingredients from list with groups.
        """
        for group in ingredients:
            self.add_ing_group( group['name'] )
            self._add_ingredients_without_groups( group['ingredients'] )
            
      
    def _add_ingredients_without_groups(self, ingredients):  
        """ Add ingredients from ingredients list without groups. 
        @type list
        @param ingredients A list of ingredients as strings, every ingredient
              has a single list entry like "1 TS Oil" 
        """
        for ing in ingredients:
            self.add_ing_from_text(ing)
            
            

        