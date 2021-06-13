"""Basic example of a Gourmet export plugin."""
from pathlib import Path
from typing import List
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
                 recipes: List['RowProxy'] = None,
                 export_path: Path = None):
        """Create the exporter.

        Two arguments are given to an exporter: the selected recipes themselves
        (entry in the database, sqlalchemy.RowProxy objects), and the path to
        export to, a pathlib.Path object.

        You can do here any setting up you need.

        This plugin is special as nothing is done with the export_path, as it's
        aiming for the clipboard!
        """
        self.recipes = recipes

    def export(self):
        """Copy a recipe and its image to the clipboard.

        This function is called by Gourmet following the creation of the object.
        """
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        recipes = []
        for recipe in self.recipes:
            formatted_recipe = f"""
# {recipe.title}

{recipe.source}
{recipe.yields} {recipe.yield_unit}

{recipe.description if recipe.description is not None else ''}

{recipe.instructions}
"""
            recipes.append(formatted_recipe)
        recipes = '\n'.join(recipes)
        clipboard.set_text(recipes, -1)