import gtk, pango
from gettext import gettext as _

class NutritionLabel (gtk.Table):
    """Provide a nutritional label that looks like standard FDA
    labels."""

    bold_font = pango.FontDescription()
    bold_font.set_weight(pango.WEIGHT_BOLD)
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
               (_('Cholesterol'),MAJOR,'chol',
                'cholestrl',DONT_SHOW_PERCENT,'g'),
               (_('Sodium'),MAJOR,'sodium',
                'sodium',DONT_SHOW_PERCENT,'mg'),
               (_('Total Carbohydrate'),MAJOR,'carb',
                'carb',SHOW_PERCENT,'g'),
               (_('Dietary Fiber'),MINOR,
                'fiber','fiber',SHOW_PERCENT,'g'),
               (_('Sugars'),MINOR,'sugar',
                'sugar',DONT_SHOW_PERCENT,'g'),
               (_('Protein'),MAJOR,'protein',
                'protein',SHOW_PERCENT,'g'),]

    recommended_intake = {
        'fat':0.30 / 9, # 30% of calories * 9 cal / g.
        'satfat':0.10 / 9, #10% of calories * 9 cal /g.
        'carb':0.6 / 4, #60% of calories * 4 cal / g.
        'protein':0.10 / 4, #10% of calories * 4 cal/g.
        'fiber':11.5/1000, #11.5 grams / 1000calories
        }

    calories_per_day = 2000

    def __init__ (self, *args):
        start_at = 4
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
        l.set_markup(
            '<span color="red" style="italic">' +\
            _('Missing nutritional information for some ingredients.')+\
            '</span>')
        l.set_alignment(0,0.5)
        b = gtk.Button(stock=gtk.STOCK_EDIT)
        hb.pack_start(l)
        hb.pack_start(b)
        b.connect('clicked',self.solidify_vapor_cb)
        b.show(),l.show(),hb.show()
        return hb

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
        self.tt.set_tip(self.edit_button,_("Percentage of recommended daily value based on %i calories per day. Click to edit number of calories per day.")%self.calories_per_day)

    def toggle_edit_calories_per_day (self, b):        
        if b.get_active():
            self.cpd_sb.set_value(self.calories_per_day)
            self.cpd_editor.show_all()
            self.cpd_sb.grab_focus()
        else:
            self.edit_calories_per_day()
            self.cpd_editor.hide()

    #def finish_edit_calories_per_day (self, *args):
    #    self.edit_calories_per_day()
    #    self.cpd_editor.hide()
        
    def edit_calories_per_day (self, *args):
        self.cpd_sb.update()
        self.calories_per_day = self.cpd_sb.get_value()        
        self.update_display()
        self.set_edit_tip()

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
        if self.nutinfo._get_vapor():
            self.missingLabel.show()
        else:
            self.missingLabel.hide()

    def update_display (self):
        """Update the display of labels based on values in nutinfo,
        adjusted by servings and calories_per_day.
        """
        for itm in self.nutrition_display_info:
            props = itm['props']
            print 'rawval - ',itm['props']
            if type(props)==str:
                print 'grab single prop'
                rawval = getattr(self.nutinfo,props) or 0
            else:
                # sum a list of properties
                print 'sum a list'
                rawval = sum([getattr(self.nutinfo,p) or 0 for p in props])
            if self.servings:
                print 'dividing ',rawval,'by',self.servings,
                rawval = float(rawval) / self.servings
                print '->',rawval
            else:
                print 'no serving info :('
            print 'rawval = ',rawval
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
            print 'druidify ',ings
            self.ndruid.add_ingredients(
                ings
                )
            self.ndruid.connect('finish',
                                self.update_nutinfo)
        
    def update_nutinfo (self,*args):
        self.nutinfo._reset()
        self.update_display()
        if self.nutinfo._get_vapor():
            self.missingLabel.show()
        else:
            self.missingLabel.hide()


if __name__ == '__main__':
    class fakenut:
        pass
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
    
    
