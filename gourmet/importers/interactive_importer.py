from gi.repository import Gtk, Pango
from xml.sax.saxutils import escape
from .generic_recipe_parser import RecipeParser
import gourmet.gtk_extras.cb_extras as cb
import gourmet.gglobals as gglobals
from . import importer
import re
from gourmet.threadManager import NotThreadSafe
from . import imageBrowser
import gourmet.ImageExtras as ImageExtras
from gettext import gettext as _

# TODO
# 1. Make this interface actually import recipes...
# 2. Add drop-down menu buttons in place of red labels to make it
#    trivial to change the label of something labelled.
# 3. Remove button-hell interface and come up with something cleaner
#    and more attractive.
# 4. Add Undo support to editing (ugh -- this will be a PITA)

DEFAULT_TAGS = []
DEFAULT_TAG_LABELS = gglobals.REC_ATTR_DIC.copy()
DEFAULT_TAG_LABELS.update(gglobals.TEXT_ATTR_DIC)

for attr in gglobals.DEFAULT_ATTR_ORDER:
    if attr != 'link':
        DEFAULT_TAGS.append(attr)
        if attr == 'yields':
            # a bit of a hack -- we want to make 'yield unit' a button
            DEFAULT_TAGS.append('yield_unit')
            DEFAULT_TAGS.append('servings')

DEFAULT_TAGS.extend(gglobals.DEFAULT_TEXT_ATTR_ORDER)

DEFAULT_TAGS.extend(['ingredients','inggroup','ignore'])
for tag,label in [
    ('servings',_('Servings')),
    ('ingredients',_('Ingredients')),
    ('inggroup',_('Ingredient Subgroup')),
    ('ignore',_('Hide'))
    ]:
    if tag not in DEFAULT_TAG_LABELS:
        DEFAULT_TAG_LABELS[tag] = label

UI_TAG_ORDER = [
    (_('Description'),[
        ('title','servings'),
        ('yields','yield_unit'),
        ('source','rating'),
        ('category','cuisine'),
        ('preptime','cooktime')]),
    (_('Text'),[('instructions','modifications')]),
    (_('Ingredients'),[('ingredients','inggroup')]),
    (_('Actions'),[('ignore','clear'),
                   ('newrec',)]),
    ]

class ConvenientImporter (importer.Importer):
    """Add some convenience methods to our standard importer.
    """
    def add_attribute (self, attname, txt):
        txt=txt.strip()
        if attname in self.rec:
            self.rec[attname] = self.rec[attname] + ', ' + txt
        else:
            self.rec[attname] = txt

    def add_text (self, attname, txt):
        if attname in self.rec:
            self.rec[attname] = self.rec[attname] + '\n' + txt
        else:
            self.rec[attname] = txt

    def add_ing_group (self, txt):
        self.group = txt.strip()

    def add_ing_from_text (self, txt):
        if not hasattr(self,'db'):
            import gourmet.backends.db as db
            self.db = db.get_database()
        parsed_dict = self.db.parse_ingredient(txt)
        self.ing = parsed_dict
        self.commit_ing()

    def add_ings_from_text (self, txt, break_at='\n'):
        """Add list of ingredients from block of text.

        By default, there is one ingredient per line of text."""
        txt=txt.strip()
        for i in txt.split(break_at):
            if (i.strip()):
                self.add_ing_from_text(i.strip())

class InteractiveImporter (ConvenientImporter, NotThreadSafe):

    NEW_REC_TEXT = _('New Recipe')

    def __init__ (self,
                  custom_parser = None,
                  tags=DEFAULT_TAGS,
                  tag_labels=DEFAULT_TAG_LABELS,
                  modal=True,
                  title=_('Import recipe')):
        self.title = title
        if custom_parser: self.parser = custom_parser
        else: self.parser = RecipeParser()
        self.labels_by_tag = tag_labels
        self.tags_by_label = {self.NEW_REC_TEXT:'newrec'}
        for k,v in list(self.labels_by_tag.items()): self.tags_by_label[v]=k
        self.tags = tags
        self.setup_window()
        self.setup_action_area()
        self.markup_marks = {}; self.markup_partners = {}
        self.anchors = []
        self.midno = 0 # an ID counter for markup marks we insert
        self.labelled = []
        self.label_counts = {}
        self.modal = modal # If we're in an embedded gtk mainloop...
        ConvenientImporter.__init__(self)

    def setup_window (self):
        # set our parent...
        from gourmet.threadManager import get_thread_manager_gui
        import gourmet.GourmetRecipeManager
        tmg = get_thread_manager_gui()
        self.w = Gtk.Window();
        self.w.set_title(self.title)
        main_app = gourmet.GourmetRecipeManager.get_application()
        self.w.set_transient_for(main_app.window)
        self.w.set_destroy_with_parent(False)
        self.hb = Gtk.HBox()
        self.w.add(self.hb)
        self.tv = Gtk.TextView()
        self.tv.set_size_request(600,500)
        self.tv.set_wrap_mode(Gtk.WrapMode.WORD)
        self.action_area = Gtk.VBox()
        sw = Gtk.ScrolledWindow(); sw.add(self.tv)
        sw.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        self.hb.add(sw); sw.show(); self.tv.show()
        self.hb.pack_end(self.action_area,expand=False); self.action_area.show()
        self.tb = self.tv.get_buffer()
        self.setup_tags()

    def setup_action_area (self):
        # Set up hard-coded functional buttons...
        self.new_recipe_button = Gtk.Button(_('_New Recipe'))
        self.new_recipe_button.connect('clicked',self.new_recipe_cb)
        self.remove_markup_button = Gtk.Button(_('Clear _Tags'))
        self.remove_markup_button.connect('clicked',self.clear_tags)
        # Set up ActionModel (used for drop-down menu version of these commands)
        self.action_model = Gtk.ListStore(str,str)
        action_table = Gtk.Table()
        self.action_area.pack_start(action_table,expand=False)
        r = 0 #rownum
        # Get our UI layout from UI_TAG_ORDER
        for label,rows in UI_TAG_ORDER:
            if r != 0:
                blank = Gtk.Label(label='')
                action_table.attach(blank,0,2,r,r+1);blank.show()
            r += 1
            l = Gtk.Label(); l.set_markup('<b>'+label+'</b>')
            l.set_alignment(0.0,0.5)
            action_table.attach(l,0,2,r,r+1); l.show()
            r += 1
            for row in rows:
                for c,t in enumerate(row): #column number, tag
                    if t == 'clear':
                        tag_button = self.remove_markup_button
                    elif t=='newrec':
                        tag_button = self.new_recipe_button
                    else:
                        tag_button = Gtk.Button('_'+self.labels_by_tag[t])
                        self.action_model.append([self.labels_by_tag[t],t])
                        tag_button.connect('clicked',
                                           self.label_callback,
                                           self.labels_by_tag[t])
                    action_table.attach(
                        tag_button,
                        c,c+1,r,r+1,
                        xpadding=12,
                        )
                r += 1
        action_table.set_row_spacings(3)
        action_table.set_col_spacings(3)
        #for t in self.tags:
        #
        #    self.action_model.append([self.labels_by_tag[t],t])
        #    tag_button = Gtk.Button('_'+self.labels_by_tag[t])
        #    tag_button.connect('clicked',
        #                       self.label_callback,
        #                       self.labels_by_tag[t])
        #    self.action_area.pack_start(tag_button,expand=False,fill=False,padding=6)
        #    tag_button.show()
        #
        self.import_button = Gtk.Button(_('Import Recipe'))
        self.import_button.connect('clicked',
                                      lambda *args: self.commit_changes())
        self.import_button.set_alignment(0.5,1.0)
        self.action_area.pack_end(self.import_button,fill=False,expand=False)
        self.action_area.show_all()

    def setup_tags (self):
        self.markup_tag = Gtk.TextTag('markup')
        self.markup_tag.set_property('editable',False)
        self.markup_tag.set_property('scale',Pango.SCALE_SMALL)
        self.markup_tag.set_property('rise',15)
        self.markup_tag.set_property('foreground',
                                     '#f00'
                                     )
        self.ignore_tag = Gtk.TextTag('ignore')
        self.ignore_tag.set_property('invisible',True)
        self.ignore_tag.set_property('editable',False)
        self.tb.get_tag_table().add(self.markup_tag)
        self.tb.get_tag_table().add(self.ignore_tag)

    def label_callback (self, button, label):
        self.label_selection(label)

    def label_selection (self, label):
        cursel = self.tb.get_selection_bounds()
        if cursel:
            st,end = cursel
        else:
            # Otherwise, there's no clear sane default... we'll just
            # select the current whole line
            cur_mark = self.tb.get_insert()
            cur_pos=Gtk.TextBuffer.get_iter_at_mark(cur_mark)
            cur_pos.backward_chars(
                cur_pos.get_line_offset())
            st = cur_pos
            end = cur_pos.forward_line()
        self.label_range(st,end,label)

    def insert_with_label (self, st, text, label):
        start_offset = st.get_offset()
        self.tb.insert(st,text)
        end_offset = start_offset + len(text)
        self.label_range(
            self.tb.get_iter_at_offset(start_offset),
            self.tb.get_iter_at_offset(end_offset),
            label
            )

    def unhide_area (self, midno):
        st,end = self.markup_marks[midno]
        self.tb.remove_tag(self.ignore_tag,
                           self.tb.get_iter_at_mark(st),
                           self.tb.get_iter_at_mark(end)
                           )

    def hide_range (self, st, end):
        """Hide text between start and end.

        Return midno that can be used to unhide the range."""
        midno = self.midno; self.midno += 1
        start_mark = Gtk.TextMark('start-markup-%s'%midno,False)
        end_mark = Gtk.TextMark('end-markup-%s'%midno,True)
        self.tb.apply_tag(self.ignore_tag,
                       st,end)
        self.tb.add_mark(start_mark,st)
        self.tb.add_mark(end_mark,end)
        self.markup_marks[midno] = (start_mark,end_mark)
        return midno

    def label_range (self, st, end, label):
        if self.tags_by_label.get(label,'')=='ignore':
            midno = self.hide_range(st,end)
            b = Gtk.Button('Ignored text: Reveal hidden text')
            anchor = self.insert_widget(end,b)
            def unhide_text (*args):
                self.unhide_area(midno)
                self.remove_widget(anchor)
            b.connect('clicked',unhide_text)
            b.show()
            return
        if label in self.label_counts:
            count = self.label_counts[label]
            self.label_counts[label] += 1
        else:
            self.label_counts[label] = 1
            count = 0
        smark = Gtk.TextMark(label+'-'+str(count)+'-start',True)
        emark = Gtk.TextMark(label+'-'+str(count)+'-end',False)
        self.tb.add_mark(smark,st)
        self.tb.add_mark(emark,end)
        self.labelled.append((smark,emark))
        # Now we add the labels...
        start_txt = '['
        start_id = self.insert_markup_text(st,start_txt,self.markup_tag)
        # Now move the mark back up...
        new_pos = self.tb.get_iter_at_mark(smark); new_pos.forward_chars(len(start_txt))
        self.tb.move_mark(smark,new_pos)
        # Create a "Remove me" button
        #b = Gtk.Button('_Remove tag'); b.show)(
        b = Gtk.Button()
        i = Gtk.Image(); i.set_from_stock(Gtk.STOCK_REMOVE,Gtk.IconSize.MENU)
        b.add(i); i.show()
        itr = self.tb.get_iter_at_mark(emark)
        anchor = self.insert_widget(itr,b)
        # Set up combo button...
        labelbutton = Gtk.ComboBoxText()
        labelbutton.set_model(self.action_model)
        cb.cb_set_active_text(labelbutton,label)
        anchor2 = self.insert_widget(self.tb.get_iter_at_mark(smark),labelbutton)
        # Add final bracket for end of markup
        end_bracket_itr = self.tb.get_iter_at_mark(emark)
        end_id = self.insert_markup_text(end_bracket_itr,']',self.markup_tag)
        self.markup_partners[start_id]=end_id; self.markup_partners[end_id]=start_id
        # Now back up our itr one character (it got advanced by adding
        # the right bracket and the button)
        eitr = self.tb.get_iter_at_mark(emark)
        eitr.backward_chars(2)
        self.tb.move_mark(emark,eitr)
        # Define callback to remove our text when button is clicked
        def remove_markup (*args):
            self.labelled.remove((smark,emark))
            self.remove_markup_text(start_id)
            self.remove_markup_text(end_id)
            self.remove_widget(anchor)
            self.remove_widget(anchor2)
        def change_mark (cb):
            # copy marks for safekeeping...
            new_text = cb.get_active_text()
            sm = Gtk.TextMark(None,True)
            self.tb.add_mark(sm,self.tb.get_iter_at_mark(smark))
            em = Gtk.TextMark(None,False)
            self.tb.add_mark(em,self.tb.get_iter_at_mark(emark))
            # remove old marks...
            remove_markup()
            # And relabel!
            self.label_range(
                self.tb.get_iter_at_mark(sm),
                self.tb.get_iter_at_mark(em),
                new_text
                )
        labelbutton.connect('changed',change_mark)
        b.connect('clicked',remove_markup)

    def new_recipe_cb (self, *args):
        # Start a new recipe at cursor
        itr = self.tb.get_iter_at_mark(self.tb.get_insert())
        self.label_range(itr,itr,self.NEW_REC_TEXT)

    def insert_markup_text (self, itr, text, *tags):
        """Insert markup text into the buffer. We do this in such a
        way that we can remove it easily later.
        """
        midno = self.midno; self.midno += 1
        start_mark = Gtk.TextMark('start-markup-%s'%midno,False)
        end_mark = Gtk.TextMark('end-markup-%s'%midno,True)
        start_offset = itr.get_offset()
        if tags:
            self.tb.insert_with_tags(itr,text,*tags)
        else:
            self.tb.insert(itr,text)
        self.tb.add_mark(start_mark,self.tb.get_iter_at_offset(start_offset))
        end_offset = start_offset + len(text)
        end_itr = self.tb.get_iter_at_offset(end_offset)
        self.tb.add_mark(end_mark,end_itr)
        self.markup_marks[midno] = (start_mark,end_mark)
        return midno

    def change_mark (self, cb, smark, emark, start_id, end_id):

        new_label = cb.get_active_text()


    def insert_widget (self, itr, widget):
        anchor = self.tb.create_child_anchor(itr)
        self.anchors.append(anchor)
        self.tv.add_child_at_anchor(widget,anchor)
        widgetstart = self.tb.get_iter_at_child_anchor(anchor)
        widgetend = widgetstart.copy(); widgetend.forward_char()
        self.tb.apply_tag(self.markup_tag,widgetstart,widgetend)
        widget.show()
        return anchor

    def remove_widget (self, anchor):
        anchor_iter = self.tb.get_iter_at_child_anchor(anchor)
        delete_to = anchor_iter.copy()
        delete_to.forward_char()
        self.tb.delete(anchor_iter,delete_to)

    def remove_markup_text (self, idno):
        smark,emark = self.markup_marks[idno]
        sitr,eitr = (self.tb.get_iter_at_mark(smark),
                     self.tb.get_iter_at_mark(emark))
        self.tb.delete(sitr,eitr)

    def clear_tags (self, *args):
        """Clear all markup in current selection, or whole buffer if
        there is no selection
        """
        cursel = self.tb.get_selection_bounds()
        if cursel:
            st,end = cursel
        else:
            st,end = self.tb.get_bounds()
        st_offset = st.get_offset()
        e_offset = end.get_offset()
        for idno,iters in list(self.markup_marks.items()):
            lst,lend = iters
            if ((e_offset > self.tb.get_iter_at_mark(lst).get_offset() > st_offset)
                or
                (e_offset > self.tb.get_iter_at_mark(lend).get_offset() > st_offset)):
                self.remove_markup_text(idno)
                if idno in self.markup_partners:
                    self.remove_markup_text(self.markup_partners[idno])
        for lst,lend in self.labelled[:]:
            if ((e_offset > self.tb.get_iter_at_mark(lst).get_offset() > st_offset)
                or
                (e_offset > self.tb.get_iter_at_mark(lend).get_offset() > st_offset)):
                self.labelled.remove((lst,lend))
        for anchor in self.anchors[:]:
            anchor_iter = self.tb.get_iter_at_child_anchor(anchor)
            if e_offset > anchor_iter.get_offset() > st_offset:
                self.anchors.remove(anchor)
                self.remove_widget(anchor)

    def commit_changes (self):
        self.labelled.sort(key=lambda x: self.tb.get_iter_at_mark(x[0]).get_offset())
        if not self.labelled: return
        self.start_rec()
        started = False
        for smark,emark in self.labelled:
            siter = self.tb.get_iter_at_mark(smark)
            eiter = self.tb.get_iter_at_mark(emark)
            text = siter.get_text(eiter)
            name = smark.get_name()
            label = name.split('-')[0]
            tag = self.tags_by_label[label]
            if tag in gglobals.TEXT_ATTR_DIC:
                self.add_text(tag,text); started=True
            elif tag in gglobals.REC_ATTR_DIC:
                if text: self.add_attribute(tag,text)
            elif tag == 'ingredient':
                if text: self.add_ing_from_text(text); started=True
            elif tag == 'ingredients':
                if text: self.add_ings_from_text(text); started=True
            elif tag == 'inggroup':
                if text: self.add_ing_group(text); started=True
            elif tag=='newrec':
                if not started: continue
                # Then we're starting a new recipe at this point...
                # Commit old recipe...
                self.commit_rec(); started=False
                # Start new one...
                self.start_rec()
            elif tag=='ignore':
                continue
            elif tag == 'servings':
                self.add_attribute('yields',text)
                self.add_attribute('yield_unit','servings')
            else:
                try:
                    print('UNKNOWN TAG',tag,text,label)
                except UnicodeError:
                    print('UNKNOWN TAG (unprintable)')
        if started: self.commit_rec()
        if hasattr(self,'images') and self.images:
            # This is ugly -- we run the dialog once per recipe. This
            # should happen rarely in current use-case (I don't know
            # of a usecase where many recipes will come from a single
            # text document / website); if in fact this becomes a
            # common usecase, we'll need to rework the UI here.
            for rec in self.added_recs:
                ibd = imageBrowser.ImageBrowserDialog(
                    title=_('Select recipe image'),
                    label=_('Select image for recipe "%s"')%escape(rec.title or _('Untitled')),
                    sublabel=_("Below are all the images found for the page you are importing. Select any images that are of the recipe, or don't select anything if you don't want any of these images."),
                    )
                for i in self.images: ibd.add_image_from_uri(i)
                ibd.run()
                if ibd.ret:
                    with open(imageBrowser.get_image_file(ibd.ret), 'rb') as ifi:
                        image_str = ifi.read()
                    image = ImageExtras.get_image_from_string(image_str)
                    # Adding image!
                    thumb = ImageExtras.resize_image(image,40,40)
                    self.rd.modify_rec(rec,{'image':ImageExtras.get_string_from_image(image),
                                            'thumb':ImageExtras.get_string_from_image(thumb),
                                            })
        if self.modal:
            self.w.hide()
            Gtk.main_quit()

    def set_text (self, txt):
        txt = str(txt) # convert to unicode for good measure
        txt = re.sub(r'(\n\s*\n)+','\n\n',txt) # Take out extra newlines
        txt = self.parser.parse(txt) # Parse
        self.set_parsed(txt)

    def set_parsed (self, parsed):
        #dbg_file = open('/tmp/out','w')
        for chunk,tag in parsed:
            #dbg_file.write(chunk)
            if tag==None:
                self.tb.insert(self.tb.get_end_iter(),
                               chunk)
            else:
                self.insert_with_label(
                    self.tb.get_end_iter(),
                    chunk,
                    self.labels_by_tag.get(tag,tag)
                    )
        #dbg_file.close()

    def do_run (self):
        self.w.show_all()
        if self.modal:
            self.w.connect('delete-event',Gtk.main_quit)
            Gtk.main()
        else:
            self.w.connect('delete-event',lambda *args: self.w.hide())



if __name__ == '__main__':
    ii = InteractiveImporter()
    ii.w.connect('delete-event',Gtk.main_quit)
    ii.w.show_all()
    if True:
        ii.images = ['http://thinkle.github.io/gourmet/images/screenshots/CardView.png']
        ii.set_text(
        """
Quick Pesto Dinner

Category: Quick, Easy, Summer
Yield: 2 Servings

Ingredients:
1-2 c. fresh basil
\xbc  cup minced fresh ginger (about 6 inches ginger root, peeled)
\xbc lb. whole-wheat spaghetti
1-2 fresh tomatoes

To accompany dish:
1 loaf bread
1 head garlic
1/4 c. olive oil

In a food processor, mix together the basil, oil and nuts and garlic, altering as you like to make the pesto nuttier, more garlicky, or more oily.

Meanwhile, boil a large pot of water and cook spaghetti.

Chop up tomatoes roughly.

Toss spaghetti in pesto and tomatoes.

Ignore: this
""")
    Gtk.main()

