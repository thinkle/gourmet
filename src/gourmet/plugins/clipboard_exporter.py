"""Basic example of a Gourmet export plugin."""
from pathlib import Path
from typing import List, Tuple
from gi.repository import Gdk, Gtk


class ClipboardExporter:
    """Export a recipe to the system's clipboard.

    This plugin demonstrates how to create an export plugin.
    The exported recipe
    """
    AUTHOR = 'Gourmet Team'
    COPYRIGHT = 'MIT'
    WEBSITE = ''

    def __init__(self,
                 recipes: List[Tuple['RowProxy', 'RowProxy']] = None,
                 export_path: Path = None):
        """Create the exporter.

        Two arguments are given to an exporter: a list of selected recipes and
        their ingredients (two entries in the database,
        sqlalchemy.RowProxy objects), and the path to export to, a pathlib.Path
        object.

        You can do here any setting up you need.

        This plugin is special as nothing is done with the export_path, as it's
        aiming for the clipboard!
        """
        self.recipes = recipes
        self.export_path = export_path

    def export(self):
        """Copy a recipe and its image to the clipboard.

        This function is called by Gourmet following the creation of the object.
        """
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        recipes = []

        # Each item in self.recipes is a set of (a recipe, its ingredients).
        for recipe, ingredients in self.recipes:
            # The ingredients have the name, quantity, and units attached
            formatted_ingredients = []
            for ingredient in ingredients:
                formatted_ingredients.append(
                    f"{ingredient.amount} {ingredient.unit} {ingredient.item}"
                )
            formatted_ingredients = '\n'.join(formatted_ingredients)

            # The description is optional, but we add extra formatting, to make
            # the text clearer.
            if recipe.description is not None:
                description = f'\n{recipe.description}\n'
            else:
                description = ''
            # Now that the ingredients and description are formatted, the title,
            # yields, description etc. can be extracted. The rating, for
            # instance, is omitted: let the recipient make their own opinion!
            formatted_recipe = f"""
# {recipe.title}

{recipe.source}
{recipe.yields} {recipe.yield_unit}
{description}
{formatted_ingredients}

{recipe.instructions}
"""
            recipes.append(formatted_recipe)

        # Join all the recipes as one text to put in the clipboard.
        recipes = '\n'.join(recipes)
        clipboard.set_text(recipes, -1)

        # Although not used here, the image can also be retrieved.
        # They are stored as jpegs in the database:
        # if recipe.image is not None:
        #     image_filename = self.export_path / f'{recipe.title}.jpg'
        #     with open(image_filename, 'wb') as fout:
        #         fout.write(recipe.image)