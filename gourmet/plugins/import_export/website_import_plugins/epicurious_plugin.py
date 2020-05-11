from gourmet.plugin import PluginPlugin

class EpicuriousPlugin(PluginPlugin):

    target_pluggable = 'webimport_plugin'

    def test_url (self, url, data):
        if 'epicurious.com' in url:
            return 5
        return 0

    def get_importer(self, webpage_importer):

        class EpicuriousParser(webpage_importer.WebParser):

            def preparse (self):
                self.preparsed_elements = []

                name = self.soup.find("h1", itemprop="name")
                if name:
                    self.preparsed_elements.append((name.text.strip(), 'title'))

                preptime = self.soup.find('dd', class_='active-time')
                if preptime:
                    self.preparsed_elements.append((preptime.text, 'preptime'))

                cooktime = self.soup.find('dd', class_='total-time')
                if cooktime:
                    self.preparsed_elements.append((cooktime.text, 'cooktime'))

                servings = self.soup.find('dd', class_='yield')
                if servings:
                    self.preparsed_elements.append((servings.text, 'yields'))

                ingredients_result = self.soup.find_all('ol', class_='ingredient-groups')[0].find_all('li')
                el_list = []
                for help_result in ingredients_result:
                    if help_result.find('strong'):
                        # This is where ingredient subheading would be.
                        el_list.append((help_result.find('strong').text, 'ingredients'))
                    playful = help_result.find_all('li')
                    if playful:
                        el_list.extend([(tag.text, 'ingredients') for tag in playful])
                self.preparsed_elements.extend(el_list)

                direction_list = []
                directions_result = self.soup.find_all('ol', class_='preparation-groups')
                directions_helpful = directions_result[0].find_all('li', class_='preparation-group')
                for li in directions_helpful:
                    if li.find('strong'):
                        # This is where direction sub-heading would be
                        direction_list.append((li.find('strong').text.strip(), 'recipe'))
                    triumph = li.find_all('li', 'preparation-step')
                    for other_li in triumph:
                        direction_list.append((other_li.text.strip(), 'recipe'))
                self.preparsed_elements.extend(direction_list)

                rating = self.soup.find('span', class_='rating')
                if rating:
                    self.preparsed_elements.append((rating.text, 'rating'))

                mod_description = self.soup.find('div', class_='dek')
                if mod_description:
                    self.preparsed_elements.append((mod_description.text, 'modifications'))

                mod_chefs_note = self.soup.find('div', class_='chef-notes-content')
                if mod_chefs_note:
                    self.preparsed_elements.append((mod_chefs_note.text, 'modifications'))

                categories = self.soup.find_all(itemprop='recipeCategory')
                if categories:
                    for category in categories:
                        self.preparsed_elements.append((category.text, 'category'))

                if self.preparsed_elements:
                    self.ignore_unparsed = True
                else:
                    webpage_importer.WebParser.preparse(self)

        return EpicuriousParser
