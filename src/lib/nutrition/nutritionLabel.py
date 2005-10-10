import gtk, pango, gobject
from gettext import gettext as _

class NutritionLabel (gtk.Table, gobject.GObject):
    """Provide a nutritional label that looks like standard FDA
    labels."""

    bold_font = pango.FontDescription()
    bold_font.set_weight(pango.WEIGHT_BOLD)
    tiny_font = pango.FontDescription()
    tiny_font.set_size(pango.SCALE*9)
    background = gtk.gdk.Color(255,0,0)
    foreground = gtk.gdk.Color(255,255,255)
    
    MAJOR = 0
    MINOR = 1
    TINY = 2
    SEP = 3
    SHOW_PERCENT = True
    DONT_SHOW_PERCENT = False
    nutdata = [(_('Calories'),MAJOR,'calorie',
                'kcal',DONT_SHOW_PERCENT,''),
               SEP,
               (_('Total Fat'),MAJOR,'fat',
                ['fasat','famono','fapoly'],SHOW_PERCENT,'g'),
               (_('Saturated Fat'),MINOR,'satfat',
                'fasat',SHOW_PERCENT,'g'),
               (_('Cholesterol'),MAJOR,'cholestrl',
                'cholestrl',SHOW_PERCENT,'g'),
               (_('Sodium'),MAJOR,'sodium',
                'sodium',SHOW_PERCENT,'mg'),
               (_('Total Carbohydrate'),MAJOR,'carb',
                'carb',SHOW_PERCENT,'g'),
               (_('Dietary Fiber'),MINOR,
                'fiber','fiber',SHOW_PERCENT,'g'),
               (_('Sugars'),MINOR,'sugar',
                'sugar',SHOW_PERCENT,'g'),
               (_('Protein'),MAJOR,'protein',
                'protein',SHOW_PERCENT,'g'),
               SEP,
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
                'vitarae',SHOW_PERCENT,'mg'),
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

    recommended_intake = {
        'fat':0.30 / 9, # 30% of calories * 9 cal / g.
        'satfat':0.10 / 9, #10% of calories * 9 cal /g.
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

    calories_per_day = 2000

    __gsignals__ = {
        'calories-changed':(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE,()),
        'ingredients-changed':(gobject.SIGNAL_RUN_LAST,gobject.TYPE_NONE,())
        }    

    def __init__ (self, *args):
        start_at = 4
        gobject.GObject.__init__(self)
        gtk.Table.__init__(self,2,len(self.nutdata)+start_at)
        self.show()
        self.tt = gtk.Tooltips()
        self.servingLabel = gtk.Label()
        self.set_servings(0)
        self.nutrition_display_info = []
        self.attach(self.servingLabel,
                    0,2,0,1)
        self.servingLabel.show()
        self.servingLabel.set_alignment(0,0.5)
        self.missingLabel = self.make_missing_label()
        self.attach(self.missingLabel,0,2,1,2)
        # setup daily value button to display calories/day assumption
        # and to allow changing it via a nifty little button
        dvb,eb = self.make_dv_boxes()
        dvb.show()
        self.attach(dvb,1,2,2,3)
        self.attach(eb,0,2,3,4,ypadding=12)
        self.tt.enable()
        for n,nutstuff in enumerate(self.nutdata):
            if nutstuff == self.SEP:
                hs = gtk.HSeparator()
                self.attach(hs,0,2,n+start_at,n+start_at+1,xoptions=gtk.FILL)
                hs.show()
                continue
            label,typ,name,properties,show_percent,unit = nutstuff
            hb = gtk.HBox()
            permanentl = gtk.Label()
            permanentl.set_alignment(0,0.5)
            if typ==self.MAJOR:
                permanentl.set_markup('<b>'+label+'</b>')
            elif typ==self.MINOR:
                permanentl.set_markup('  '+label)
            elif typ==self.TINY:
                permanentl.set_markup('  <span size="smaller">'+label+'</span>')
            hb.pack_start(permanentl)
            unit_label = gtk.Label()
            unit_label.set_alignment(0,0.5)
            hb.pack_start(unit_label)
            hb.show_all()
            self.attach(hb,0,1,n+start_at,n+start_at+1,xoptions=gtk.FILL)
            if show_percent==self.SHOW_PERCENT:
                percent_label = gtk.Label()
                percent_label.modify_font(self.bold_font)
                percent_label.set_alignment(1,0.5)
                percent_label.show()
                self.attach(percent_label,1,2,n+start_at,n+start_at+1,xoptions=gtk.FILL)
            self.nutrition_display_info.append({
                'props':properties,
                'percent_label':(show_percent==self.SHOW_PERCENT
                                 and
                                 percent_label),
                'unit_label': unit_label,
                'unit':unit,
                'usda_rec_per_cal':(self.recommended_intake.has_key(name) and
                                    self.recommended_intake[name])
                })

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
        return hb

    def set_missing_label_text (self,missing,total):
        self.missingLabelLabel.set_markup(
            '<span color="red" style="italic">' +\
            _('Missing nutritional information for %(missing)s of %(total)s ingredients.')%locals()+\
            '</span>')

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

    def set_servings (self, n):
        self.servings = n
        self.setup_serving_label()
        #self.update_display()

    def set_nutinfo (self, nutinfo):
        """Set nutrition info from a nutrition info object.

        A nutinfo object has attributes with our relevant data.
        """
        self.nutinfo = nutinfo
        self.update_display()
        vapor = self.nutinfo._get_vapor()
        if vapor:
            self.set_missing_label_text(len(vapor),len(self.nutinfo))
            self.missingLabel.show()
        else:
            self.missingLabel.hide()

    def update_display (self):
        """Update the display of labels based on values in nutinfo,
        adjusted by servings and calories_per_day.
        """
        for itm in self.nutrition_display_info:
            props = itm['props']
            if type(props)==str:
                rawval = getattr(self.nutinfo,props) or 0
            else:
                # sum a list of properties
                rawval = sum([getattr(self.nutinfo,p) or 0 for p in props])
            if self.servings:
                rawval = float(rawval) / self.servings
            if itm['unit_label']:
                itm['unit_label'].set_text('%i%s'%(rawval,itm['unit']))
            if itm['usda_rec_per_cal'] and itm['percent_label']:
                totrec = itm['usda_rec_per_cal']*self.calories_per_day
                percent = 100 * (float(rawval) / totrec)
                itm['percent_label'].set_text("%i%%"%percent)

    def setup_serving_label (self):
        if self.servings:
            self.servingLabel.set_markup('<b>'+_('Amount per Serving')+'</b>')
        else:
            self.servingLabel.set_markup('<b>'+_('Amount per recipe')+'</b>')
        
    def set_nutritional_info (self, info):
        """Set nutrition from a NutritionInfo or NutritionInfoList object."""
        self.nutinfo = info
        self.update_display()
        
    def solidify_vapor_cb (self,*args):
        vapor = self.nutinfo._get_vapor()
        import nutritionDruid
        if vapor:
            self.ndruid = nutritionDruid.NutritionInfoDruid(vapor[0].__nd__)
            ings = [(v.__key__,[(v.__amt__,
                                 v.__unit__)]
                     ) for v in vapor]
            self.ndruid.add_ingredients(
                ings
                )
            self.ndruid.connect('finish',
                                self.update_nutinfo)
        
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

if gtk.pygtk_version[1]<8:
    gobject.type_register(NutritionLabel)


if __name__ == '__main__':
    class fakenut:

        def __len__ (self): return 2
    
    ni = fakenut()
    ni.fasat = 2
    ni.cholestrl = 10
    ni.famono = 23
    ni.fapoly = 6
    ni.protein = 3
    ni.carb = 12
    ni.fiber = 1.5
    ni.sugar = 43
    ni.kcal = ni.carb*4+ni.sugar*4+ni.protein*4+ni.famono*9+ni.fasat*9
    ni.sodium = 120
    ni.has_vapor = lambda *args: True
    ni._get_vapor  = lambda *args: [('black pepper',[(1,'tsp.')]),
                                    ('red pepper',[(1,''),
                                                   (2,'c.')])]
    w = gtk.Window()
    nl = NutritionLabel()
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
    #nl.set_servings(2)
    nl.set_nutinfo(ni)
    nl.show()
    w.show()
    w.connect('delete-event',lambda *args: gtk.main_quit())
    gtk.main()
    
    
