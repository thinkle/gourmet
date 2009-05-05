import gtk, pango
from gettext import gettext as _
from generic_recipe_parser import RecipeParser
import gourmet.gtk_extras.cb_extras as cb
import gourmet.gglobals as gglobals
import importer
import re
import gourmet.convert as convert
from gourmet.threadManager import NotThreadSafe
import imageBrowser
import gourmet.ImageExtras as ImageExtras
# TODO
# 1. Make this interface actually import recipes...
# 2. Add drop-down menu buttons in place of red labels to make it
#    trivial to change the label of something labelled.
# 3. Remove button-hell interface and come up with something cleaner
#    and more attractive.
# 4. Add Undo support to editing (ugh -- this will be a PITA)

DEFAULT_TAGS = []
DEFAULT_TAG_LABELS = gglobals.REC_ATTR_DIC.copy()
for attr in gglobals.DEFAULT_ATTR_ORDER:
    if attr != 'link':
        DEFAULT_TAGS.append(attr)
        if attr == 'yields':
            # a bit of a hack -- we want to make 'yield unit' a button
            DEFAULT_TAGS.append('yield_unit')
DEFAULT_TAGS.extend(['instructions','ingredients','inggroup','ignore'])
for tag,label in [('instructions',_('Instructions')),
                  ('ingredients',_('Ingredients')),
                  ('inggroup',_('Ingredient Subgroup')),
                  ('ignore',_('Hide'))
                  ]:
    if not DEFAULT_TAG_LABELS.has_key(tag):
        DEFAULT_TAG_LABELS[tag] = label

class ConvenientImporter (importer.Importer):
    """Add some convenience methods to our standard importer.
    """
    def add_attribute (self, attname, txt):
        txt=txt.strip()
        if self.rec.has_key(attname):
            self.rec[attname] = self.rec[attname] + ', ' + txt
        else:
            self.rec[attname] = txt

    def add_text (self, attname, txt):
        if self.rec.has_key(attname):
            self.rec[attname] = self.rec[attname] + '\n' + txt
        else:
            self.rec[attname] = txt

    def add_ing_group (self, txt):
        self.group = txt.strip()

    def add_ing_from_text (self, txt):
        try:
            txt=unicode(txt.strip())
        except UnicodeDecodeError:
            print 'Weird -- ignoring unicode error with ',txt
            txt = txt.strip()
        txt = re.sub('\s+',' ',txt)
        if not txt: return        
        mm = convert.ING_MATCHER.match(txt)
        if mm:
            amount = mm.group(convert.ING_MATCHER_AMT_GROUP)
            unit = mm.group(convert.ING_MATCHER_UNIT_GROUP)
            item = mm.group(convert.ING_MATCHER_ITEM_GROUP)
            #print 'Parsed ingredient: "%s"'%txt,"into:",amount,'|',unit,'|',item
            # If our unit isn't familiar and is longer than 2
            # characters, don't add it as a unit! (this lets most
            # abbreviations through)
            if unit and not self.conv.unit_dict.has_key(unit.strip()) and len(unit.strip())>2:
                item = unit + ' ' + item
                unit = ''                
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

class InteractiveImporter (ConvenientImporter, NotThreadSafe):

    NEW_REC_TEXT = _('New Recipe')

    def __init__ (self,
                  custom_parser = None,
                  tags=DEFAULT_TAGS,
                  tag_labels=DEFAULT_TAG_LABELS,
                  modal=True):
        if custom_parser: self.parser = custom_parser
        else: self.parser = RecipeParser()
        self.labels_by_tag = tag_labels
        self.tags_by_label = {self.NEW_REC_TEXT:'newrec'}
        for k,v in self.labels_by_tag.items(): self.tags_by_label[v]=k
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
        self.w = gtk.Window()
        self.hb = gtk.HBox()
        self.w.add(self.hb)
        self.tv = gtk.TextView()
        self.tv.set_size_request(600,400)
        self.tv.set_wrap_mode(gtk.WRAP_WORD)
        self.action_area = gtk.VBox()
        sw = gtk.ScrolledWindow(); sw.add(self.tv)
        sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.hb.add(sw); sw.show(); self.tv.show()
        self.hb.add(self.action_area)
        self.tb = self.tv.get_buffer()
        self.setup_tags()

    def setup_action_area (self):
        for t in self.tags:
            tag_button = gtk.Button('_'+self.labels_by_tag[t])
            tag_button.connect('clicked',
                               self.label_callback,
                               self.labels_by_tag[t])
            self.action_area.pack_start(tag_button,expand=False,fill=False,padding=6)
            tag_button.show()
        self.action_area.add(gtk.HSeparator())
        self.remove_markup_button = gtk.Button(_('Clear _Tags'))
        self.remove_markup_button.connect('clicked',self.clear_tags)
        self.action_area.pack_start(self.remove_markup_button,expand=False,fill=False)
        self.new_recipe_button = gtk.Button(_('_New Recipe'))
        self.new_recipe_button.connect('clicked',self.new_recipe_cb)
        self.action_area.pack_start(self.new_recipe_button)
        self.action_area.pack_start(gtk.HSeparator(),expand=False,fill=False)
        self.show_text_button = gtk.Button(stock=gtk.STOCK_OK)
        self.show_text_button.connect('clicked',
                                      lambda *args: self.commit_changes())
        self.action_area.add(self.show_text_button)
        self.action_area.show_all()

    def setup_tags (self):
        self.markup_tag = gtk.TextTag('markup')
        self.markup_tag.set_property('editable',False)
        self.markup_tag.set_property('scale',pango.SCALE_SMALL)
        self.markup_tag.set_property('rise',15)
        self.markup_tag.set_property('foreground',
                                     '#f00'
                                     )
        self.ignore_tag = gtk.TextTag('ignore')
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
            cur_pos = self.tb.get_insert()
            cur_pos.backward_chars(
                cur_pos.get_line_offset())
            st = cur_pos
            end = cur_pos.copy()
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
        start_mark = gtk.TextMark('start-markup-%s'%midno,False)
        end_mark = gtk.TextMark('end-markup-%s'%midno,True)
        self.tb.apply_tag(self.ignore_tag,
                       st,end)
        self.tb.add_mark(start_mark,st)
        self.tb.add_mark(end_mark,end)
        self.markup_marks[midno] = (start_mark,end_mark)
        return midno

    def label_range (self, st, end, label):
        if self.tags_by_label.get(label,'')=='ignore':
            midno = self.hide_range(st,end)
            b = gtk.Button('Ignored text: Reveal hidden text')
            anchor = self.insert_widget(end,b)
            def unhide_text (*args):
                self.unhide_area(midno)
                self.remove_widget(anchor)
            b.connect('clicked',unhide_text)
            b.show()
            return
        if self.label_counts.has_key(label):
            count = self.label_counts[label]
            self.label_counts[label] += 1
        else:
            self.label_counts[label] = 1
            count = 0
        smark = gtk.TextMark(label+'-'+str(count)+'-start',True)
        emark = gtk.TextMark(label+'-'+str(count)+'-end',False)
        self.tb.add_mark(smark,st)
        self.tb.add_mark(emark,end)
        self.labelled.append((smark,emark))
        # Now we add the labels...
        start_txt = '['+label+':'
        start_id = self.insert_markup_text(st,start_txt,self.markup_tag)
        # Now move the mark back up...
        new_pos = self.tb.get_iter_at_mark(smark); new_pos.forward_chars(len(start_txt))
        self.tb.move_mark(smark,new_pos)
        # Create a "Remove me" button
        itr = self.tb.get_iter_at_mark(emark)
        #b = gtk.Button('_Remove tag'); b.show)(
        b = gtk.Button()
        i = gtk.Image(); i.set_from_stock(gtk.STOCK_REMOVE,gtk.ICON_SIZE_MENU)
        b.add(i); i.show()
        anchor = self.insert_widget(itr,b)
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
        start_mark = gtk.TextMark('start-markup-%s'%midno,False)
        end_mark = gtk.TextMark('end-markup-%s'%midno,True)
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
        for idno,iters in self.markup_marks.items():
            lst,lend = iters
            if ((e_offset > self.tb.get_iter_at_mark(lst).get_offset() > st_offset)
                or
                (e_offset > self.tb.get_iter_at_mark(lend).get_offset() > st_offset)):
                self.remove_markup_text(idno)
                if self.markup_partners.has_key(idno):
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
        def mark_sorter (a,b):
            a = self.tb.get_iter_at_mark(a[0]).get_offset()
            b = self.tb.get_iter_at_mark(b[0]).get_offset()
            return cmp(a,b)
        self.labelled.sort(mark_sorter)
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
            else:
                print 'UNKNOWN TAG',tag,text,label
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
                    label=_('Select image for recipe "%s"'%rec.title or _('Untitled')),
                    sublabel=_("Below are all the images found for the page you are importing. Select any images that are of the recipe, or don't select anything if you don't want any of these images."),
                    )
                for i in self.images: ibd.add_image_from_uri(i)
                ibd.run()
                if ibd.ret:
                    ifi = file(imageBrowser.get_image_file(ibd.ret),'r')
                    image_str = ifi.read(); ifi.close()
                    image = ImageExtras.get_image_from_string(image_str)
                    # Adding image!
                    thumb = ImageExtras.resize_image(image,40,40)
                    self.rd.modify_rec(rec,{'image':ImageExtras.get_string_from_image(image),
                                            'thumb':ImageExtras.get_string_from_image(thumb),
                                            })
        if self.modal:
            self.w.hide()
            gtk.main_quit()

    def set_text (self, txt):
        txt = unicode(txt) # convert to unicode for good measure
        self.set_parsed(self.parser.parse(txt))
        

    def set_parsed (self, parsed):
        #dbg_file = file('/tmp/out','w')
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
            self.w.connect('delete-event',gtk.main_quit)
            gtk.main()
        else:
            self.w.connect('delete-event',lambda *args: self.w.hide())
        
    
            
if __name__ == '__main__':
    ii = InteractiveImporter()
    ii.w.connect('delete-event',gtk.main_quit)
    ii.w.show_all()
    if True:
        ii.images = ['http://grecipe-manager.sourceforge.net/CardView.png']
        ii.set_text(
        u"""
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
    gtk.main()
    
