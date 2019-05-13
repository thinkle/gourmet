"""
This plugin imports recipes from the german recipe site
https://www.chefkoch.de/
"""
from gourmet.plugin import PluginPlugin
from gourmet.importers.interactive_importer import ConvenientImporter
from gourmet.gdebug import debug, warn
from gourmet.isoduration_parser import parse_iso8601_duration
from fractions import Fraction
import re
import urllib2
import json


# the regular expression matches the JSON recipe data in the page
JSON_RO = re.compile(r"""<script\s+type="application/ld\+json">(
\s*{
\s*"@context":\s*"http://schema.org",
\s*"@type":\s*"Recipe",
.*?)
</script>""",
re.DOTALL|re.VERBOSE)


class ChefkochDeParser(ConvenientImporter):
    """All recipe pages store the information in a JSON string in
    Recipe schema (defined in https://schema.org/Recipe).
    This parser extracts the JSON from the recipe page and parses it.
    This is not a generic schema.org recipe parser since it relies on the
    specific implementation of chefkoch.de.
    """

    def __init__(self, url, data, content_type):
        self.url = url
        self.data = data
        super(ChefkochDeParser, self).__init__()

    def do_run (self):
        """Construct recipe and ingredients from parsed JSON data."""
        json_data = parse_json_from_data(self.data, self.url)
        if json_data:
            self.start_rec()
            # start_rec() initializes self.rec to an empty recipe dict
            self.rec['source'] = 'Web'
            self.rec['link'] = self.url
            ingredients = []
            import_schema_recipe(json_data, self.rec, ingredients)
            for txt in ingredients:
                # add_ing_from_text(txt) uses self.db.parse_ingredient(txt)
                self.add_ing_from_text(txt)
            self.commit_rec()
        else:
            warn("could not find recipe data in chefkoch.de URL %s - please submit a bug report" % self.url)
        return super(ChefkochDeParser, self).do_run()


def parse_json_from_data(data, url):
    """Parse recipe JSON data. Sometimes the recipe data is incomplete
    and is missing the instructions, so try up to three times.

    @param data: the HTML webpage data
    @ptype data: string
    @param url: the webpage URL
    @ptype url: string
    @return: the parsed JSON object, or None
    @rtype: dict or None
    """
    tries = 1
    while tries <= 3:
        match = JSON_RO.search(data)
        if match:
            json_string = match.group(1).strip()
            json_data = json.loads(json_string)
            if 'recipeInstructions' not in json_data:
                data, _ = getdatafromurl(url)
                tries += 1
            else:
                return json_data
        else:
            return None
    return None


def import_schema_recipe(json_data, recipe, ingredients):
    """Fill given recipe dict and ingredients list with data from JSON.
    @param json_data: the parsed JSON recipe schema data
    @ptype json_data: dict (with various keys and values)
    @param recipe: the gourmet recipe to fill
    @ptype recipe: dict
    @param ingredients: the ingredient list to fill
    @ptype ingredients: list
    @return: nothing, the recipe and ingredients will be modified instead
    @rtype: None
    """
    recipe['title'] = json_data['name']
    if 'recipeCategory' in json_data:
        categories = json_data["recipeCategory"]
        if categories:
            # gourmet only has one category per recipe, so get the first one in the list
            recipe['category'] = categories[0]
            if len(categories) > 1:
                # If there are several categories add them to the modifications.
                recipe['modifications'] = "Kategorien: %s" % (", ".join(categories))
    try:
        cooktime = parse_iso8601_duration(json_data['cookTime'])
    except ValueError:
        warn("could not parse cookTime %r" % json_data['cookTime'])
    else:
        recipe['cooktime'] = cooktime
    try:
        preptime = parse_iso8601_duration(json_data['prepTime'])
    except ValueError:
        warn("could not parse prepTime %r" % json_data['prepTime'])
    else:
        recipe['preptime'] = preptime
    recipe['instructions'] = json_data['recipeInstructions']
    recipe['yields'] = json_data['recipeYield']
    if 'aggregateRating' in json_data:
        rating = float(json_data['aggregateRating']['ratingValue'])
        # adjust "1 to 5" rating of chefkoch to "1 to 10" of gourmet
        recipe['rating'] = int(rating * 2)
    image = json_data['image']
    if image:
        if isinstance(image, list):
            image = image[0]
        recipe['image'], _ = getdatafromurl(image, content_type_check="image/")
    for ing in json_data['recipeIngredient']:
        ingredients.append(import_schema_ingredient(ing))


def import_schema_ingredient(ing):
    """Parse one chefkoch.de ingredient and return the corrected string
    suitable for ConvenientImporter.add_ing_from_text()
    Note that this parser has specific features only suitable for
    german recipes from chefkoch.de.

    @param ing: the ingredient
    @ptype ing: string
    @return: the adjusted ingredient string suitable for the default importer
    @rtype: string
    """
    if ing.startswith(" "):
        # amount is missing when ingredient starts with a space
        # this is likely specific for chefkoch.de
        ing = ing.strip()
        if ing.lower().startswith("evtl."):
            # add english optional tag
            ing = "optional: " + ing[5:]
    else:
        split = ing.split(None, 1)
        if len(split) > 1:
            try:
                # replace german comma with dot
                amount = split[0].replace(',', '.')
                # convert to fraction
                amount = Fraction(amount)
                # convert to string so non-integer fractions can be parsed
                # by gourmet
                amount = str(amount)
                ing = "%s %s" % (amount, split[1])
            except ValueError:
                warn("could not parse amount %r" % split[0])
                # do nothing
                pass
        else:
            # do nothing
            pass
    return ing


def getdatafromurl(url, content_type_check=None):
    """Download data from URL.
    @param url: the URL to download
    @ptype url: string
    @param content_type_check: if non-empty, only return data if the
      Content-Type header starts with the given string
    @ptype content_type_check: string
    @return: URL data or None, and the url (which may be redirected
      to a new URL)
    @rtype: tuple (string, string) or (None, string)
    """
    data = None
    try:
        sock = urllib2.urlopen(url)
        url = sock.geturl()
        if content_type_check:
            content_type = sock.info().get('content-type', 'application/octet-stream')
            if content_type.lower().startswith(content_type_check):
                data = sock.read()
        else:
            data = sock.read()
    except urllib2.URLError as msg:
        warn("could not get data from URL %r: %s" % (url, msg))
    return data, url


class ChefkochDePlugin(PluginPlugin):
    """This plugin matches for all URLs from chefkoch.de with path /rezepte/."""

    target_pluggable = 'webimport_plugin'

    def test_url(self, url, data):
        """Return positive integer if this URL should be parsed."""
        if 'chefkoch.de/rezepte/' in url:
            return 5
        return 0

    def get_importer(self, webpage_importer):
        """Use ChefkochDeParser instead of the default webpage_importer."""
        return ChefkochDeParser


def test_chefkoch_parser(url):
    """Try to parse a recipe for testing purposes."""
    from pprint import pprint
    data, url = getdatafromurl(url)
    print url
    json_data = parse_json_from_data(data, url)
    if json_data:
        recipe = {}
        ingredients = []
        import_schema_recipe(json_data, recipe, ingredients)
        recipe['image'] = recipe['image'][:40] + '...'
        pprint(recipe, indent=2)
        pprint(ingredients, indent=2)
    else:
        raise ValueError("error parsing %s with data %r" % (url, data))


if __name__ == '__main__':
    # the default URL is a random recipe
    url = "https://www.chefkoch.de/rezepte/zufallsrezept/"
    test_chefkoch_parser(url)
