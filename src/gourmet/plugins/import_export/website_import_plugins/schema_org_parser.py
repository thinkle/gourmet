"""
Parser for web pages that use the http://schema.org/Recipe microformat
"""

from datetime import timedelta

import scrape_schema_recipe


def generate(BaseParser):

    class SchemaOrgParser(BaseParser):

        schema_org_mappings = {
            'name': 'title',
            'description': 'modifications',
            # Properties from CreativeWork (none)
            # Properties from Recipe
            #'cookingMethod'
            'ingredients': 'ingredients',
            'recipeIngredient': 'ingredients',
            #'nutrition'
            'recipeCategory': 'category',
            'recipeCuisine': 'cuisine',
            'recipeInstructions': 'recipe',
            'recipeYield': 'yields',
            'totalTime': 'totaltime',
            'cookTime': 'cooktime',
            'prepTime': 'preptime'
        }

        imageexcluders = []

        def preparse(self):
            self.preparsed_elements = []
            self.data = scrape_schema_recipe.scrape(self.text, python_objects=True)

            if not self.data:
                BaseParser.preparse(self)
                return

            recipe = self.data[0]
            self.recipe = recipe

            for schema_key, output_key in self.schema_org_mappings.items():
                if schema_key in recipe:
                    value = recipe[schema_key]
                    if isinstance(value, str):
                        self.preparsed_elements.append((value, output_key))
                    if isinstance(value, list):
                        for entry in value:
                            self.preparsed_elements.append((entry, output_key))
                    elif isinstance(value, timedelta):
                        minutes = int(value.total_seconds() // 60)
                        if not minutes % 60 == 0:
                            # Not full hours.
                            self.preparsed_elements.append(("{} min".format(minutes), output_key))
                        else:
                            # Full hours.
                            self.preparsed_elements.append(("{} h".format(minutes // 60), output_key))

            if self.preparsed_elements:
                self.ignore_unparsed = True
            else:
                BaseParser.preparse(self)

    return SchemaOrgParser

