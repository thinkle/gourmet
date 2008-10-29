import gtk
import RatingWidget
from gourmet import convert, mnemonic_manager, gglobals

class DiffTable (gtk.Table):
    """A Table displaying differences in a recipe.

    diff_dic is a dictionary with the differences.
    {'attribute':(VAL1,VAL2,...)}

    recipe_object is a recipe object representing one of our duplicate
    recs, from which we can grab attributes that are not different.
    """

    def __init__ (self, diff_dic, recipe_object=None, parent=None):
        self.idiffs = []
        self.diff_dic = diff_dic
        gtk.Table.__init__(self)
        self.selected_dic = {}
        self.set_col_spacings(6)
        self.set_row_spacings(6)        
        self.row = 0
        self.max_cols = 1
        for attr,name,typ in gglobals.REC_ATTRS \
                + [('image','Image',None)] \
                + [(attr,gglobals.TEXT_ATTR_DIC[attr],None) for attr in gglobals.DEFAULT_TEXT_ATTR_ORDER]:
            if diff_dic.has_key(attr):
                buttons = self.build_options(attr,self.diff_dic[attr])
                label = gtk.Label('_'+name+':')
                label.set_alignment(0.0,0.5)
                label.set_use_underline(True)
                label.show()
                self.attach(label,0,1,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
                target = None
                for col,b in enumerate(buttons):
                    self.setup_widget_size(b,in_col=True)
                    b.show()
                    if not target:
                        target = b
                        label.set_mnemonic_widget(target)
                    self.attach(b,col+1,col+2,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
                    if col > self.max_cols: self.max_cols = col
                self.row += 1
            elif recipe_object and hasattr(recipe_object,attr) and getattr(recipe_object,attr):
                att_label = gtk.Label(name+':')
                att_label.set_use_underline(True)
                att_label.set_alignment(0,0.5)
                att_label.show()
                constructor = get_display_constructor(attr)
                val = getattr(recipe_object,attr)
                val_label = constructor(getattr(recipe_object,attr))
                val_label.show()
                self.setup_widget_size(val_label,False)
                if hasattr(val_label,'set_alignment'): val_label.set_alignment(0,0.5)
                self.attach(att_label,0,1,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
                self.attach(val_label,1,5,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)                
                self.row += 1
        self.mm = mnemonic_manager.MnemonicManager()
        self.mm.add_toplevel_widget(self)
        self.mm.fix_conflicts_peacefully()
        self.rec = recipe_object.id
        
    def setup_widget_size (self, w, in_col=True):
        if in_col:
            w.set_size_request(230,-1)
        else:
            w.set_size_request(650,-1)

    def build_options (self, attribute, values):
        buttons = []
        group_rb = None
        make_widget = get_display_constructor(attribute)
        for v in values:
            rb = gtk.RadioButton(group=group_rb)
            if not group_rb: group_rb = rb
            if v is not None:
                rb.add(make_widget(v))
            else:
                rb.add(gtk.Label(_("None")))
            rb.show_all()
            buttons.append(rb)
            rb.connect('toggled',self.value_toggled,attribute,v)
        self.selected_dic[attribute] = values[0]
        for n,v in enumerate(values):
            if v:
                buttons[n].set_active(True)
                break
        return buttons

    def value_toggled (self, rb, attribute, v):
        self.selected_dic[attribute] = v

    def add_ingblocks (self, rd, recs):
        #print 'add_ingblocks for ',[r.id for r in recs]
        self.rd = rd
        self.iblock_dic = {}
        if len(recs) == 1:
            blocks = recipeIdentifier.format_ingdiff_line(
                recipeIdentifier.format_ings(recs[0],self.rd)
                )
            self.iblock_dic[blocks[0]] = recs[0]
        else:
            blocks = []
            rec_0 = recs[0]
            for r in recs[1:]:
                chunks = self.get_ing_text_blobs(rec_0,r)
                if not chunks and not blocks:
                    # If there is no diff, in other words, and we
                    # don't yet have any block...
                    chunks = [recipeIdentifier.format_ings(recs[0],self.rd)]
                elif not chunks:
                    # Otherwise if there are no diffs we just continue
                    # our loop...
                    continue
                if not blocks:
                    blocks = [chunks[0]]
                    self.iblock_dic[blocks[0]] = rec_0
                if chunks and len(chunks) > 1:
                    new_block = chunks[1]
                    if new_block not in blocks:
                        blocks.append(new_block)
                        self.iblock_dic[new_block] = r
        group_rb = None
        name = _('Ingredients')
        if len(blocks) > 1:
            lab = gtk.Label('_'+_("Ingredients")); lab.set_use_underline(True)
            for col,block in enumerate(blocks):
                rb = gtk.RadioButton(
                    label=_("Recipe")+ ' ' +'%i'%(col+1),
                    group=group_rb
                    )
                if not group_rb:
                    group_rb = rb
                    lab.set_mnemonic_widget(rb)
                if not block:
                    rb.add(gtk.Label(_("None")))                    
                else:
                    for n,txt in enumerate(block):
                        l = gtk.Label(txt)
                        l.set_alignment(0.0,0.0)                    
                        l.set_use_markup(True)
                        l.set_line_wrap(True); l.set_line_wrap_mode(gtk.WRAP_WORD)
                        l.show()
                        self.setup_widget_size(l,in_col=True)
                        self.attach(l,col+1,col+2,self.row+1+n,self.row+2+n,
                                    xoptions=gtk.SHRINK|gtk.FILL,
                                    yoptions=gtk.SHRINK|gtk.FILL)
                    #rb.add(l)
                rb.connect('toggled',self.ing_value_toggled,block)
                self.setup_widget_size(rb,in_col=True)                
                rb.show()
                self.attach(rb,col+1,col+2,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
        else:
            lab = gtk.Label(_("Ingredients")); lab.show()
            l = gtk.Label(blocks[0])
            l.set_alignment(0.0,0.0)
            l.set_use_markup(True)
            l.set_line_wrap(True); l.set_line_wrap_mode(gtk.WRAP_WORD)
            l.show()
            self.attach(l,1,5,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)
        lab.set_alignment(0.0,0.0); lab.show()
        self.attach(lab,0,1,self.row,self.row+1,xoptions=gtk.SHRINK|gtk.FILL,yoptions=gtk.SHRINK|gtk.FILL)

    def ing_value_toggled (self, rb, block):
        if rb.get_active():
            self.rec = self.iblock_dic[block]

    def get_ing_text_blobs (self, r1, r2):
        """Return an ing-blurb for r1 and r2 suitable for display."""
        idiff = recipeIdentifier.diff_ings(self.rd,r1,r2)
        if idiff: self.idiffs.append(idiff)
        def is_line (l):
            return not (l == '<diff/>')
        if idiff:
            return [
                tuple([recipeIdentifier.format_ingdiff_line(i)
                 for i in filter(is_line,igroup)
                 ])
                for igroup in idiff
                ]
        else:
            return None
            
def put_text_in_scrolled_window (text):
    sw = gtk.ScrolledWindow()
    tv = gtk.TextView()
    sw.add(tv)
    tv.get_buffer().set_text(text)
    tv.set_editable(False)
    tv.set_wrap_mode(gtk.WRAP_WORD)
    sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    tv.show()
    return sw

def make_text_label (t, use_markup=False):
    if not t:
        return gtk.Label(_('None'))
    elif len(t) < 30:
        return gtk.Label(t)
    elif len(t) < 250:
        l = gtk.Label(t)
        if use_markup: l.set_use_markup(use_markup)
        l.set_line_wrap_mode(gtk.WRAP_WORD)
        return l
    else:
        return put_text_in_scrolled_window(t)

def get_display_constructor (attribute):
    if attribute == 'rating':
        return lambda v: ratingWidget.make_star_image(
            ratingWidget.star_generator,
            value=v,
            upper=10)
    elif attribute in ['preptime','cooktime']:
        return lambda v: gtk.Label(convert.seconds_to_timestring(v))
    elif attribute=='image':
        return lambda v: (v and gtk.Label("An Image") or gtk.Label("No Image"))
    elif attribute in gglobals.DEFAULT_TEXT_ATTR_ORDER:        
        return make_text_label
    else:
        return lambda v: v and gtk.Label(v) or gtk.Label(_('None'))
