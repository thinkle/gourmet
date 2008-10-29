__author__ = 'Thomas Hinkle <Thomas_Hinkle@alumni.brown.edu>'

from dogtail import tree, predicate
from dogtail.utils import run
from time import sleep,time

# Convenience function to workaround annoyingness

def find_children (node, *args, **kwargs):
    p = predicate.GenericPredicate(*args,**kwargs)
    return node.findChildren(p)

import gourmet.version
appname = gourmet.version.appname

times = []

def time_me (f):
    def _ (*args,**kwargs):
        t = time()
        ret = f(*args,**kwargs)
        t = time() - t
        times.append((f.__name__,args,kwargs,t))
        return ret
    return _

class Row (list):

    def __init__ (self, headers):
        self.headers = headers

    def __getattr__ (self, a):
        if a in self.headers:
            return self[self.headers.index(a)]
        else:
            raise AttributeError

class GourmetIndex:

    def __init__ (self, gr):
        self.gr = gr
        self.search_box = gr.child(roleName='text')
        self.search_by_menu = gr.child(roleName='combo box')
        self.rectable = gr.child(roleName='table')
        self.column_headers = find_children(self.rectable,roleName='table column header')
        self.headers = [c.text for c in self.column_headers]
        self.table_row_len = len(self.headers)
        self.forward_button = self.gr.child(name='Forward')
        self.back_button = self.gr.child(name='Back')

    @time_me
    def set_search_text (self, txt):
        self.search_box.text = txt

    @time_me
    def set_search_by (self, txt):
        self.search_by_menu.menuItem(txt).click()

    def get_n_results (self):
        s = filter(lambda x: x.find('Showing')==0,self.gr.getUserVisibleStrings())[0]
        return int(s.split(' ')[-1])

    def get_table_rows (self):
        cc = find_children(self.rectable,roleName='table cell')
        rows = []
        row = Row(self.headers)
        for n,c in enumerate(cc):
            row.append(c)
            if n and (n % self.table_row_len)==0:
                rows.append(row)
                row = Row(self.headers)
        return rows

    @time_me
    def toggle_sort (self,header):
        n = self.headers.index(header)
        self.column_headers[n].click()

    @time_me
    def open_recipe (self,n=0):
        cell = self.get_table_rows()[n][1]
        title = cell.text
        cell.grabFocus()
        cell.doAction('activate')
        window_name = 'Recipe Card: '+title
        child = self.gr.child(name=window_name)
        return RecCardDisplay(child)

    @time_me
    def new_recipe (self):
        self.gr.child('New Recipe').click()
        child = self.gr.child(name='Edit Recipe: New Recipe')
        return RecEditDisplay(child)

class RecCardDisplay:
    def __init__ (self, rc):
        self.rc = rc
        self.edit_ingredients_button = self.rc.child('Edit ingredients')
        self.mult_button,self.servings_button = find_children(self.rc.child,roleName='spin button')

    def multiply (self, n):
        if self.servings_button.text:
            self.servings_button.text = str(int(self.servings_button.text)*2)
        else:
            self.mult_button.text = '2'

    def edit_ings (self, n):
        self.edit_ingredients_button.click()
        title = self.rc.name.split(':')[1].strip()
        child = self.gr.child(name='Edit Recipe: '+title)
        return RecEditDisplay(child)

class RecEditDisplay:
    def __init__ (self, rc):
        self.rc = rc
        self.save_button = self.rc.child(name='Save',roleName='push button')
        self.revert_button = self.rc.child(name='Revert',roleName='push button')
        self.att_entries = {}
        for att in ['title','category','preparation time','cooking time','cuisine','servings','source']:
            try: self.att_entries[att] = self.rc.child(name=att)
            except: print 'problem getting',att

    def enter_attr (self, att, txt):
        self.att_entries[att].text = txt

print 'Starting ',appname
try: run('gourmet --gtk-module=libgail.so libgail-gnome.so libkeymouselistener.so libdwellmouselistener.so libatk-bridge.so')
except: pass
print 'Gourmet is started up'
gourmet_root = tree.root.application(appname)

gi = GourmetIndex(gourmet_root)

def test_search (gi):
    gi.set_search_by('ingredient')
    gi.set_search_text('flour')
    print gi.get_n_results(),'for ingredient flour'
    gi.set_search_text('sugar')
    print gi.get_n_results(),'for ingredient sugar'
    gi.set_search_text('garlic')
    print gi.get_n_results(),'for ingredient garlic'
    gi.set_search_text('dessert')
    gi.set_search_by('category')
    print gi.get_n_results(),'for category dessert'

def test_entry (gi):
    entry = gi.new_recipe()
    entry.enter_attr('servings','4')
    entry.enter_attr('title','Fooey')
    entry.enter_attr('category','Dessert')
    entry.enter_attr('cooking time','30 minutes')
    entry.enter_attr('preparation time','1 1/2 hours')
    entry.enter_attr('source','1 1/2 hours')
    
    


