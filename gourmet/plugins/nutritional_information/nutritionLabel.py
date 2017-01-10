import gtk, pango, gobject
from gettext import gettext as _
import gourmet.defaults

MAJOR = 0
MINOR = 1
TINY = 2
SEP = 3
SHOW_PERCENT = True
DONT_SHOW_PERCENT = False
MAIN_NUT_LAYOUT = [(_('Calories'),MAJOR,'kcal',
                'kcal',DONT_SHOW_PERCENT,''),
               SEP,
               (_('Total Fat'),MAJOR,'fat',
                ['fasat','famono','fapoly'],SHOW_PERCENT,'g'),
               (_('Saturated Fat'),MINOR,'fasat',
                'fasat',SHOW_PERCENT,'g'),
               (_('Cholesterol'),MAJOR,'cholestrl',
                'cholestrl',SHOW_PERCENT,'mg'),
               (_('Sodium'),MAJOR,'sodium',
                'sodium',SHOW_PERCENT,'mg'),
               (_('Total Carbohydrate'),MAJOR,'carb',
                'carb',SHOW_PERCENT,'g'),
               (_('Dietary Fiber'),MINOR,
                'fiber','fiber',SHOW_PERCENT,'g'),
               (_('Sugars'),MINOR,'sugar',
                'sugar',DONT_SHOW_PERCENT,'g'),
               (_('Protein'),MAJOR,'protein',
                'protein',SHOW_PERCENT,'g'),
                   ]

DETAIL_NUT_LAYOUT = [
               (_('Alpha-carotene'),TINY,'alphac',
                'alphac',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Ash'),TINY,'ash',
                'ash',DONT_SHOW_PERCENT,'g'),
               (_('Beta-carotene'),TINY,'betac',
                'betac',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Beta Cryptoxanthin'),TINY,'betacrypt',
                'betacrypt',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Calcium'),TINY,'calcium',
                'calcium',SHOW_PERCENT,'mg'),
               (_('Copper'),TINY,'copper',
                'copper',SHOW_PERCENT,'mg'),
               (_('Folate Total'),TINY,'folatetotal',
                'folatetotal',SHOW_PERCENT,u'\u00B5g'),
               (_('Folic acid'),TINY,'folateacid',
                'folateacid',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Food Folate'),TINY,'foodfolate',
                'foodfolate',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Dietary folate equivalents'),TINY,'folatedfe',
                'folatedfe',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Iron'),TINY,'iron',
                'iron',SHOW_PERCENT,'mg'),
               (_('Lycopene'),TINY,'lypocene',
                'lypocene',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Lutein+Zeazanthin'),TINY,'lutzea',
                'lutzea',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Magnesium'),TINY,'magnesium',
                'magnesium',SHOW_PERCENT,'mg'),
               (_('Manganese'),TINY,'manganese',
                'manganese',SHOW_PERCENT,'mg'),
               (_('Niacin'),TINY,'niacin',
                'niacin',SHOW_PERCENT,'mg'),
               (_('Pantothenic Acid'),TINY,'pantoacid',
                'pantoacid',SHOW_PERCENT,'mg'),
               (_('Phosphorus'),TINY,'phosphorus',
                'phosphorus',SHOW_PERCENT,'mg'),
               (_('Potassium'),TINY,'potassium',
                'potassium',SHOW_PERCENT,'mg'),
               (_('Vitamin A'),TINY,'vitarae',
                'vitarae',SHOW_PERCENT,u'\u00B5g'),
               (_('Retinol'),TINY,'retinol',
                'retinol',SHOW_PERCENT,u'\u00B5g'),
               (_('Riboflavin'),TINY,'riboflavin',
                'riboflavin',SHOW_PERCENT,'mg'),
               (_('Selenium'),TINY,'selenium',
                'selenium',SHOW_PERCENT,u'\u00B5g'),
               (_('Thiamin'),TINY,'thiamin',
                'thiamin',SHOW_PERCENT,'mg'),
               (_('Vitamin A (IU)'),TINY,'vitaiu',
                'vitaiu',SHOW_PERCENT,'IU'),
               (_('Vitamin A (RAE)'),TINY,'vitarae',
                'vitarae',DONT_SHOW_PERCENT,u'\u00B5g'),
               (_('Vitamin B6'),TINY,'vitaminb6',
                'vitaminb6',SHOW_PERCENT,'mg'),
               (_('Vitamin B12'),TINY,'vitb12',
                'vitb12',SHOW_PERCENT,u'\u00B5g'),
               (_('Vitamin C'),TINY,'vitaminc',
                'vitaminc',SHOW_PERCENT,'mg'),
               (_('Vitamin E'),TINY,'vite',
                'vite',SHOW_PERCENT,'mg'),
               (_('Vitamin K'),TINY,'vitk',
                'vitk',SHOW_PERCENT,'mg'),
               (_('Zinc'),TINY,'zinc',
                'zinc',SHOW_PERCENT,'mg'),
               ]

NUT_LAYOUT = MAIN_NUT_LAYOUT + DETAIL_NUT_LAYOUT

RECOMMENDED_INTAKE = {
        'fat':0.30 / 9, # 30% of calories * 9 cal / g.
        'fasat':0.10 / 9, #10% of calories * 9 cal /g.
        'carb':0.6 / 4, #60% of calories * 4 cal / g.
        'protein':0.10 / 4, #10% of calories * 4 cal/g.
        'fiber':11.5/1000, #11.5 grams / 1000calories
        'sodium':2400.0/2000, # 2400 mg per typical 2000 c diet
        'potassium':3500.0/2000,
        'iron':18.0/2000,
        'calcium':1000.0/2000,
        'cholestrl':300.0/2000,
        'vitarae':900.0/2000,
        'magnesium':420.0/2000,
        'vitaminc':60.0/2000,
        'vitaiu':5000.0/2000,
        'vite':30.0/2000,
        'vitk':80.0/2000,
        'thiamin':1.5/2000,
        'riboflavin':1.7/2000,
        'niacin':20.0/2000,
        'vitaminb6':2.0/2000,
        'folatetotal':400.0/2000,
        'vitb12':6.0/2000,
        'pantoacid':10.0/2000,
        'phosphorus':1000.0/2000,
        'magnesium':400.0/2000,
        'zinc':15.0/2000,
        'selenium':70.0/2000,
        'copper':2.0/2000,
        'manganese':2.0/2000,
        'chromium':120.0/2000,
        'molybdenum':75.0/2000,
        'chloride':3400.0/2000,
        }


class NutritionLabel (gtk.VBox, gobject.GObject):
    """Provide a nutritional label that looks like standard FDA
    labels."""

    __gtype_name__ = 'NutritionLabel'

    bold_font = pango.FontDescription()
    bold_font.set_weight(pango.WEIGHT_BOLD)
    tiny_font = pango.FontDescription()
    tiny_font.set_size(pango.SCALE*9)
    background = gtk.gdk.Color(255,0,0)
    foreground = gtk.gdk.Color(255,255,255)

    calories_per_day = 2000

    __gsignals__ = {
        'calories-changed':(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE,()),
        'ingredients-changed':(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE,()),
        'label-changed':(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE,()),
        }

    def __init__ (self, prefs=None,
                  rec=None,
                  custom_label=None,
                  pressable=True
                  ):
        self.pressable = pressable
        self.toggles = {}; self.__toggling__ = False
        self.active_name = None
        self.active_unit = None
        self.active_label = None
        self.active_properties = None
        self.active_button_markup = ('<span background="#ffff00">','</span>')
        self.custom_label = custom_label
        self.prefs = prefs
        self.rec = rec
        start_at = 4
        gobject.GObject.__init__(self)
        gtk.VBox.__init__(self)
        #,2,len(NUT_LAYOUT)+start_at)
        self.show()
        self.tt = gtk.Tooltips()
        self.yieldLabel = gtk.Label()
        self.set_yields(0)
        self.nutrition_display_info = []
        #self.attach(self.yieldLabel,
        #            0,2,0,1)
        self.yieldLabel.show()
        self.yieldLabel.set_alignment(0,0.5)
        self.missingLabel = self.make_missing_label()
        #self.attach(self.missingLabel,0,2,1,2)
        self.pack_start(self.missingLabel,fill=False,expand=False)
        self.pack_start(self.yieldLabel,fill=False,expand=False)
        # setup daily value button to display calories/day assumption
        # and to allow changing it via a nifty little button
        dvb,eb = self.make_dv_boxes()
        dvb.show()
        self.cal_per_day_box = gtk.HBox();
        self.cal_per_day_box.show()
        vb = gtk.VBox(); vb.show()
        vb.pack_start(dvb,fill=False,expand=False)
        vb.pack_start(eb,fill=False,expand=False)
        self.cal_per_day_box.pack_end(vb)
        self.pack_start(self.cal_per_day_box)
        self.tt.enable()
        self.main_table = gtk.Table(); self.main_table.show()
        self.main_table.set_col_spacings(18)
        self.pack_start(self.main_table)
        self.sub_table = gtk.Table(); self.sub_table.show()
        self.sub_table.set_col_spacings(18)
        self.nutexpander = gtk.Expander(_('Vitamins and minerals'))
        self.nutexpander.show()
        self.nutexpander.add(self.sub_table)
        self.pack_start(self.nutexpander)
        for table,layout in [(self.main_table,MAIN_NUT_LAYOUT),
                             (self.sub_table,DETAIL_NUT_LAYOUT),
                             ]:
            for n,nutstuff in enumerate(layout):
                if nutstuff == SEP:
                    hs = gtk.HSeparator()
                    table.attach(hs,0,2,n+start_at,n+start_at+1,xoptions=gtk.FILL)
                    hs.show()
                    continue
                label,typ,name,properties,show_percent,unit = nutstuff
                hb = gtk.HBox()
                permanentl = gtk.Label()
                permanentl.set_alignment(0,0.5)
                if typ==MAJOR:
                    permanentl.set_markup('<b>'+label+'</b>')
                elif typ==MINOR:
                    permanentl.set_markup('  '+label)
                elif typ==TINY:
                    permanentl.set_markup('  <span size="smaller">'+label+'</span>')
                if self.pressable:
                    b = gtk.Button(); b.add(permanentl)
                    b.set_relief(gtk.RELIEF_NONE)
                    b.connect('clicked',self.toggle_label,label,name,properties,unit)
                    hb.pack_start(b,expand=False)
                    self.toggles[name] = b
                else:
                    hb.pack_start(permanentl)
                unit_label = gtk.Label()
                unit_label.set_alignment(0,0.5)
                if name != 'kcal':
                    hb.pack_start(unit_label)
                else:
                    #print 'pack end'
                    #hb.pack_end(unit_label,expand=True)
                    table.attach(unit_label,1,2,n+start_at,n+start_at+1,xoptions=gtk.FILL)
                    unit_label.set_alignment(1,0.5)
                    unit_label.show()
                hb.show_all()
                table.attach(hb,0,1,n+start_at,n+start_at+1,xoptions=gtk.FILL)
                if show_percent==SHOW_PERCENT:
                    percent_label = gtk.Label()
                    percent_label.modify_font(self.bold_font)
                    percent_label.set_alignment(1,0.5)
                    percent_label.show()
                    table.attach(percent_label,1,2,n+start_at,n+start_at+1,xoptions=gtk.FILL)
                self.nutrition_display_info.append({
                    'props':properties,
                    'percent_label':(show_percent==SHOW_PERCENT
                                     and
                                     percent_label),
                    'unit_label': unit_label,
                    'unit':unit,
                    'usda_rec_per_cal':(RECOMMENDED_INTAKE.has_key(name) and
                                        RECOMMENDED_INTAKE[name]),
                    'box':hb,
                    'type':typ,
                    })

    def set_prefs (self, prefs):
        self.prefs = prefs

    def toggle_label (self, button, label, name,properties, unit):
        if self.__toggling__: return
        self.__toggling__ = True
        if name != self.active_name:
            for b in self.toggles.values():
                lab = b.get_children()[0]
                if b != button:
                    orig = lab.get_label()
                    if orig.find(self.active_button_markup[0])==0:
                        lab.set_label(orig[len(self.active_button_markup[0]):(- len(self.active_button_markup[1]))])
                else:
                    lab.set_label(self.active_button_markup[0]+lab.get_label()+self.active_button_markup[1])
            self.active_name = name
            self.active_unit = unit
            self.active_label = label
            self.active_properties = properties
        else:
            self.active_name = None
            self.active_unit = None
            self.active_label = None
            lab = button.get_children()[0]
            orig = lab.get_label()
            if orig.find(self.active_button_markup[0])==0:
                lab.set_label(orig[len(self.active_button_markup[0]):(- len(self.active_button_markup[1]))])
        self.emit('label-changed')
        self.__toggling__ = False

    def make_missing_label (self):
        hb = gtk.HBox()
        l=gtk.Label()
        self.missingLabelLabel = l
        l.set_alignment(0,0.5)
        b = gtk.Button(stock=gtk.STOCK_EDIT)
        hb.pack_start(l)
        hb.pack_start(b)
        b.connect('clicked',self.solidify_vapor_cb)
        b.show(),l.show(),hb.show()
        self.edit_missing_button = b
        return hb

    def set_missing_label_text (self,missing,total):
        self.missingLabelLabel.set_markup(
            '<span color="red" style="italic">' +\
            _('''Missing nutritional information\nfor %(missing)s of %(total)s ingredients.''')%locals()+\
            '</span>')
        if missing==0:
            self.missingLabelLabel.hide()
        else:
            self.missingLabelLabel.show()
        if missing==total: method = 'hide'
        else: method = 'show'
        getattr(self.main_table,method)()
        getattr(self.nutexpander,method)()
        getattr(self.yieldLabel,method)()
        getattr(self.cal_per_day_box,method)()

    def make_dv_boxes (self):
        dvLabel = gtk.Label()
        dvLabel.set_markup('<span weight="bold" size="small">' + \
                           _('% _Daily Value') + \
                           '</span>')
        dvLabel.set_use_underline(True)
        dvLabel.set_alignment(1,0.5)
        vb = gtk.VBox()
        hb = gtk.HBox()
        self.edit_button = gtk.ToggleButton()
        dvLabel.set_mnemonic_widget(self.edit_button)
        i = gtk.Image()
        i.set_from_stock(gtk.STOCK_EDIT,gtk.ICON_SIZE_MENU)
        self.edit_button.add(i)
        hb.pack_end(dvLabel,fill=False,expand=False)
        self.edit_button.set_alignment(1,0.5)
        hb.pack_end(self.edit_button,fill=False,expand=False,padding=6)
        self.edit_button.show_all()
        self.set_edit_tip()
        self.edit_button.connect('clicked',self.toggle_edit_calories_per_day)
        hb.show_all()
        self.cpd_editor = gtk.HBox()
        cpd_ed_label = gtk.Label('<i>_'+'Calories per day:' + '</i>')
        cpd_ed_label.set_use_underline(True)
        cpd_ed_label.set_use_markup(True)
        self.cpd_editor.pack_start(cpd_ed_label,padding=12)
        cpd_ed_label.set_alignment(1,0.5)
        self.cpd_sb = gtk.SpinButton()
        self.cpd_sb.set_numeric(True)
        self.cpd_sb.connect('activate',
                            lambda *args: self.edit_button.set_active(False))
        self.cpd_sb.connect('value-changed',self.edit_calories_per_day)
        cpd_ed_label.set_mnemonic_widget(self.cpd_sb)
        adj = self.cpd_sb.get_adjustment()
        adj.lower,adj.upper=0,4000
        adj.step_increment,adj.page_increment = 50,500
        self.cpd_editor.pack_start(self.cpd_sb)
        cancelb = gtk.Button(stock=gtk.STOCK_CANCEL)
        #okb = gtk.Button(stock=gtk.STOCK_OK)
        #self.cpd_editor.pack_start(cancelb,padding=12)
        #self.cpd_editor.pack_start(okb,)
        #okb.connect('clicked',self.edit_calories_per_day)
        #cancelb.connect('clicked',lambda *args: self.cpd_editor.hide())
        return hb,self.cpd_editor

    def set_edit_tip (self):
        self.tt.set_tip(
            self.edit_button,
            _("Percentage of recommended daily value based on %i calories per day. Click to edit number of calories per day.")%self.calories_per_day
            )

    def toggle_edit_calories_per_day (self, b):
        if b.get_active():
            self.cpd_sb.set_value(self.calories_per_day)
            self.cpd_editor.show_all()
            self.cpd_sb.grab_focus()
        else:
            self.edit_calories_per_day()
            self.cpd_editor.hide()

    def edit_calories_per_day (self, *args):
        self.cpd_sb.update()
        self.calories_per_day = self.cpd_sb.get_value()
        self.update_display()
        self.set_edit_tip()
        self.emit('calories-changed')

    def set_yields (self, n, unit='servings'):
        self.yields = n
        self.yield_unit = unit
        self.setup_yield_label()
        #self.update_display()

    def set_nutinfo (self, nutinfo):
        """Set nutrition info from a nutrition info object.

        A nutinfo object has attributes with our relevant data.
        """
        self.nutinfo = nutinfo
        if len(self.nutinfo)==0:
            self.main_table.hide()
            self.nutexpander.hide()
            self.yieldLabel.hide()
            self.cal_per_day_box.hide()
            self.missingLabel.hide()
        else:
            self.update_display()
            vapor = self.nutinfo._get_vapor()
            if vapor:
                len(vapor)
                self.nutinfo.recursive_length()
                self.set_missing_label_text(
                    len(vapor),
                    self.nutinfo.recursive_length()
                    )
                self.missingLabel.show()
            else:
                self.main_table.show()
                self.nutexpander.show()
                self.yieldLabel.show()
                self.cal_per_day_box.show()
                self.missingLabel.hide()

    def update_display (self):
        """Update the display of labels based on values in nutinfo,
        adjusted by yields and calories_per_day.
        """
        for itm in self.nutrition_display_info:
            props = itm['props']
            if type(props)==str:
                rawval = getattr(self.nutinfo,props) or 0
            else:
                # sum a list of properties
                rawval = sum([getattr(self.nutinfo,p) or 0 for p in props])
            if self.yields:
                rawval = float(rawval) / self.yields
            if itm['type'] != MAJOR:
                # If the item is not "MAJOR", then we hide it if the
                # rawval is 0
                if rawval == 0:
                    itm['box'].hide()
                    if itm['percent_label']: itm['percent_label'].hide()
                else:
                    itm['box'].show()
                    if itm['percent_label']: itm['percent_label'].show()
            if itm['unit_label']:
                itm['unit_label'].set_text('%i%s'%(rawval,itm['unit']))
            if itm['usda_rec_per_cal'] and itm['percent_label']:
                totrec = itm['usda_rec_per_cal']*self.calories_per_day
                if totrec:
                    percent = 100 * (float(rawval) / totrec)
                    itm['percent_label'].set_text("%i%%"%percent)

    def setup_yield_label (self):
        if self.custom_label:
            self.yieldLabel.set_markup('<b>'+self.custom_label+'</b>')
        elif self.yields:
            singular_unit = gourmet.defaults.get_pluralized_form(self.yield_unit,1)
            self.yieldLabel.set_markup('<b>'+_('Amount per %s'%singular_unit)+'</b>')
        else:
            self.yieldLabel.set_markup('<b>'+_('Amount per recipe')+'</b>')

    def set_nutritional_info (self, info):
        """Set nutrition from a NutritionInfo or NutritionInfoList object."""
        self.nutinfo = info
        self.update_display()

    def solidify_vapor_cb (self,*args):
        self.show_druid(fix_vapor=True)

    def show_druid (self, nd=None, fix_vapor=False):
        vapor = fix_vapor and self.nutinfo._get_vapor()
        if not nd:
            if vapor: nd=vapor[0].__nd__
            else:
                raise Exception("No nutritional database handed to us!")
        import nutritionDruid
        self.ndruid = nutritionDruid.NutritionInfoDruid(nd,
                                                        prefs=self.prefs,rec=self.rec)
        self.ndruid.connect('key-changed',lambda w,tpl: self.emit('ingredients-changed'))
        self.ndruid.connect('unit-changed',lambda w,tpl: self.emit('ingredients-changed'))
        if vapor:
            ings = [(v.__key__,[(v.__amt__,
                                 v.__unit__)]
                     ) for v in vapor]
            self.ndruid.add_ingredients(
                ings,
                )
        else:
            self.ndruid.setup_nutrition_index()
        self.ndruid.connect('finish',
                            self.update_nutinfo)
        self.ndruid.show()

    def update_nutinfo (self,*args):
        self.nutinfo._reset()
        self.update_display()
        vapor = self.nutinfo._get_vapor()
        if vapor:
            self.set_missing_label_text(len(vapor),len(self.nutinfo))
            self.missingLabel.show()
        else:
            self.missingLabel.hide()
        self.emit('ingredients-changed')

if __name__ == '__main__':
    import random
    class fakenut:

        __attdict__ = {}

        def __len__ (self): return 7

        def __getattr__ (self,n):
            if n=='has_vapor':
                return self.has_vapor
            if n=='_get_vapor':
                return self._get_vapor_
            if self.__attdict__.has_key(n):
                return self.__attdict__[n]
            elif n=='kcal':
                self.__attdict__[n]=self.carb*4+self.sugar*4+self.protein*4+self.famono*9+self.fasat*9
                return self.__attdict__[n]
            else:
                #n = random.randint(0,100)
                self.__attdict__[n]=random.randint(0,100)
                return self.__attdict__[n]

        def has_vapor (self): True

        def recursive_length (self): return self.__len__()

        def _get_vapor_ (self):
            return [('black pepper',[(1,'tsp.')]),
                    ('red pepper',[(1,''),
                                   (2,'c.')])]


    ni = fakenut()
    w = gtk.Window()
    nl = NutritionLabel({})
    vb=gtk.VBox()
    w.add(vb)
    hb = gtk.HBox()
    vb.pack_start(hb,expand=False,fill=False)
    hb.pack_start(nl,expand=False,fill=False)
    vb.show()
    b = gtk.Button('Test me')
    vb.add(b)
    nl.tt.set_tip(b,'What about this?')
    b.show()
    hb.show()
    #nl.set_yields(2)
    nl.set_nutinfo(ni)
    def display_info (w):
        print w.active_name,w.active_unit,w.active_label
    nl.connect('label-changed',display_info)
    nl.show()
    w.show()
    w.connect('delete-event',lambda *args: gtk.main_quit())
    gtk.main()


