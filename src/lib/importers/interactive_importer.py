"""A fallback interactive importer.

This is handed generic text. We then guide the user through the text
(they tell us what's an instruction, what's an ingredient, etc.)
"""

import gtk, gtk.glade, gtk.gdk, pango
import re, os.path
from gourmet import convert
from gourmet import gglobals
import importer

# Copied from """
# SimpleGladeApp.py
# Module that provides an object oriented abstraction to pygtk and libglade.
# Copyright (C) 2004 Sandino Flores Moreno
#
import tokenize
import weakref
import inspect

class SimpleGladeApp:

    def __init__(self, path, root=None, domain=None, **kwargs):
        """
        Load a glade file specified by glade_filename, using root as
        root widget and domain as the domain for translations.

        If it receives extra named arguments (argname=value), then they are used
        as attributes of the instance.

        path:
            path to a glade filename.
            If glade_filename cannot be found, then it will be searched in the
            same directory of the program (sys.argv[0])

        root:
            the name of the widget that is the root of the user interface,
            usually a window or dialog (a top level widget).
            If None or ommited, the full user interface is loaded.

        domain:
            A domain to use for loading translations.
            If None or ommited, no translation is loaded.

        **kwargs:
            a dictionary representing the named extra arguments.
            It is useful to set attributes of new instances, for example:
                glade_app = SimpleGladeApp("ui.glade", foo="some value", bar="another value")
            sets two attributes (foo and bar) to glade_app.
        """        
        if os.path.isfile(path):
            self.glade_path = path
        else:
            glade_dir = os.path.dirname( sys.argv[0] )
            self.glade_path = os.path.join(glade_dir, path)
        for key, value in kwargs.items():
            try:
                setattr(self, key, weakref.proxy(value) )
            except TypeError:
                setattr(self, key, value)
        self.glade = None
        self.install_custom_handler(self.custom_handler)
        self.glade = self.create_glade(self.glade_path, root, domain)
        if root:
            self.main_widget = self.get_widget(root)
        else:
            self.main_widget = None
        self.normalize_names()
        self.add_callbacks(self)
        self.new()

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.main_widget:
            root = gtk.Widget.get_name(self.main_widget)
            repr = '%s(path="%s", root="%s")' % (class_name, self.glade_path, root)
        else:
            repr = '%s(path="%s")' % (class_name, self.glade_path)
        return repr

    def new(self):
        """
        Method called when the user interface is loaded and ready to be used.
        At this moment, the widgets are loaded and can be refered as self.widget_name
        """
        pass

    def add_callbacks(self, callbacks_proxy):
        """
        It uses the methods of callbacks_proxy as callbacks.
        The callbacks are specified by using:
            Properties window -> Signals tab
            in glade-2 (or any other gui designer like gazpacho).

        Methods of classes inheriting from SimpleGladeApp are used as
        callbacks automatically.

        callbacks_proxy:
            an instance with methods as code of callbacks.
            It means it has methods like on_button1_clicked, on_entry1_activate, etc.
        """        
        self.glade.signal_autoconnect(callbacks_proxy)

    def normalize_names(self):
        """
        It is internally used to normalize the name of the widgets.
        It means a widget named foo:vbox-dialog in glade
        is refered self.vbox_dialog in the code.

        It also sets a data "prefixes" with the list of
        prefixes a widget has for each widget.
        """
        for widget in self.get_widgets():
            widget_name = gtk.Widget.get_name(widget)
            prefixes_name_l = widget_name.split(":")
            prefixes = prefixes_name_l[ : -1]
            widget_api_name = prefixes_name_l[-1]
            widget_api_name = "_".join( re.findall(tokenize.Name, widget_api_name) )
            gtk.Widget.set_name(widget, widget_api_name)
            if hasattr(self, widget_api_name):
                raise AttributeError("instance %s already has an attribute %s" % (self,widget_api_name))
            else:
                setattr(self, widget_api_name, widget)
                if prefixes:
                    gtk.Widget.set_data(widget, "prefixes", prefixes)

    def add_prefix_actions(self, prefix_actions_proxy):
        """
        By using a gui designer (glade-2, gazpacho, etc)
        widgets can have a prefix in theirs names
        like foo:entry1 or foo:label3
        It means entry1 and label3 has a prefix action named foo.

        Then, prefix_actions_proxy must have a method named prefix_foo which
        is called everytime a widget with prefix foo is found, using the found widget
        as argument.

        prefix_actions_proxy:
            An instance with methods as prefix actions.
            It means it has methods like prefix_foo, prefix_bar, etc.
        """        
        prefix_s = "prefix_"
        prefix_pos = len(prefix_s)

        is_method = lambda t : callable( t[1] )
        is_prefix_action = lambda t : t[0].startswith(prefix_s)
        drop_prefix = lambda (k,w): (k[prefix_pos:],w)

        members_t = inspect.getmembers(prefix_actions_proxy)
        methods_t = filter(is_method, members_t)
        prefix_actions_t = filter(is_prefix_action, methods_t)
        prefix_actions_d = dict( map(drop_prefix, prefix_actions_t) )

        for widget in self.get_widgets():
            prefixes = gtk.Widget.get_data(widget, "prefixes")
            if prefixes:
                for prefix in prefixes:
                    if prefix in prefix_actions_d:
                        prefix_action = prefix_actions_d[prefix]
                        prefix_action(widget)

    def custom_handler(self,
            glade, function_name, widget_name,
            str1, str2, int1, int2):
        """
        Generic handler for creating custom widgets, internally used to
        enable custom widgets (custom widgets of glade).

        The custom widgets have a creation function specified in design time.
        Those creation functions are always called with str1,str2,int1,int2 as
        arguments, that are values specified in design time.

        Methods of classes inheriting from SimpleGladeApp are used as
        creation functions automatically.

        If a custom widget has create_foo as creation function, then the
        method named create_foo is called with str1,str2,int1,int2 as arguments.
        """
        try:
            handler = getattr(self, function_name)
            return handler(str1, str2, int1, int2)
        except AttributeError:
            return None

    def gtk_widget_show(self, widget, *args):
        """
        Predefined callback.
        The widget is showed.
        Equivalent to widget.show()
        """
        widget.show()

    def gtk_widget_hide(self, widget, *args):
        """
        Predefined callback.
        The widget is hidden.
        Equivalent to widget.hide()
        """
        widget.hide()

    def gtk_widget_grab_focus(self, widget, *args):
        """
        Predefined callback.
        The widget grabs the focus.
        Equivalent to widget.grab_focus()
        """
        widget.grab_focus()

    def gtk_widget_destroy(self, widget, *args):
        """
        Predefined callback.
        The widget is destroyed.
        Equivalent to widget.destroy()
        """
        widget.destroy()

    def gtk_window_activate_default(self, window, *args):
        """
        Predefined callback.
        The default widget of the window is activated.
        Equivalent to window.activate_default()
        """
        widget.activate_default()

    def gtk_true(self, *args):
        """
        Predefined callback.
        Equivalent to return True in a callback.
        Useful for stopping propagation of signals.
        """
        return True

    def gtk_false(self, *args):
        """
        Predefined callback.
        Equivalent to return False in a callback.
        """
        return False

    def gtk_main_quit(self, *args):
        """
        Predefined callback.
        Equivalent to self.quit()
        """
        self.quit()

    def main(self):
        """
        Starts the main loop of processing events.
        The default implementation calls gtk.main()

        Useful for applications that needs a non gtk main loop.
        For example, applications based on gstreamer needs to override
        this method with gst.main()

        Do not directly call this method in your programs.
        Use the method run() instead.
        """
        gtk.main()

    def quit(self):
        """
        Quit processing events.
        The default implementation calls gtk.main_quit()
        
        Useful for applications that needs a non gtk main loop.
        For example, applications based on gstreamer needs to override
        this method with gst.main_quit()
        """
        gtk.main_quit()

    def run(self):
        """
        Starts the main loop of processing events checking for Control-C.

        The default implementation checks wheter a Control-C is pressed,
        then calls on_keyboard_interrupt().

        Use this method for starting programs.
        """
        try:
            self.main()
        except KeyboardInterrupt:
            self.on_keyboard_interrupt()

    def on_keyboard_interrupt(self):
        """
        This method is called by the default implementation of run()
        after a program is finished by pressing Control-C.
        """
        pass

    def install_custom_handler(self, custom_handler):
        gtk.glade.set_custom_handler(custom_handler)

    def create_glade(self, glade_path, root, domain):
        return gtk.glade.XML(self.glade_path, root, domain)

    def get_widget(self, widget_name):
        return self.glade.get_widget(widget_name)

    def get_widgets(self):
        return self.glade.get_widget_prefix("")        

# End copied material

class RecipeParser:

    LONG_LINE = 80
    SHORT_LINE = 40

    INGREDIENT = 'ING'
    INSTRUCTIONS = 'INSTRUCTIONS'
    ATTRIBUTE = 'ATT'
    TITLE = 'TIT'
    IGNORE = 'IGN'

    ing_matcher = re.compile("%s\s*\w+.*"%convert.NUMBER_REGEXP)
    attribute_matcher = re.compile('\s*\w+(\W+\w+)?:\s+\w+')

    def break_into_paras (self):
        self.long_lines = False
        for l in self.txt.split('\n'):
            if len(l)>self.LONG_LINE:
                self.long_lines = True
                break
        if self.long_lines:
            self.paras = self.txt.split('\n')
        else:
            # Try to deal with wrapped lines reasonably...
            self.paras = []
            start_new_para = True
            for l in self.txt.split('\n'):                
                if start_new_para or self.ing_matcher.match(l):
                    self.paras.append(l)
                    start_new_para = False
                else:
                    self.paras[-1] = self.paras[-1]+' '+l
                    start_new_para = (len(l) < self.SHORT_LINE)

    def parse (self, txt):
        self.txt = txt
        self.parsed = []
        self.break_into_paras()
        title_parsed = False
        for p in self.paras:
            if not title_parsed and p:
                self.parsed.append((p,self.TITLE))
                title_parsed = True
            elif not p.strip():
                self.parsed.append((p,self.IGNORE))
            elif self.ing_matcher.match(p.strip()):
                self.parsed.append((p,self.INGREDIENT))
            elif self.attribute_matcher.match(p.strip()):
                self.parsed.append((p,self.ATTRIBUTE))
            else:
                self.parsed.append((p,self.INSTRUCTIONS))
        return self.parsed

# Material copied from our generic recipe importer...

class InteractiveImporter (SimpleGladeApp, importer.importer):

    def __init__(self, rd):
        self.parser = RecipeParser()
        self.parser_to_choice = {
            self.parser.INGREDIENT:'Ingredient',
            self.parser.INSTRUCTIONS:'Instructions',
            self.parser.IGNORE:'Ignore',
            self.parser.TITLE:'Title',
            self.parser.ATTRIBUTE:'Attribute',
            }
        self.added_to = False
        SimpleGladeApp.__init__(self,
                                path=os.path.join(gglobals.gladebase,
                                                  "generic_importer.glade"),
                                root="window1",
                                domain="gourmet")

    #-- InteractiveImporter.new {
    def new(self):
        print "A new %s has been created" % self.__class__.__name__
        self.get_widget('window1').show_all()
        self.get_widget('window1').connect('delete-event',lambda *args: gtk.main_quit())
        self.textview = self.glade.get_widget('textview')
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.connect('mark-set',self.on_cursor_moved)
        self.display = RecipeDisplay(self.glade)
        self.glade.get_widget('window1').show()
        self.populate_action_box()
    #-- InteractiveImporter.new }

    #-- InteractiveImporter custom methods {
    #   Write your own methods here
    def populate_action_box (self):
        """Set up our choices of actions."""
        self.action_box = self.glade.get_widget('treeview1')
        self.actions = {
            'Instructions':self.display.add_instructions,
            'Notes':self.display.add_notes,
            'Ingredient':self.display.add_ing_from_text,
            'Ingredients': self.display.add_ings_from_text,
            'Ingredient Supgroup':self.display.add_ing_group,
            #'Ignore':lambda *args: None,
            #'Attribute':lambda txt: \
            #self.display.add_attribute(*[t.strip() for t in txt.split(':')]),
            'Servings':lambda txt: self.display.add_attribute('servings',txt),
            'Cooking Time:':lambda txt: self.display.add_attribute('cooktime',txt),
            'Preparation Time:':lambda txt: self.display.add_attribute('preptime',txt),
            'Cuisine':lambda txt: self.display.add_attribute('cuisine',txt),
            'Category':lambda txt: self.display.add_attribute('category',txt),                        
            'Title':lambda txt: self.display.add_attribute('title',txt),
            }
        
        keys = self.actions.keys()
        keys.sort()
        # set up model
        mod = gtk.ListStore(str)
        for k in keys: mod.append([k])
        # set up treeview column...
        renderer = gtk.CellRendererText()
        tvc = gtk.TreeViewColumn('',renderer,text=0)
        self.action_box.append_column(tvc)
        self.action_box.set_model(mod)

    def get_current_action (self, *args):
        """Get the current default actions for our section of text."""
        mod,itr = self.action_box.get_selection().get_selected()
        return mod.get_value(itr,0)

    def set_current_action (self, action):
        """Set the current default action for our section of text."""
        mod = self.action_box.get_model()
        sel = self.action_box.get_selection()
        for r in mod:
            if r[0]==action:
                sel.select_iter(r.iter)
                return
        print action,'not found!'
        # if we haven't returned by now, we have no action
        sel.unselect_all()
        
    def set_text (self, txt):
        """Set raw text."""
        self.textbuffer = gtk.TextBuffer()
        self.textview.set_buffer(self.textbuffer)
        parsed = self.parser.parse(txt)
        tagtable = self.textbuffer.get_tag_table()
        # a list of marks...
        self.sections = []
        self.section_pos = 0
        for line,tag in parsed:
            if not tagtable.lookup(tag):
                tagtable.add(gtk.TextTag(tag))
            if tag==self.parser.IGNORE:
                self.textbuffer.insert(self.textbuffer.get_end_iter(),
                                       line+'\n')
            else:
                smark = self.textbuffer.create_mark(None,
                                                    self.textbuffer.get_end_iter(),
                                                    True)
                self.textbuffer.insert_with_tags_by_name(
                    self.textbuffer.get_end_iter(),
                    line+'\n',
                    tag
                    )
                emark = self.textbuffer.create_mark(None,
                                                    self.textbuffer.get_end_iter(),
                                                    True)
                self.sections.append((smark,emark))
        self.goto_section(0)

    def goto_next_section (self):
        """Goto our next section"""
        self.goto_section(self.get_current_mark_pos()+1)
        
    def goto_prev_section (self):
        """Goto our previous section"""
        self.goto_section(self.get_current_mark_pos()-1)

    def get_current_mark_pos (self):
        """Get the current position of our cursor relative to our marks"""
        itr = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert())
        cur_offset = itr.get_offset()
        #print 'current offset is ',cur_offset
        for n,mks in enumerate(self.sections):
            start = self.textbuffer.get_iter_at_mark(mks[0])
            end = self.textbuffer.get_iter_at_mark(mks[1])
            #print cur_offset, '<=',end.get_offset(),'?'
            if start.get_offset() <= cur_offset < end.get_offset():
                #print 'current mark=',n
                return n
            elif cur_offset < start.get_offset():
                return n - 1
        else:
            return len(self.sections)+1

    def goto_section (self, n):
        if n >= len(self.sections): n = len(self.sections)-1
        elif n < 0: n = 0
        self.curmark = n
        s,e=self.sections[n]
        start_itr=self.textbuffer.get_iter_at_mark(s)
        self.textbuffer.select_range(start_itr,
                                     self.textbuffer.get_iter_at_mark(e)
                                     )
        self.textview.scroll_to_iter(start_itr,0.3)
        self.on_cursor_moved(self.textview)
        
            
    #-- InteractiveImporter custom methods }

    #-- InteractiveImporter.on_open {
    def on_open(self, widget, *args):
        #print "on_open called with self.%s" % widget.get_name()
        #fsd = gtk.FileChooserDialog(buttons=(gtk.STOCK_CANCEL,
        #                                     gtk.RESPONSE_CANCEL,
        #                                     gtk.STOCK_OK,
        #                                     gtk.RESPONSE_OK))
        #response = fsd.run()
        #fsd.hide()
        #if response==gtk.RESPONSE_OK:
        #    # Warning, we don't check to make sure the filesize is
        #    # reasonable...
        fname = dialog_extras.select_file('Open recipe',
                                         filters=[['Plain Text',['text/plain'],'*.txt']])
        if fname:
            ofi = file(fname,'r')
            self.set_text(ofi.read())
            ofi.close()            
    #-- InteractiveImporter.on_open }

    #-- InteractiveImporter.on_open_url {
    def on_open_url(self, widget, *args):
        print "on_open_url called with self.%s" % widget.get_name()
        # A quick hack to try web import... eventually we'll want to
        # use urllib to do something crossplatform and reasonable if
        # we want this (and of course we can just borrow code from
        # Gourmet which already does this right)
        url = dialog_extras.getEntry(label='Enter address of webpage with a recipe on it.',
                                     entryLabel='URL:',
                                     entryTip="""URLs start with http://""")
        if url.find('//')<0: url = 'http://'+url
        ifi = os.popen('w3m -T text/html -dump %(url)s'%locals())
        self.set_text(ifi.read())
    #-- InteractiveImporter.on_open_url }

    #-- InteractiveImporter.on_save {
    def on_save(self, widget, *args):
        print "on_save called with self.%s" % widget.get_name()
        import eatdrinkfeelgood
        ofi = sys.stdout
        writer = eatdrinkfeelgood.RecipeWriter(ofi)
        print 'Writing'
        writer(self.display)
        writer.finish()
    #-- InteractiveImporter.on_save }

    #-- InteractiveImporter.on_quit {
    def on_quit(self, widget, *args):
        print "on_quit called with self.%s" % widget.get_name()
        self.glade.get_widget('window1').hide()
        gtk.main_quit()
    #-- InteractiveImporter.on_quit }

    def set_added_to (self, bool):
        """Set a switch that we have been added to, or not."""
        self.added_to = bool
        if bool: self.glade.get_widget('NewRecipeButton').set_sensitive(bool)

    def on_new_recipe (self, *args):
        # If we already have a recipe
        if self.added_to:
            self.commit_rec()
        self.start_rec()
        self.set_added_to(False)

    def on_add_attribute (self, attname, attval):
        self.rec[attname]=attval

    #-- InteractiveImporter.on_cursor_moved {
    def on_cursor_moved (self, widget, *args):
        print 'cursor moved!'
        cursor = self.textbuffer.get_insert()
        itr = self.textbuffer.get_iter_at_mark(cursor)
        tags = itr.get_tags()
        action = None
        for t in tags:
            if self.parser_to_choice.has_key(t.props.name):
                action = self.parser_to_choice[t.props.name]
        print 'setting action->',action
        self.set_current_action(action)
        
    #-- InteractiveImporter.on_cursor_moved }

    #-- InteractiveImporter.on_ingredientEventBox_drag_drop {
    def on_ingredientEventBox_drag_drop(self, widget, *args):
        print "on_ingredientEventBox_drag_drop called with self.%s" % widget.get_name()
    #-- InteractiveImporter.on_ingredientEventBox_drag_drop }

    #-- InteractiveImporter.on_back {
    def on_back(self, widget, *args):
        print "on_back called with self.%s" % widget.get_name()
        self.goto_prev_section()
    #-- InteractiveImporter.on_back }

    #-- InteractiveImporter.on_forward {
    def on_forward(self, widget, *args):
        self.goto_next_section()
    #-- InteractiveImporter.on_forward }

    #-- InteractiveImporter.on_apply {
    def on_apply(self, widget, *args):
        selection = self.textbuffer.get_text(
            *self.textbuffer.get_selection_bounds()
            )
        active_txt = self.get_current_action()
        print 'Action:',active_txt
        print 'Selection:',selection
        if not hasattr(self,'inserted_tag'):
            self.inserted_tag = gtk.TextTag('inserted')
            self.inserted_tag.set_property('editable',False)
            self.inserted_tag.set_property('style',pango.STYLE_ITALIC)
        if not self.textbuffer.get_tag_table().lookup('inserted'):
            self.textbuffer.get_tag_table().add(self.inserted_tag)
        self.textbuffer.apply_tag(self.inserted_tag,*self.textbuffer.get_selection_bounds())
        if not hasattr(self,'markup_tag'):
            self.markup_tag = gtk.TextTag('markup')
            self.markup_tag.set_property('editable',False)
            self.markup_tag.set_property('scale',pango.SCALE_SMALL)
            self.markup_tag.set_property('rise',15)
            self.markup_tag.set_property('foreground',
                                         '#f00'
                                         )
        if not self.textbuffer.get_tag_table().lookup('markup'):
            self.textbuffer.get_tag_table().add(self.markup_tag)
        st,end = self.textbuffer.get_selection_bounds()
        self.textbuffer.insert_with_tags(st,'['+active_txt+':',self.markup_tag)
        st,end = self.textbuffer.get_selection_bounds()
        self.textbuffer.insert_with_tags(end,']',self.markup_tag)
        # We'll do something real soon...
        #self.resultbuffer.insert(
        #    self.resultbuffer.get_end_iter(),
        #    "%s: %s\n"%(active_txt,selection)
        #    )
        action = self.actions[active_txt]
        print 'Calling ',action
        action(selection)
        self.on_forward(None)
    #-- InteractiveImporter.on_apply }

class RecipeDisplay:
    def __init__ (self, glade):
        self.parent_glade = glade
        #self.rc_glade = ...

    def add_instructions (self, txt):
        print 'instr:',txt

    def add_notes (self, txt):
        print 'instr:',txt

    def add_ing_group (self, txt):
        print 'group:',txt

    def add_ing_from_text (self, txt):
        print 'ing:',txt

    def add_ings_from_text (self, txt):
        print 'ings:',txt

    def add_attribute (self, n, v):
        print n,':',v

def main():
    window1 = InteractiveImporter('foo')
    window1.set_text(
        """
Quick Pesto Dinner

Category: Quick, Easy, Summer
Yield: 2 Servings

Ingredients:
1-2 c. fresh basil
1/4-1/2 c. olive oil
1/4-1/2 c. pine nuts or walnuts
1/4 c. parmesan cheese
A handful of cheese
Some sausages
3-6 cloves garlic
1/2 lb. whole-wheat spaghetti
1-2 fresh tomatoes

In a food processor, mix together the basil, oil and nuts and garlic, altering as you like to make the pesto nuttier, more garlicky, or more oily.

Meanwhile, boil a large pot of water and cook spaghetti.

Chop up tomatoes roughly.

Toss spaghetti in pesto and tomatoes.
""")
    window1.run()        

if __name__ == '__main__':
    main()
