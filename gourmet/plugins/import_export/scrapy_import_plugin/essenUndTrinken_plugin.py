from gourmet.plugin import PluginPlugin

class EssenUndTrinkenPlugin (PluginPlugin):
    """ This is a plugin for the german Essen & Trinken page to import recipes
    easily.
    """
    target_pluggable = 'scrapyWeb_plugin'

    def do_activate (self, pluggable):
        pass
    
    def test_url (self, url, data):
        if 'essen-und-trinken.de' in url: 
            return 10
        return -99

    def get_parser (self):
        class Parser:
            def parse(self, selector):
                recipe = dict()
                recipe['source'] = "Essen & Trinken"
                
                recipe['title'] = selector.xpath("//span[@itemprop='name']/text()").extract()[0]
                ingsRaw = selector.xpath("//span[@itemprop='ingredients']")
                ingredientsWithGroups = []
                ingredients = []
                for ing in ingsRaw:
                    groupRaw = ing.xpath("span[@class='recipe_subheadline']/text()")
                    if len(groupRaw) > 0:
                        # We have a group
                        group = " ".join( groupRaw.extract() )
                        gDict = { 'name':group, 'ingredients':[] }
                        ingredientsWithGroups.append( gDict )
                        ingredients = gDict['ingredients']
                    else:
                        ingredients.append(" ".join( ing.xpath("span/text()").extract() ) )
                        
                recipe['ingredients'] = ingredients if len( ingredientsWithGroups ) == 0 else ingredientsWithGroups 
                recipeYield = selector.xpath("//span[@itemprop='recipeYield']/text()").extract()[0]
                recipeYield = [int(s) for s in recipeYield.split() if s.isdigit()]
                if len(recipeYield) != 1:
                    raise RuntimeError("Unable to parse yield from webpage!")

                recipe['servings'] = recipeYield[0]
                recipe['cooktime'] = selector.xpath("//span[@class='cooktime']/text()").extract()[0]
                
                recipe['instructions'] = "\n\n".join( selector.xpath("//span[@itemprop='recipeInstructions']/p/text()").extract() )
                recipe['imageUrl'] = selector.xpath("//img[@id='recipePreviewImage']/@src").extract()[0]

                return recipe;

        return Parser()


