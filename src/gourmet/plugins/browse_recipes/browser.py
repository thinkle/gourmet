import os.path
from gettext import gettext as _

from gi.repository import GdkPixbuf, GObject, Gtk
from sqlalchemy.sql import and_, not_

import gourmet.convert as convert
from gourmet.gglobals import DEFAULT_ATTR_ORDER, REC_ATTR_DIC
from gourmet.gtk_extras.ratingWidget import star_generator
from gourmet.image_utils import bytes_to_pixbuf

from .icon_helpers import (ICON_SIZE, attr_to_icon, get_recipe_image,
                           get_time_slice, scale_pb)

curdir = os.path.split(__file__)[0]


class RecipeBrowserView(Gtk.IconView):

    __gsignals__ = {
        'recipe-selected': (GObject.SignalFlags.RUN_LAST,
                            GObject.TYPE_INT, [GObject.TYPE_INT]),
        'path-selected': (GObject.SignalFlags.RUN_LAST,
                          GObject.TYPE_STRING, [GObject.TYPE_STRING])
    }

    def __init__(self, rd):
        self.rd = rd
        super().__init__()
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_item_width(ICON_SIZE)
        self.models = {}
        self.set_model()
        self.set_text_column(1)
        self.set_pixbuf_column(2)
        self.connect('item-activated', self.item_activated_cb)
        self.switch_model('base')
        self.path = ['base']

    def new_model(self):
        return Gtk.ListStore(str,  # path
                             str,  # text
                             GdkPixbuf.Pixbuf,  # image
                             GObject.TYPE_PYOBJECT)

    def switch_model (self, path, val=None):
        if path not in self.models:
            self.build_model(path,val)
        self.set_model(self.models[path])

    def build_model (self, path,val):
        if path == 'base':
            self.build_base_model()
        elif not '>' in path:
            self.build_first_level_model(path)
        else:
            self.build_recipe_model(path,val)

    def build_base_model(self):
        m = self.models['base'] = self.new_model()
        self.set_model(m)
        for item in DEFAULT_ATTR_ORDER:
            if item in ['title', 'link', 'yields']:
                continue
            pb = self.get_base_icon(item)
            m.append((item, (REC_ATTR_DIC[item]), pb, None))

    def get_base_icon(self, item):
        return attr_to_icon.get(item, attr_to_icon['category'])

    def get_pixbuf(self, attr: str, val: str) -> GdkPixbuf.Pixbuf:
        if attr=='category':
            tbl = self.rd.recipe_table.join(self.rd.categories_table)
            col = self.rd.categories_table.c.category
            if hasattr(self, 'category_images'):
                stment = and_(col == val, self.rd.recipe_table.c.image != None,
                              self.rd.recipe_table.c.image != bytes(),
                              not_(self.rd.recipe_table.c.title.in_(self.category_images)))
            else:
                stment = and_(col == val, self.rd.recipe_table.c.image != None,
                              self.rd.recipe_table.c.image != bytes())
            result = tbl.select(stment,limit=1).execute().fetchone()
            if not hasattr(self, 'category_images'):
                self.category_images = []
            if result:
                self.category_images.append(result.title)
        elif attr == 'rating':
            return star_generator.get_pixbuf(val)
        elif attr in ['preptime', 'cooktime']:
            return get_time_slice(val)
        else:
            tbl = self.rd.recipe_table
            col = getattr(self.rd.recipe_table.c, attr)
            stment = and_(col == val, self.rd.recipe_table.c.image != None,
                          self.rd.recipe_table.c.image != bytes())
            result = tbl.select(stment,limit=1).execute().fetchone()
        if result and result.thumb:
            return scale_pb(bytes_to_pixbuf(result.image))
        else:
            return self.get_base_icon(attr) or self.get_base_icon('category')

    def convert_val(self, attr, val) -> str:
        if attr in ['preptime', 'cooktime']:
            if val:
                return convert.seconds_to_timestring(int(val))
            else:
                return 'None'
        elif attr == 'rating':
            if not val:
                return _('Unrated')
            else:
                val = int(val)
                txt = str(int(val) // 2)
                if val % 2:
                    txt += ' 1/2'
                txt += ' ' + _('Stars')
                return txt
        else:
            return str(val)

    def build_first_level_model (self, attribute):
        m = self.models[attribute] = self.new_model()
        if attribute == 'category':
            for n, val in self.rd.fetch_count(self.rd.categories_table, 'category'):
                # FIXME: known bug here -- this includes deleted recs in the count
                to_add = (f"{attribute}>{val}", f"{val} ({n})", self.get_pixbuf(attribute, val), val)
                m.append(to_add)
        else:
            for n, val in self.rd.fetch_count(self.rd.recipe_table, attribute, deleted=False):
                if n == 0:
                    continue
                to_add = (f"{attribute}>{val}", f"{self.convert_val(attribute, val)} ({n})",
                          self.get_pixbuf(attribute, val), val)
                m.append(to_add)

    def build_recipe_model (self, path, val):
        m = self.models[path] = self.new_model()
        searches = [{'column':'deleted','operator':'=','search':False}]
        path = path.split('>')
        while path:
            _ = path.pop()
            attr = path.pop()
            if val is None:
                searches.append({'column':attr,'search':val,'operator':'='})
            else:
                searches.append({'column':attr,'search':val})
        for recipe in self.rd.search_recipes(searches):
            pb = get_recipe_image(recipe)
            m.append((str(recipe.id),recipe.title,pb,None))

    def set_path (self, path):
        self.path = ['base']
        for level in path.split('>'):
            self.path.append(level)
        self.switch_model(path)

    def item_activated_cb (self, iv, path):
        row = self.get_model()[path]
        step = row[0]; val = row[3]
        try:
            rid = int(step)
        except ValueError:
            self.switch_model(step,val)
            self.path.append(step)
            self.emit('path-selected',step)
        else:
            self.emit('recipe-selected',rid)

    def get_selected_recipes (self):
        paths = self.get_selected_items()
        model = self.get_model()
        recipes = [int(model[p][0]) for p in paths]
        def just_recs_filter (item):
            try:
                int(item)
            except:
                return False
            else:
                return True
        recipes = list(filter(just_recs_filter,recipes))
        return [r for r in self.rd.recipe_table.select(self.rd.recipe_table.c.id.in_(recipes)).execute()]

    def reset_model (self):
        self.models = {}
        self.switch_model(self.path[-1])

    def back (self):
        if len(self.path) > 1:
            self.ahead = self.path.pop()
            self.switch_model(self.path[-1])


class RecipeBrowser(Gtk.VBox):

    def __init__(self, rd):
        Gtk.VBox.__init__(self)
        self.view = RecipeBrowserView(rd)
        self.buttons = []
        self.button_bar = Gtk.HBox()
        self.button_bar.set_spacing(6)
        self.pack_start(self.button_bar, False, False, 0)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.view)
        self.pack_start(sw, True, True, 0)
        home_button = Gtk.Button(stock=Gtk.STOCK_HOME)
        self.button_bar.pack_start(home_button, False, False, 0)
        home_button.connect('clicked', self.home)
        home_button.show()
        self.view.connect('path-selected', self.path_selected_cb)
        self.view.show()
        sw.show()

    def home (self, *args):
        self.view.set_path('base')

    def path_selected_cb (self, view, path):
        self.button_bar.show()
        for b in self.buttons:
            self.button_bar.remove(b)
        self.buttons = []
        so_far = ''
        for step in path.split('>'):
            self.append_button(so_far + step)
            so_far += step + '>'

    def append_button (self, path):
        if '>' in path:
            attribute, value = path.split('>')
            txt = self.view.convert_val(attribute, value)
        else:
            txt = path
        self.buttons.append(Gtk.Button(REC_ATTR_DIC.get(txt,txt)))
        self.buttons[-1].connect('clicked',lambda *args: self.view.set_path(path))
        self.button_bar.pack_start(self.buttons[-1], False, False, 0)
        self.buttons[-1].show()


def try_out ():
    import gourmet.recipeManager
    rb = RecipeBrowser(gourmet.recipeManager.get_recipe_manager())
    vb = Gtk.VBox()
    vb.pack_start(rb, True, True, 0)
    rb.show()
    w = Gtk.Window()
    w.add(vb)
    w.show(); vb.show()
    w.set_size_request(800,500)
    w.connect('delete-event',Gtk.main_quit)
    Gtk.main()

if __name__ == '__main__':
    try_out()
