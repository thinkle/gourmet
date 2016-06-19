from __future__ import print_function

from gourmet.plugin import PluginPlugin

class EpicuriousPlugin(PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        if 'epicurious.com' in url:
            return 5
        return 0

    def get_importer(self, webpage_importer):

        class EpicuriousParser(webpage_importer.MenuAndAdStrippingWebParser):

            def preparse (self):
                self.preparsed_elements = []

                title = self.soup.title
                if title:
                    self.preparsed_elements.append((title, 'title'))

                preptime = self.soup.find('dd', 'active-time')
                if preptime:
                    self.preparsed_elements.append((preptime,'preptime'))

                cooktime = self.soup.find('dd', 'total-time')
                if cooktime:
                    self.preparsed_elements.append((cooktime,'cooktime'))

                servings = self.soup.find('dd', 'yield')
                if servings:
                    self.preparsed_elements.append((servings, 'yields'))

                ingredients_result = self.soup.findAll('ol', 'ingredient-groups')[0].findAll('li')
                el_list = []
                for help_result in ingredients_result:
                    if help_result.find('strong'):
                        #This is where ingredient subheading would be.
                        el_list.append((help_result.find('strong'), 'ingredients'))
                    playful = help_result.findAll('li')
                    if len(playful) != 0:
                        el_list.extend([(tag, 'ingredients') for tag in playful])
                self.preparsed_elements.extend(el_list)

                direction_list = []
                directions_result = self.soup.findAll('ol', 'preparation-groups')
                directions_helpful = directions_result[0].findAll('li','preparation-group')
                for li in directions_helpful:
                    if li.find('strong'):
                        # This is where direction sub-heading would be
                        direction_list.append((li.find('strong'), 'instructions'))
                    triumph = li.findAll('li', 'preparation-step')
                    for other_li in triumph:
                        direction_list.append((other_li, 'instructions'))
                self.preparsed_elements.extend(direction_list)

                rating = self.soup.find('span', 'rating')
                if rating:
                    self.preparsed_elements.append((rating, 'rating'))

                mod_description = self.soup.find('div', 'dek')
                if mod_description:
                    self.preparsed_elements.append((mod_description, 'modifications'))

                mod_chefs_note = self.soup.find('div', 'chef-notes-content')
                if mod_chefs_note:
                    self.preparsed_elements.append((mod_chefs_note, 'modifications'))

                categories = self.soup.findAll(itemprop='recipeCategory')
                if categories:
                    for category in categories:
                        self.preparsed_elements.append((category, 'category'))

                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    webpage_importer.MenuAndAdStrippingWebParser.preparse(self)

        return EpicuriousParser