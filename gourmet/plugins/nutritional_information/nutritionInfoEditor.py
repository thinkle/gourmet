import gtk, gobject, pango
import gourmet.gtk_extras.pageable_store as pageable_store
import gourmet.gglobals as gglobals
import os, re
import gourmet.gtk_extras.cb_extras as cb
from gettext import gettext as _
from gettext import ngettext
import sqlalchemy
import gourmet.backends.db

from models import Nutrition, NutritionAlias

class NutritionInfoIndex:

    def __init__ (self, session, prefs=None, ui=None,
                  ingredients=None,
                  in_string = _('recipe'),
                  ):
        if ui:
            self.ui = ui
        else:
            self.ui = gtk.Builder()
            self.ui.add_from_file(os.path.join(gglobals.uibase,'nutritionDruid.ui'))
        self.session = session
        self.prefs = prefs
        # Initialize variables used for search
        self.search_string = ''
        self.use_regexp = None
        #self.search_by = 
        self.widget_names = ['treeview', 'searchByBox', 'searchEntry',
                             'searchButton', 'window',
                             'searchAsYouTypeToggle', 'regexpTog',
                             'nutritionFilterInLabel','nutritionFilterComboBox',
                             ]
        for w in self.widget_names:
            setattr(self,w,self.ui.get_object(w))
        self.prev_button = self.ui.get_object('prevButton')
        self.next_button = self.ui.get_object('nextButton')
        self.first_button = self.ui.get_object('firstButton')
        self.last_button = self.ui.get_object('lastButton')
        self.showing_label = self.ui.get_object('showingLabel')
        self.prev_button.connect('clicked',lambda *args: self.treeModel.prev_page())
        self.next_button.connect('clicked',lambda *args: self.treeModel.next_page())
        self.first_button.connect('clicked',lambda *args: self.treeModel.goto_first_page())
        self.last_button.connect('clicked',lambda *args: self.treeModel.goto_last_page())
        self.set_limit(ingredients,in_string)                
        self.ui.connect_signals({
            'iSearch':self.isearchCB,
            'search':self.searchCB,
            'search_as_you_type_toggle':self.search_as_you_typeCB,
            'filter_changed':self.filter_changed_cb,
            })
        self.makeTreeModel()
        self.setupTreeView()
        self.treeview.set_model(self.treeModel)
        self.update_showing_label()

    def set_limit (self, ingredients, in_string=_('recipe')):
        """Set ingredients to show in index.

        in_string is a string describing what these ingredients
        represent. For example, recipe.
        """
        self.ingredients = ingredients
        self.in_string = in_string
        cb.set_model_from_list(
            self.nutritionFilterComboBox,
            [self.in_string,_('entire database')]
            )
        cb.cb_set_active_text(self.nutritionFilterComboBox,self.in_string)

    def filter_changed_cb (self, *args):
        if self.nutritionFilterComboBox.get_active()==0:
            self.treeModel.search_kwargs = self.treeModel.limited_args
        else:
            self.treeModel.search_kwargs = {}
        self.reset()
        
    def setupTreeView (self):
        cssu = pageable_store.ColumnSortSetterUpper(self.treeModel)
        sortable = [1,2]
        for n,head in [[1,_('Ingredient Key')],
                       [2,_('USDA ID Number')],
                       [3,_('USDA Item Description')],
                       [4,_('Density Equivalent')],]:
            renderer = gtk.CellRendererText()
            # If we have gtk > 2.8, set up text-wrapping
            try:
                renderer.get_property('wrap-width')
            except TypeError:
                pass
            else:
                renderer.set_property('wrap-mode',pango.WRAP_WORD)
                renderer.set_property('wrap-width',200)
            #if n==self.VALUE_COL:
            #    renderer.set_property('editable',True)
            #    renderer.connect('edited',self.tree_edited,n,head)
            col = gtk.TreeViewColumn(head, renderer, text=n)
            col.set_resizable(True)
            self.treeview.append_column(col)
            if n in sortable: cssu.set_sort_column_id(col,n)
        
    def makeTreeModel (self):
        self.treeModel = NutStore(self.session,per_page=12,ingredients=self.ingredients)
        self.treeModel.connect('page-changed',self.model_changed_cb)
        self.treeModel.connect('view-changed',self.model_changed_cb)

    def reset (self):
        """Rebuild our model, regardless."""
        self.search_string = 'NO ONE WOULD EVER SEARCH FOR THIS'
        self.doSearch()

    # Set up searching...
    def doSearch (self):
        """Do the actual searching."""
        last_search = self.search_string
        self.search_string = self.searchEntry.get_text()
        #last_by = self.search_by
        #self.search_by = cb.cb_get_active_text(self.searchByBox)
        last_regexp = self.use_regexp
        self.use_regexp = self.regexpTog.get_active()
        if (#self.search_by==last_by and
            self.search_string==last_search and
            self.use_regexp==last_regexp):
            # Don't do anything...
            return
        # RESET THE VIEW IF NEED BE
        #if (self.search_string.find(last_search)!=0 or
        #    #self.search_by != last_by or
        #    self.use_regexp != last_regexp):
        #    self.treeModel.reset_view()
        self.treeModel.limit(self.search_string,column='ingkey',
                             search_options={'use_regexp':self.use_regexp,}
                             )

    def isearchCB (self, *args):
        if self.searchAsYouTypeToggle.get_active():
            self.doSearch()

    def searchCB (self, *args):
        self.doSearch()

    def search_as_you_typeCB (self, *args):
        if self.searchAsYouTypeToggle.get_active():
            self.searchButton.hide()
        else: self.searchButton.show()

    def model_changed_cb (self, model):
        if model.page==0:
            self.prev_button.set_sensitive(False)
            self.first_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)
            self.first_button.set_sensitive(True)
        if model.get_last_page()==model.page:
            self.next_button.set_sensitive(False)
            self.last_button.set_sensitive(False)
        else:
            self.next_button.set_sensitive(True)
            self.last_button.set_sensitive(True)
        self.update_showing_label()
        
    def update_showing_label (self):
        bottom,top,total = self.treeModel.showing()
        if top >= total and bottom==1:
            lab = ngettext('%s ingredient','%s ingredients',top)%top
        else:
            # Do not translate bottom, top and total -- I use these fancy formatting
            # strings in case your language needs the order changed!
            lab = _('Showing ingredients %(bottom)s to %(top)s of %(total)s'%locals())
        self.showing_label.set_markup('<i>' + lab + '</i>')

    def get_selected_ingredient (self, *args):
        mod,itr = self.treeview.get_selection().get_selected()
        return mod.get_value(itr,0)
        

class MockObject:
    def __init__ (self, **kwargs):
        for k,v in kwargs.items(): setattr(self,k,v)

class NutStore (pageable_store.PageableViewStore):

    #__gsignals__ = {
    #    'view-changed':(gobject.SIGNAL_RUN_LAST,
    #                    gobject.TYPE_NONE,
    #                    ()),
    #    }

    KEY = _('Key')+':'
    USDA_ID = _('Item')+':'
    USDA_ITEM_NUMBER = _('USDA ID#')+':'
    USDA_DESC = _('USDA Item Description')+':'
    DENSITY_EQUIVALENT = _('Density Equivalent')
    columns=['obj','ingkey','ndbno','desc','density_equivalent']
    column_types=[gobject.TYPE_PYOBJECT, #row ref
                  str, # key
                  int, # ID
                  str, # description
                  str, # Density equivalent
                  #float, # Density
                  ]

    def __init__ (self,
                  session,
                  per_page=15,
                  ingredients=None
                  ):
        self.session = session
        self.query = self.session.query(NutritionAlias.ingkey,
                                        NutritionAlias.density_equivalent,
                                        Nutrition.desc,
                                        Nutrition.ndbno)
        if ingredients:
            self.limited_query = self.search_query = self.query.filter(NutritionAlias.ingkey.in_(ingredients))
        else:
            self.limited_query = self.search_query = self.query
        self.ingredients = ingredients
        vw = self.get_vw(self.search_query)
        pageable_store.PageableViewStore.__init__(self,
                                                  vw,
                                                  columns=self.columns,
                                                  column_types=self.column_types,
                                                  per_page=per_page
                                                  )

    def get_vw (self, query, search_extras_regexp=None):
        """Get a view for our model.

        Our model will consist of items found in our database + any
        ingredients specified when we were created. In other words,
        we'll list all ingredients that we're told about, whether
        they're in the nutrition aliases table or not.

        query is the query we'll perform on our database.
        search_extras_text is a regexp used to filter our "extras."
        """
        vw = query.all()
        #vw = self.session.fetch_join(self.session.nutritionaliases_table,self.session.nutrition_table,
        #                        'ndbno','ndbno',sort_by=[('ingkey',1)],
        #                        **search_kwargs)
        # We must show ingredients whether we have them or not...
        extras = []
        if self.ingredients:
            ings_to_add = self.ingredients[:]
            if search_extras_regexp:
                ings_to_add = filter(lambda i: re.match(search_extras_regexp,
                                                        i),
                                     ings_to_add)
            for row in vw:
                while row.ingkey in ings_to_add:
                    ings_to_add.remove(row.ingkey)
            for extra_ing in ings_to_add:
                if extra_ing:
                    extras.append(MockObject(ingkey=extra_ing,
                                             ndbno=0,desc='Not in database',density_equivalent=None)
                                  )
        return vw + extras
        

    def limit  (self, txt, column='ingkey', search_options={}):
        if not txt:
            vw = self.get_vw(self.search_kwargs)
        else:
            if search_options ['use_regexp']:
                s = ('REGEXP',txt)
                extras_search = '.*'+txt+'.*'
            else:
                s = ('LIKE','%'+txt.replace('%','%%')+'%')
                extras_search = '.*'+re.escape(txt)+'.*'
            kwargs = self.search_kwargs.copy()
            if kwargs.has_key(column):
                kwargs[column] = ('and',[kwargs[column],s])
            else:
                kwargs[column]=s
            vw = self.get_vw(kwargs,extras_search)
        self.change_view(vw)

    def _get_value_ (self, row, attr): return getattr(row,attr)

    def _get_slice_ (self, bottom, top):
        try:
            return [[r] + [self._get_value_(r,col) for col in self.columns[1:]] for r in self.view[bottom:top]]
        except:
            print '_get_slice_ failed with',bottom,top
            raise
        
        
if __name__ == '__main__':
    import gourmet.recipeManager as rm
    rd = rm.RecipeManager()
    nie = NutritionInfoIndex(rd,ingredients=['cilantro','tomato','basil','water','onion, red','onion, white','scallion','hare'])
    nie.window.show()
    nie.window.connect('delete-event',gtk.main_quit)
    #nie.show_index_page()
    gtk.main()
