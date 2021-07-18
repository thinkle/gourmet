import gi
import pytest

gi.require_version("Gtk", "3.0")
from collections import namedtuple  # noqa: import not at top of file
from gi.repository import Gtk, Gdk  # noqa: import not at top of file
from gourmet.plugins.clipboard_exporter import ClipboardExporter  # noqa

Recipe = namedtuple('Recipe', ['title', 'source', 'yields', 'yield_unit',
                               'description', 'instructions'])

recipe1 = Recipe('Title1', 'Source1', 700.0, 'g.', None, 'Make the Dough.')
recipe2 = Recipe('Title2', 'Source2', 2, 'litres', 'test', 'Directions.')

Ingredient = namedtuple('Ingredient', ['amount', 'unit', 'item'])

ingredients1 = (Ingredient(600, 'g.', 'flour'),)
ingredients2 = (Ingredient(600, 'g.', 'flour'),
                Ingredient(2, 'l.', 'water'))

recipe_input = [(recipe1, ingredients1)]
recipe_expected_output = """
# Title1

Source1
700.0 g.

600 g. flour

Make the Dough.
"""

two_recipes_input = [(recipe1, ingredients1), (recipe2, ingredients2)]

two_recipes_expected_output = """
# Title1

Source1
700.0 g.

600 g. flour

Make the Dough.


# Title2

Source2
2 litres

test

600 g. flour
2 l. water

Directions.
"""


@pytest.mark.parametrize(
    'recipes, expected',
    [
        ([], ''),
        (recipe_input, recipe_expected_output),
        (two_recipes_input, two_recipes_expected_output),
     ],
)
def test_clipboard_exporter(recipes, expected):
    ce = ClipboardExporter(recipes)
    ce.export()

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    assert clipboard.wait_for_text() == expected
