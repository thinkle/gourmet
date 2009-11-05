from gourmet.plugin import PluginPlugin
import re

class AllRecipesPlugin (PluginPlugin):
    target_pluggable = 'webimport_plugin'

    def do_activate (self, pluggable):
        pass
    
    def test_url (self, url, data):
        if 'allrecipes.com' in url: 
            return 5

    def get_importer (self, webpage_importer):
        class All_Recipes_Parser (webpage_importer.MenuAndAdStrippingWebParser):
            def preparse (self):
                webpage_importer.MenuAndAdStrippingWebParser.preparse(self)
                #Title
                for title_element in self.soup('h1',{'id':'itemTitle'}):
                    self.preparsed_elements.append((title_element,'title'))
                #Ingredients    <div class="recipe centercontent2">, li
                for recipe in self.soup('div',{'class':'recipe centercontent2'}):
                    bulk = []
                    bulk.append(recipe('li'))
                    self.preparsed_elements.append((bulk[0],'ingredients'))
                    #Directions     div class="recipe centercontent2", li
                    self.preparsed_elements.append((bulk[2],'directions'))
                    #Servings       
                    #div class="recipe centercontent2",<input name="ctl00$CenterColumnPlaceHolder$txtConversion" type="text" value="9"
                    #or
                    #<div id="nutri-info">, 1st p
                    #self.soup('span',{'class':'yield'})
                    #Cook Time
                    for c_time in self.soup('tr',{'id':"ctl00_CenterColumnPlaceHolder_rowCook"}):
                        self.preparsed_elements.append((c_time('b'),'cooktime'))
                    #Prep Time      tr id="ctl00_CenterColumnPlaceHolder_rowPrep", b
                    for element in self.soup('tr',{'id':"ctl00_CenterColumnPlaceHolder_rowPrep"}):
                        self.preparsed_elements.append((element('b'),'preptime'))
                for to_ignore in ['review-block','nutri-div','modal','rb-grey','rvr-grey',
                                  'left','right','modal-upload-a-photo','modal-content',
                                  'modal userWhoSaved','saved custom','recipe-tools-container',
                                  'midpagetabs']:
                    for div in self.soup('div',{'class':to_ignore}):
                        self.preparsed_elements.append((div,'ignore'))
                for to_ignore in ['countries','ctl00_divModal','country','rb','copyright',]:
                    for div in self.soup('div',{'id':to_ignore}):
                        self.preparsed_elements.append((div,'ignore'))
                

        return All_Recipes_Parser
