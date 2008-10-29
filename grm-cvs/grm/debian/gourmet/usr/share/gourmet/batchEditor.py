import os
import gtk, gtk.glade
import gglobals
import ratingWidget, timeEntry, cb_extras

class BatchEditor:

    def __init__ (self, rg):
        self.rg = rg
        self.setup_glade()

    def setup_glade (self):
        self.makeTimeEntry = lambda *args: timeEntry.makeTimeEntry()
        self.makeStarButton = lambda *args: ratingWidget.make_star_button(self.rg.star_generator)
        def custom_handler (glade,func_name,
                            widg, s1,s2,i1,i2):
            f=getattr(self,func_name)
            w= f(s1,s2,i1,i2)
            return w
        gtk.glade.set_custom_handler(custom_handler)        
        self.glade = gtk.glade.XML(os.path.join(gglobals.gladebase,'batchEditor.glade'))
        self.dialog = self.glade.get_widget('batchEditorDialog')
        self.setFieldWhereBlankButton = self.glade.get_widget('setFieldWhereBlankButton')
        self.setup_boxes()
        self.dialog.connect('response',self.response_cb)
        
    def setup_boxes (self):
        self.attribute_widgets = {}
        self.get_data_methods = {}
        for a,l,w in gglobals.REC_ATTRS:
            checkbutton = self.glade.get_widget('%sCheckButton'%a)
            if checkbutton:
                setattr(self,'%sCheckButton'%a,checkbutton)
                box = self.glade.get_widget('%sBox'%a)
                self.attribute_widgets[a] = box
                setattr(self,'%sBox'%a,box)
                checkbutton.connect('toggled',self.toggle_cb,a)
                box.set_sensitive(False)
                if w=='Combo':
                    # If this is a combo box, we'll get info via the child's get_text method...
                    self.get_data_methods[a] = (checkbutton,
                                                getattr(self,'%sBox'%a).get_children()[0].get_text)
                    
                    box.set_model(self.rg.getAttributeModel(a))
                    box.set_text_column(0)
                    cb_extras.setup_completion(box)
                elif w=='Entry':
                    if hasattr(box,'get_value'):
                        method = box.get_value
                    else:
                        method = box.get_text
                    self.get_data_methods[a] = (checkbutton,
                                                method)

    def set_values_from_recipe (self, recipe):
        for attribute,box in self.attribute_widgets.items():
            if hasattr(recipe,attribute):
                val = getattr(recipe,attribute)
            elif attribute == 'category':
                val = ', '.join(self.rg.rd.get_cats(recipe))
            if val:
                if hasattr(box,'set_value'):
                    box.set_value(val)
                elif hasattr(box,'set_text'):
                    box.set_text(val)
                elif hasattr(box.get_children()[0],'set_text'):
                    box.get_children()[0].set_text(val)
                else:
                    print "Can't figure out how to set value for ",attribute,box

    def toggle_cb (self, widg, attr):
        box = self.attribute_widgets[attr]
        if widg.get_active(): box.set_sensitive(True)
        else: box.set_sensitive(False)
        
    def get_values (self):
        changed = {}
        for attribute in self.get_data_methods.keys():
            cb,get_method = self.get_data_methods[attribute]
            if cb.get_active():
                val = get_method()
                changed[attribute]=val
        return changed
    
    def response_cb (self, dialog, resp):
        if resp == gtk.RESPONSE_OK:
            self.setFieldWhereBlank = self.setFieldWhereBlankButton.get_active()
            self.values =  self.get_values()
        else:
            self.setFieldWhereBlank = None
            self.values = None
        

if __name__ == '__main__':
    import GourmetRecipeManager
    rg = GourmetRecipeManager.RecGui()
    be=BatchEditor(rg)
    be.set_values_from_recipe(rg.rd.fetch_one(rg.rd.rview))
    be.dialog.run()
