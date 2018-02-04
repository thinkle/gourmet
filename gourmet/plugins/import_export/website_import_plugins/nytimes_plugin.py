from gourmet.plugin import PluginPlugin
import BeautifulSoup

NYT_CUISINES = [
    "African",
    "American",
    "Asian",
    "Australian",
    "Austrian",
    "Belgian",
    "Brazilian",
    "British",
    "Cajun",
    "Caribbean",
    "Central American",
    "Chinese",
    "Creole",
    "Cuban",
    "Eastern European",
    "Filipino",
    "French",
    "German",
    "Greek",
    "Icelandic",
    "Indian",
    "Indonesian",
    "Indian",
    "Indonesian",
    "Irish",
    "Italian",
    "Japanese",
    "Jewish",
    "Korean",
    "Latin American",
    "Malaysian",
    "Mediterranean",
    "Mexican",
    "Middle Eastern",
    "Moroccan",
    "New England",
    "Pakitani",
    "Portuguese",
    "Provencal",
    "Russian",
    "Scandinavian",
    "South American",
    "Southern",
    "Southwestern",
    "Spanish",
    "Thai",
    "Tibetan",
    "Turkish",
    "Vietnamese",
]

class NYTPlugin(PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        if 'nytimes.com' in url:
            return 5
        return 0

    def get_importer(self, webpage_importer):

        class NYTParser(webpage_importer.MenuAndAdStrippingWebParser):

            def maybe_add (self, el, tag):
                if el:
                    if type(el) in [list,BeautifulSoup.ResultSet]:
                        for e in el:
                            self.maybe_add(e,tag)
                    else:
                        if hasattr(el,'strip') and callable(el.strip):
                            if not el.strip():
                                return # Don't add empty strings or we screw things up royally
                            else:
                                print 'we are adding navigable string: ',el,'with tag',tag
                        self.preparsed_elements.append((el,tag))


            def preparse (self):
                self.preparsed_elements = []

                self.maybe_add(
                    self.soup.findAll(attrs={'itemprop':'description'}),
                    'instructions'
                    )
                self.maybe_add(
                    self.soup.findAll(attrs={'itemprop':'recipeIngredient'}),
                    'ingredients')
                for ingWrap in self.soup.findAll(attrs={'class':'recipe-ingredients-wrap'}):
                    self.maybe_add(
                        ingWrap.findAll(attrs={'class':'part-name'}),
                        'inggroup'
                        )
                for tb in self.soup.findAll(attrs={'class':'special-diets tag-block'}):
                    for a in tb.findAll('a'):
                        if a.text in NYT_CUISINES:
                            self.preparsed_elements.append((a,'cuisine'))
                        else:
                            self.preparsed_elements.append((a,'category'))
                self.maybe_add(
                    self.soup.findAll(attrs={'itemprop':'recipeInstructions'}),
                    'instructions'
                    )
                self.maybe_add(
                    self.soup.findAll('h1',attrs={'itemprop':'name'}),
                    'title'
                    )
                self.maybe_add(
                    self.soup.findAll(attrs={'class':'byline'}),
                    'source'
                    )
                self.maybe_add(
                    self.soup.findAll(attrs={'itemprop':'recipeYield'}),
                    'yields'
                    )
                # Handle time and stupid icon we have to skip...
                for ct in self.soup.findAll(attrs={'itemprop':'cookTime'}):
                    # Delete stupid time icon thing
                    stupid_icon = ct.parent.find('span')
                    if stupid_icon:
                        stupid_icon.extract()
                    print 'Add cooktime',ct.parent
                    self.maybe_add(
                        ct.parent,
                        'cooktime'
                        )
                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    webpage_importer.MenuAndAdStrippingWebParser.preparse(self)

        return NYTParser

