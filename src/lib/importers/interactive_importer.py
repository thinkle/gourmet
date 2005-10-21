"""A fallback interactive importer.

This is handed generic text. We then guide the user through the text
(they tell us what's an instruction, what's an ingredient, etc.)
"""

import gtk, gtk.glade, gtk.gdk, pango
import re, os.path
from gourmet import convert
from gourmet import gglobals
import importer
from generic_recipe_parser import RecipeParser
import imageBrowser
from gettext import gettext as _

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

class ConvenientImporter (importer.importer):
    """Add some convenience methods to our standard importer.
    """
    started=False

    def autostart_rec (f):
        """A decorator to make sure our recipe has been started before
        we add something to it.
        """
        def _ (self,*args,**kwargs):
            self.set_added_to(True)
            return f(self,*args,**kwargs)
        return _

    @autostart_rec
    def add_attribute (self, attname, txt):
        txt=txt.strip()
        if self.rec.has_key(attname):
            self.rec[attname] = self.rec[attname] + ', ' + txt
        else:
            self.rec[attname] = txt

    @autostart_rec
    def add_text (self, attname, txt):
        if self.rec.has_key(attname):
            self.rec[attname] = self.rec[attname] + '\n' + txt
        else:
            self.rec[attname] = txt

    @autostart_rec
    def add_ing_group (self, txt):
        self.group = txt.strip()

    @autostart_rec
    def add_ing_from_text (self, txt):
        txt=txt.strip()
        txt = re.sub('\s+',' ',txt)
        if not txt: return        
        mm = convert.ING_MATCHER.match(txt)
        if mm:
            groups = mm.groups()
            amount = groups[convert.ING_MATCHER_AMT_GROUP]
            unit = groups[convert.ING_MATCHER_UNIT_GROUP]
            item = groups[convert.ING_MATCHER_ITEM_GROUP]
            # If our unit isn't familiar, don't add it as a unit!
            if unit and not self.conv.unit_dict.has_key(unit.strip()):
                unit = ''
                item = unit + item
        else:
            print 'Unable to parse ingredient from text "%s"'%txt
            print 'Setting amount and unit to None'
            amount = None; unit = None;
            item = txt
        self.start_ing()
        if amount: self.add_amt(amount)
        if unit: self.add_unit(unit)
        if item: self.add_item(item)
        self.commit_ing()

    def add_ings_from_text (self, txt, break_at='\n'):
        """Add list of ingredients from block of text.

        By default, there is one ingredient per line of text."""
        txt=txt.strip()
        for i in txt.split(break_at): self.add_ing_from_text(i)


# Material copied from our generic recipe importer...

class InteractiveImporter (SimpleGladeApp, ConvenientImporter):

    def __init__(self, rd, progress=None,
                 custom_parser=None):
        self.progress = progress
        if custom_parser: self.parser = custom_parser
        else: self.parser = RecipeParser()
        self.parser_to_choice = {
            'ingredient':'Ingredient',
            'ingredients':'Ingredients',
            #'instructions':'Instructions',
            'None':'Ignore',
            #'title':'Title',
            }
        self.added_to = False
        self.attdic = gglobals.REC_ATTR_DIC 
        self.textattdic = gglobals.TEXT_ATTR_DIC
        SimpleGladeApp.__init__(self,
                                path=os.path.join(gglobals.gladebase,
                                                  "generic_importer.glade"),
                                root="window1",
                                domain="gourmet")
        ConvenientImporter.__init__(self,rd,threaded=True)

    #-- InteractiveImporter.new {
    def new(self):
        print "A new %s has been created" % self.__class__.__name__
        self.get_widget('window1').show_all()
        self.get_widget('window1').connect('delete-event',lambda *args: gtk.main_quit())
        self.textview = self.glade.get_widget('textview')
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.connect('mark-set',self.on_cursor_moved)
        #self.display = RecipeDisplay(self.glade)
        self.glade.get_widget('window1').show()
        self.populate_action_box()
    #-- InteractiveImporter.new }

    #-- InteractiveImporter custom methods {
    #   Write your own methods here
    def populate_action_box (self):
        """Set up our choices of actions."""
        self.action_box = self.glade.get_widget('treeview1')
        self.action_to_label = {}
        self.actions = {
            #'Instructions':self.display.add_instructions,
            #'Notes':self.display.add_notes,
            'Ingredient':lambda lab,txt: self.add_ing_from_text(txt),
            'Ingredients': lambda lab,txt: self.add_ings_from_text(txt),
            'Ingredient Subgroup':lambda lab,txt: self.add_ing_group(txt),
            }
        for attname,display_name in self.attdic.items():
            self.actions[display_name] = self.add_attribute
            self.action_to_label[display_name]=attname
        for attname,display_name in self.textattdic.items():
            self.actions[display_name] = self.add_text
            self.action_to_label[display_name]=attname
        keys = [self.attdic[a] for a in gglobals.DEFAULT_ATTR_ORDER]
        keys.extend(['Ingredient Subgroup','Ingredient','Ingredients' ])
        keys.extend([self.textattdic[a] for a in gglobals.DEFAULT_TEXT_ATTR_ORDER])
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
        sel = self.action_box.get_selection().get_selected()
        if sel:
            mod,itr = sel
            return mod.get_value(itr,0)
        else:
            return None

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

    def set_images (self, image_urls):
        self.images = image_urls

    def commit_rec (self, *args, **kwargs):
        if hasattr(self,'images'):
            if self.progress: self.progress(-1,_('Getting images...'))
            self.ibd=imageBrowser.ImageBrowserDialog(
                title=_("Select recipe image"),
                label=_("Select recipe image."),
                sublabel=_("Below are all the images found for the page you are importing. Select any images that are of the recipe, or don't select anything if you don't want any of these images."),
                )
            for i in self.images: self.ibd.add_image_from_uri(i)
            self.ibd.run()
            image = self.ibd.ret
            if image:
                fi=file(imageBrowser.get_image_file(image),'r')
                self.rec['image']=fi.read()
                fi.close()
        ConvenientImporter.commit_rec(self,*args,**kwargs)        
    
    def set_text (self, txt):
        """Set raw text."""
        self.textbuffer = gtk.TextBuffer()
        self.textview.set_buffer(self.textbuffer)
        parsed = self.parser.parse(txt,progress=self.progress)
        tagtable = self.textbuffer.get_tag_table()
        # a list of marks...
        self.sections = []
        self.section_pos = 0
        tot=len(parsed); n=0
        for line,tag in parsed:
            print 'adding line',line,'with tag',tag
            if self.progress:
                self.progress(float(n)/tot,
                              _('Setting up interactive importer')
                              )
                n+=1
            if tag==None:
                self.textbuffer.insert(self.textbuffer.get_end_iter(),
                                       line)            
            else:
                if not tagtable.lookup(tag):
                    tagtable.add(gtk.TextTag(tag))
                smark = self.textbuffer.create_mark(None,
                                                    self.textbuffer.get_end_iter(),
                                                    True)
                self.textbuffer.insert_with_tags_by_name(
                    self.textbuffer.get_end_iter(),
                    line,
                    tag
                    )
                emark = self.textbuffer.create_mark(None,
                                                    self.textbuffer.get_end_iter(),
                                                    True)
                self.sections.append((smark,emark))
        print 'We have ',len(self.sections),'sections.'
        self.goto_section(0)
        self.on_new_recipe()

    def goto_next_section (self):
        """Goto our next section"""
        cur_sec = self.get_section_containing_mark()
        end_bound =self.textbuffer.get_iter_at_mark(
            self.sections[cur_sec][1]
            ).get_offset()
        cur_pos = self.textbuffer.get_iter_at_mark(
            self.textbuffer.get_insert()
            ).get_offset()
        if cur_pos < end_bound:
            print 'Moving forward within our section',cur_sec
            self.goto_section(cur_sec,direction=1)
        else:
            print 'Moving forward',cur_sec,'->',cur_sec+1
            self.goto_section(cur_sec+1,direction=1)

    def goto_prev_section (self):
        """Goto our previous section"""
        cur_sec = self.get_section_containing_mark()
        start_bound =self.textbuffer.get_iter_at_mark(
            self.sections[cur_sec][0]
            ).get_offset()
        cur_sel = self.textbuffer.get_selection_bounds()
        if cur_sel:
            print 'use selection...'
            cur_pos = (cur_sel[0].get_offset()<cur_sel[1].get_offset() and 
                       cur_sel[0].get_offset() or
                       cur_sel[1].get_offset()
                       )
        else:
            print 'use cursor...'
            cur_pos = self.textbuffer.get_iter_at_mark(
                self.textbuffer.get_insert()
                ).get_offset()
        if cur_pos > start_bound:
            print 'Moving backward within our section',cur_sec
            self.goto_section(cur_sec,direction=-1)
        else:
            print 'Moving backward',cur_sec,'->',cur_sec-1
            self.goto_section(cur_sec-1,direction=-1)

    def section_contains_mark (self, section, mark=None):
        if not mark: mark = self.textbuffer.get_insert()
        if type(section)==int: section = self.sections[section]
        st,end = section
        siter = self.textbuffer.get_iter_at_mark(st)
        eiter = self.textbuffer.get_iter_at_mark(end)
        citer = self.textbuffer.get_iter_at_mark(mark)
        return siter.get_offset() < citer.get_offset() < eiter.get_offset()

    def get_section_containing_mark (self):
        """Get the current position of our cursor relative to our marks"""
        itr = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert())
        cur_offset = itr.get_offset()
        for n,mks in enumerate(self.sections):
            start = self.textbuffer.get_iter_at_mark(mks[0])
            end = self.textbuffer.get_iter_at_mark(mks[1])
            if start.get_offset() <= cur_offset < end.get_offset():
                return n
            elif cur_offset < start.get_offset():
                return n - 1
        return len(self.sections)-1

    def goto_section (self, n, direction=1):
        """Move to section numbered n

        If direction is positive, adjust forward if necessary.
        If direction is negative, adjust backward if necessary.
        """
        if n >= len(self.sections): n = len(self.sections)-1
        elif n < 0: n = 0
        self.curmark = n
        s,e=self.sections[n]        
        start_itr=self.textbuffer.get_iter_at_mark(s)
        end_itr = self.textbuffer.get_iter_at_mark(e)
        print 'Selecting selection ',n,start_itr.get_offset(),\
              '->',end_itr.get_offset()
        # Check where our current section is
        cur_sel = self.textbuffer.get_selection_bounds()
        if cur_sel:
            soffset,eoffset = start_itr.get_offset(),end_itr.get_offset()
            print 'target:',soffset,eoffset
            cur_start,cur_end = cur_sel
            print 'current:',cur_start.get_offset(),cur_end.get_offset()
            if cur_start.get_offset() < soffset and cur_end.get_offset() > eoffset:
                print 'we contain the target -- move along!'
                if direction>0: self.goto_section(n+1)
                else: self.goto_section(n-1)
            if direction > 0 and soffset < cur_end.get_offset() < eoffset:
                print 'adjusting start forward!'
                start_itr = cur_end
                import sys
                if re.match('\s',start_itr.get_char()):
                    start_itr.forward_find_char(lambda c,user_data: re.match('\S',c) and True,
                                                limit=end_itr)
            elif direction < 0 and soffset < cur_start.get_offset() < eoffset:
                print 'adjusting end backward'
                end_itr = cur_start
                if re.match('\s',start_itr.get_char()):
                    start_itr.backward_find_char(lambda c,user_data: re.match('\S',c) and True,
                                                 limit=end_itr)
        print 'selecting ',end_itr.get_offset(),'-',start_itr.get_offset()
        if end_itr.get_offset()==start_itr.get_offset(): print 'Funny, end == start'
        self.textbuffer.select_range(end_itr,
                                     start_itr
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
        #print "on_save called with self.%s" % widget.get_name()
        #print 'commit rec!',self.rec
        self.commit_rec()

    #-- InteractiveImporter.on_quit {
    def on_quit(self, widget, *args):
        #print 'on_quit!'
        #print 'commit!',self.rec
        self.commit_rec()
        #print "on_quit called with self.%s" % widget.get_name()
        self.glade.get_widget('window1').hide()
        if self.progress: self.progress(1,_('Import complete!'))
        gtk.main_quit()
        
    #-- InteractiveImporter.on_quit }

    def set_added_to (self, bool):
        """Set a switch that we have been added to, or not."""
        self.added_to = bool
        if bool: self.glade.get_widget('NewRecipeButton').set_sensitive(bool)

    def on_new_recipe (self, *args):
        # If we already have a recipe
        if self.added_to:
            #print 'committing!'
            self.commit_rec()
        self.start_rec()
        self.set_added_to(False)

    #-- InteractiveImporter.on_cursor_moved {
    def on_cursor_moved (self, widget, *args):
        print 'cursor moved!'
        cursor = self.textbuffer.get_insert()
        itr = self.textbuffer.get_iter_at_mark(cursor)
        tags = itr.get_tags()
        while not tags:
            itr = self.textbuffer.get_iter_at_offset(
                itr.get_offset()-1
                )
            tags = itr.get_tags()
            print 'back up a character...'
        action = None
        print 'we have ',len(tags),'tags'
        for t in tags:
            print 'look at ',t.props.name
            if self.parser_to_choice.has_key(t.props.name):
                action = self.parser_to_choice[t.props.name]
            elif self.attdic.has_key(t.props.name):
                action = self.attdic[t.props.name]
            elif self.textattdic.has_key(t.props.name):
                action = self.textattdic[t.props.name]
        print 'setting action->',action
        self.set_current_action(action)
        
    #-- InteractiveImporter.on_cursor_moved }

    #-- InteractiveImporter.on_ingredientEventBox_drag_drop {
    def on_ingredientEventBox_drag_drop(self, widget, *args):
        #print "on_ingredientEventBox_drag_drop called with self.%s" % widget.get_name()
        pass
    #-- InteractiveImporter.on_ingredientEventBox_drag_drop }

    #-- InteractiveImporter.on_back {
    def on_back(self, widget, *args):
        #print "on_back called with self.%s" % widget.get_name()
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
        #print 'Action:',active_txt
        #print 'Selection:',selection
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
        #print st,end,dir(end)
        while end.starts_line() and end.backward_char():
            end = self.textbuffer.get_iter_at_offset(end.get_offset()-1)
        self.textbuffer.insert_with_tags(end,']',self.markup_tag)
        # We'll do something real soon...
        #self.resultbuffer.insert(
        #    self.resultbuffer.get_end_iter(),
        #    "%s: %s\n"%(active_txt,selection)
        #    )
        action = self.actions[active_txt]
        #print 'Calling ',active_txt,'->',action
        if self.action_to_label.has_key(active_txt):
            active_txt = self.action_to_label[active_txt]
        action(active_txt,selection)
        self.on_forward(None)
    #-- InteractiveImporter.on_apply }

class InteractiveTextImporter (InteractiveImporter):
    def __init__ (self, filename, rd, progress=None, source=None, threaded=False,custom_parser=None):
        #print 'iti: file:',filename,'rd:',rd
        InteractiveImporter.__init__(self,rd,progress=progress,custom_parser=custom_parser)
        ofi = file(filename,'r')
        self.set_text(ofi.read())
        ofi.close()

    def __repr__ (self): return "<InteractiveTextImporter>"



def main():
    from gourmet import recipeManager
    rd = recipeManager.RecipeManager(**recipeManager.dbargs)
    window1 = InteractiveImporter(rd)
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

To accompany dish:
1 loaf bread
1 head garlic
1/4 c. olive oil

In a food processor, mix together the basil, oil and nuts and garlic, altering as you like to make the pesto nuttier, more garlicky, or more oily.

Meanwhile, boil a large pot of water and cook spaghetti.

Chop up tomatoes roughly.

Toss spaghetti in pesto and tomatoes.
""")
    window1.run()        

if __name__ == '__main__':
    main()
