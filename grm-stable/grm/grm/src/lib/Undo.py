import gtk, difflib,re
from gourmet.gdebug import debug

class TooManyChanges (Exception):
    def __init__ (self, value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class UndoableObject:
    """An UndoableObject. This must provide an action, an inverse and a history. Alternatively,
    it can supply get_reapply_action_args, which will allow the action to be "reapplied" to new
    arguments (for example, if the action is setting a text attribute, reapply might set that attribute
    for the currently highlighted text)."""
    
    def __init__ (self, action, inverse, history,
                  action_args=None,
                  undo_action_args=None,
                  get_reapply_action_args=None,
                  get_reundo_action_args=None,
                  reapply_name=None,
                  reundo_name=None,
                  is_undo=False,
                  widget=None, # Keep track of widget where this
                               # action began (useful for GUIs to
                               # check if actions have changed value
                               # from "saved" state)
                  ):
        if not action_args: action_args = []
        if not undo_action_args: undo_action_args = []
        self.history = history
        self.action = action
        self.inverse_action = inverse
        self.get_reapply_action_args = get_reapply_action_args
        self.undo_action_args = undo_action_args
        self.get_reundo_action_args = get_reundo_action_args
        self.reapply_name = reapply_name
        self.reundo_name = reundo_name
        self.is_undo = is_undo  # If our action itself is an undo
        self.widget = widget
        if self.get_reapply_action_args:
            self.reapplyable = True
        else:
            self.reapplyable = False
        self.action_args = action_args

    def perform (self):
        self.action(*self.action_args)
        self.history.append(self)

    def inverse (self):
        u = UndoableObject(self.inverse_action, self.action, self.history,
                           action_args=self.undo_action_args,
                           undo_action_args=self.action_args,
                           get_reapply_action_args=self.get_reundo_action_args,
                           get_reundo_action_args=self.get_reapply_action_args,
                           is_undo=not self.is_undo,
                           widget=self.widget)
        self.history.remove(self)
        u.perform()

    def reapply (self):
        if self.get_reapply_action_args:
            args,undoargs = self.get_reapply_action_args()
            u = UndoableObject(self.action,self.inverse_action,self.history,
                               action_args=args,
                               undo_action_args=undoargs,
                               get_reapply_action_args=self.get_reapply_action_args,
                               reapply_name=self.reundo_name, reundo_name=self.reapply_name)
            u.perform()

    def __repr__ (self):
        return '<Undo.UndoableObject %s widget=%s>'%(self.is_undo,self.widget)

class UndoableTextChange (UndoableObject):
    def __init__ (self, set_text_action, history, initial_text="",text="",txt_id=None,is_undo=False):
        self.txt_id = txt_id
        self.blob_matcher = re.compile('\s+\S+\s+')
        self.initial_text = initial_text
        self.text = text
        self._set_text = set_text_action
        UndoableObject.__init__(self,lambda *args: self._set_text(self.text),lambda *args: self._set_text(self.initial_text),history,
                                is_undo=is_undo,widget=self.txt_id)
        self.mode=self.determine_mode()
        try:
            self.cindex,self.clen = self.find_change(self.text)
        except TooManyChanges:
            debug('Too many changes - assume 0,0',0)
            self.cindex,self.clen = 0,0

    def determine_mode (self,text=None,initial_text=None):
        if not text: text=self.text
        if not initial_text: initial_text=self.initial_text
        if len(text) > len(initial_text):
            return 'add'
        elif len(text) < len(initial_text):
            return 'delete'

    def find_change (self, text2=None, initial_text=None):
        if initial_text is None: initial_text = self.initial_text
        if not self.mode:
            self.text = text2
            self.determine_mode()
        if text2 is None: text2=self.text
        blocks = difflib.SequenceMatcher(None,initial_text,text2).get_matching_blocks()
        # we only are interested in similar blocks at different positions
        # (which tell us where the changes happened).
        ch_blocks = filter(lambda x: x[0] != x[1] and x[2] != 0, blocks)
        if ch_blocks and len(ch_blocks)>1:
            raise TooManyChanges("More than one block changed from '%s' to '%s': %s"%(initial_text,text2,ch_blocks))
        if ch_blocks:
            i,j,n = ch_blocks[0]
            change_length = j-i
            change_index = i
            return [change_index,change_length]
        else:
            if self.mode=='delete':
                return [len(initial_text),len(initial_text)-len(text2)]
            else: #self.mode=='add', we presume
                return [len(initial_text),len(text2)-len(initial_text)]

    def add_text (self, new_text):
        mode=self.determine_mode(new_text,self.text)
        contmode = self.determine_mode(new_text,self.text)
        if (mode == contmode == self.mode):
            try:
                # This whole thing is in a try/except box because
                # there are multiple places where "Too many changes"
                # could crop up as an error.
                cindex,clen = self.find_change(new_text)
                if ((cindex==self.cindex) or
                    (self.mode=='add' and cindex==self.cindex) or
                    (self.mode=='delete' and cindex==(self.cindex-clen))
                    ):
                    if self.mode=='add': changed_text = new_text[cindex:cindex+(self.clen+clen)]
                    else: changed_text=''
                    # Now we make sure the addition is at the end or middle of our new text...
                    relative_cindex,relative_clen = self.find_change(new_text,self.text)
                    # We only consider a word at a time to be a continuous change...
                    if (
                        # Adding text to the end
                        (
                        relative_cindex==cindex+(clen-relative_clen) 
                        or
                        # Adding text to the beginning
                        (relative_cindex==self.clen or relative_cindex==self.cindex) 
                        )
                        and
                        not self.blob_matcher.search(changed_text)
                        ):
                        self.text = new_text
                        self.cindex,self.clen = self.find_change(new_text)
                        ## End here if we've worked
                        return                
            except TooManyChanges:
                pass # We'll go to the end of the method & create a new action
        # If the mode has changed or we have too many changes to
        # handle simply, we just create a new undo action for this new
        # change
        self.new_action(new_text)

    def new_action (self, new_text):
        self.history.append(UndoableTextChange(self._set_text,self.history,
                                               initial_text=self.text, text=new_text,
                                               txt_id=self.txt_id,
                                               )
                            )

    def inverse (self):
        #self._set_text(self.initial_text)
        u=UndoableTextChange(self._set_text,self.history,initial_text=self.text,
                             text=self.initial_text,txt_id=self.txt_id,
                             is_undo=not self.is_undo,
                             )
        self.history.remove(self)
        u.perform()

    def perform (self):
        self._set_text(self.text)
        self.history.append(self)

    def __repr__ (self):
        return '<Undo.UndoableTextChange '+repr(self.mode)+' '+repr(self.txt_id)+\
               repr(self.initial_text)+'=>'+repr(self.text)+'clen'+str(self.clen)+\
               'cindex'+str(self.cindex)+'>'

    def __eq__ (self,obj):
        """We are equal too objects that represent the same txt_id and
        are either the same action as us or the inverse of us
        """
        if not hasattr(obj,'txt_id'):
            return False
        else:
            return (
                self.txt_id==obj.txt_id
                and
                ((self.initial_text==obj.initial_text
                  and
                  self.text == obj.text)
                 or
                 (self.initial_text==obj.text
                  and
                  self.text==obj.initial_text)
                 )
                )
    

class UndoableTextContainer:
    def __init__ (self, container, history):
        self.history = history
        self.container = container
        self.setup_widgets()
        self.txt = self.get_text()
        self._setting = False

    def change_event_cb (self,*args):
        # if the last change is the same as us...
        if self._setting:
            return
        txt = self.get_text()
        if txt == self.txt: return
        if len(self.history)>=1 and hasattr(self.history[-1],'txt_id') and self.history[-1].txt_id==self.container:
            self.change = self.history[-1]
            self.history[-1].add_text(txt)
        else:
            self.change=UndoableTextChange(self._set_text,
                                           self.history,
                                           initial_text=self.txt,
                                           text=txt,
                                           txt_id=self.container)
            self.history.append(self.change)
        self.txt = txt
        
    def setup_widgets (self): pass
    def get_text (self): raise NotImplementedError

    def _set_text (self,txt):
        self._setting = True # Set flag so we don't trigger our own
                             # callbacks
        orig = self.get_text() # Get current text for comparison
                               # (helps with placement of cursor)
        if len(txt) > orig:         # If we're adding
            try:
                index,length = self.change.find_change(txt,orig)
                cursor_index = index+length
            except TooManyChanges:
                # If we changed more than one block, there is no obvious
                # place to put the cursor, so we put it at the end
                cursor_index = len(txt)
        else: # If we're Removing
            try:
                # We get the *index* of the inverse of our action
                # i.e. If we go from Thhis -> This, then we reverse to
                # This -> Thhis (which is the same as where it would
                # have been after hitting backspace) and we put it
                # there.
                index,length = self.change.find_change(orig,txt)
                cursor_index = index
            except TooManyChanges:
                cursor_index = len(txt)
        self.set_text(txt,cursor_index)
        self._setting = False # Unset flag

    def set_text (self,txt,cursor_index): raise NotImplementedError

class UndoableEntry (UndoableTextContainer):
    def __init__ (self, entry,history):
        self.entry = entry
        self.get_text = self.entry.get_text
        UndoableTextContainer.__init__(self,self.entry,history)

    def setup_widgets (self): 
        self.entry.connect('changed',
                           self.change_event_cb
                           )
        
    def set_text (self, txt, cursor_index):
        self.entry.grab_focus()
        self.entry.set_text(txt)
        self.entry.set_position(cursor_index)
        
class UndoableGenericWidget:
    """Wrap a widget in an Undo class.

    We take a set_method, a get_method, and a signal, as well as a
    history list to append our Undo objects to.
    """
    def __init__ (self, widget, history, set_method='set_value',get_method='get_value', signal='changed'):
        self.w = widget
        self.set_method = set_method
        self.get_method = get_method
        self.im_doing_the_setting = False
        self.history = history
        self.last_value = self.get()
        self.w.connect(signal,self.changecb)

    def set (self, val):
        self.im_doing_the_setting = True
        getattr(self.w,self.set_method)(val)
        self.im_doing_the_setting = False

    def get (self):
        return getattr(self.w,self.get_method)()

    def changecb (self,*args):
        if self.im_doing_the_setting:
            # If we are doing the setting, presumably this is from one
            # of the Undo objects we created, in which case we don't
            # want to add a new item to the Undo queue
            return
        old_val = self.last_value
        new_val = self.get()
        if old_val==new_val: return # Ignore redundant changes...
        if new_val != old_val:
            # We don't perform because we're being called after the action has happened.
            # We simply append ourselves to the history list.
            u = UndoableObject(lambda *args: self.set(new_val),
                               lambda *args: self.set(old_val),
                               self.history,
                               widget=self.w
                               )
            self.history.append(u)
            self.last_value=new_val
        
class UndoableTextView (UndoableTextContainer):
    def __init__ (self, textview, history):
        self.tv = textview
        UndoableTextContainer.__init__(self,self.tv,history)
        
    def setup_widgets (self):
        self.buffer = self.tv.get_buffer()
        self.buffer.connect('changed',
                            self.change_event_cb)
        self.buffer.connect('apply-tag',self.change_event_cb)
        self.buffer.connect('remove-tag',self.change_event_cb)
        
    def set_text (self, text, cursor_index):        
        self.buffer.set_text(text)
        self.tv.grab_focus()
        self.buffer.place_cursor(self.buffer.get_iter_at_offset(cursor_index))

    def get_text (self):
        return self.buffer.get_text(self.buffer.get_start_iter(),
                                    self.buffer.get_end_iter())        

class UndoHistoryList (list):
    """An UndoHistoryList."""
    def __init__ (self, undo_widget, redo_widget, reapply_widget=None, signal='activate'):
        self.undo_widget = undo_widget
        self.redo_widget = redo_widget
        self.reapply_widget = reapply_widget
        self.action_hooks = []
        list.__init__(self)
        self.gui_update()
        if signal:
            if self.undo_widget: self.undo_widget.connect(signal,self.undo)
            if self.redo_widget: self.redo_widget.connect(signal,self.redo)
            if self.reapply_widget: self.reapply_widget.connect(signal,self.reapply)

    def add_action_hook (self, hook):
        """Add action hook

        Hook will be a callback as follows

        hook(undo_history,action,type)

        where undo_history is this instance of UndoHistory and
        type is 'perform','undo','redo', or 'reapply'
        """
        self.action_hooks.append(hook)

    def undo (self, *args):
        index = -1
        if len(self) == 0: return False
        try:
            while self[index].is_undo:
                index -= 1
        except IndexError:
            debug('All %s available action are .is_undo=True'%len(self),0)
            print 'There is nothing to undo!'
            print 'All %s actions are undos'%len(self)
            print self,index
            raise
        action = self[index]
        action.inverse()
        for h in self.action_hooks: h(self,action,'undo')

    def redo (self, *args):
        if len(self) == 0: return False
        index = -1
        try:
            while not self[index].is_undo:
                index = index - 1
        except IndexError:
            debug('All %s available actions are is_undo=False'%len(self),0)
            print 'There is nothing to redo!'
            print 'All %s available actions are is_undo=False'%len(self)
            raise
        action = self[index]
        action.inverse()
        for h in self.action_hooks: h(self,action,'redo')

    def reapply (self, *args):
        debug('Reapplying',0)
        action = self[-1]
        action.reapply()
        for h in self.action_hooks: h(self,action,'reapply')

    def set_sensitive (self,w,val):
        debug('set_sensitive',0)
        if not w: return
        try:
            w.set_sensitive(val)
            debug('%s.set_sensitive succeeded'%w,0)
        except AttributeError:
            # 2.6 will give gtk.Action a set_sensitive property, but for now...
            #if type(w)==gtk.Action:
            for p in w.get_proxies():
                debug('setting %s sensitivity to %s'%(w,val),0)
                #p.set_sensitive(val)
                p.set_property('sensitive',val)

    def gui_update (self):
        debug('gui_update',0)
        if len(self) >= 1:
            undoables = [x.is_undo for x in self]
            if False in undoables:
                self.set_sensitive(self.undo_widget,True)
                debug('Sensitizing undo_widget',0)
            else:
                self.set_sensitive(self.undo_widget,False)
                debug('Desensizing undo_widget',0)
            if True in undoables:
                debug('Sensitizing redo_widget',0)
                self.set_sensitive(self.redo_widget,True)
            else:
                debug('Desensitizing redo widget',0)
                self.set_sensitive(self.redo_widget,False)
            if self[-1].reapplyable:
                debug('Sensitizing "reapply" widgets',0)
                self.set_sensitive(self.reapply_widget,True)
                if self[-1].reapply_name:
                    if type(self.reapply_widget)==gtk.MenuItem:
                        alabel = self.reapply_widget.get_children()[0]
                        alabel.set_text_with_mnemonic(self[-1].reapply_name)
                        alabel.set_use_markup(True)
        else:
            debug('Nothing to undo, desensitizing widgets',0)
            self.set_sensitive(self.redo_widget,False)
            self.set_sensitive(self.undo_widget,False)
            self.set_sensitive(self.reapply_widget,False)
            
    def append (self,obj):
        debug('Appending %s'%obj,0)
        list.append(self,obj)
        if obj.is_undo==False: # Is this necessary? Not sure...
            for h in self.action_hooks:
                h(self,obj,'perform')
        self.gui_update()

    def remove (self,obj):
        debug('Removing %s'%obj,0)        
        list.remove(self,obj)
        self.gui_update()

class MultipleUndoLists:
    """For tabbed interfaces and other places where it makes sense for one
    Action (menu item, etc.) to control multiple UndoLists (since presumably
    nobody wants to undo things they can't see)"""
    def __init__ (self, undo_widget, redo_widget, reapply_widget=None, signal='activate',
                  get_current_id=None):
        self.undo_widget = undo_widget
        self.redo_widget = redo_widget
        self.reapply_widget = reapply_widget
        self.signal = signal
        self.get_current_id = get_current_id
        self.histories = {}
        self.action_hooks = []
        if signal:
            if self.undo_widget: self.undo_widget.connect(signal,self.undo)
            if self.redo_widget: self.redo_widget.connect(signal,self.redo)
            if self.reapply_widget: self.reapply_widget.connect(signal,self.reapply)
        
        # attempts to implement the following programatically are failing me...
        # it feels awful to write each of these methods out here, but here goes...

    def add_action_hook (self, hook):
        self.action_hooks.append(hook)
        for h in self.get_all_histories(): h.add_action_hook(hook)
    def __add__ (self,*args,**kwargs): return self.get_history().__add__(*args,**kwargs)
    def __contains__ (self,*args,**kwargs): return self.get_history().__contains__(*args,**kwargs)
    def __delitem__ (self,*args,**kwargs): return self.get_history().__delitem__(*args,**kwargs)
    def __delslice__ (self,*args,**kwargs): return self.get_history().__delslice__(*args,**kwargs)
    def __doc__ (self,*args,**kwargs): return self.get_history().__doc__(*args,**kwargs)
    def __eq__ (self,*args,**kwargs): return self.get_history().__eq__(*args,**kwargs)
    def __ge__ (self,*args,**kwargs): return self.get_history().__ge__(*args,**kwargs)
    def __getitem__ (self,*args,**kwargs): return self.get_history().__getitem__(*args,**kwargs)
    def __getslice__ (self,*args,**kwargs): return self.get_history().__getslice__(*args,**kwargs)
    def __gt__ (self,*args,**kwargs): return self.get_history().__gt__(*args,**kwargs)
    def __hash__ (self,*args,**kwargs): return self.get_history().__hash__(*args,**kwargs)
    def __iadd__ (self,*args,**kwargs): return self.get_history().__iadd__(*args,**kwargs)
    def __imul__ (self,*args,**kwargs): return self.get_history().__imul__(*args,**kwargs)
    def __iter__ (self,*args,**kwargs): return self.get_history().__iter__(*args,**kwargs)
    def __le__ (self,*args,**kwargs): return self.get_history().__le__(*args,**kwargs)
    def __len__ (self,*args,**kwargs): return self.get_history().__len__(*args,**kwargs)
    def __lt__ (self,*args,**kwargs): return self.get_history().__lt__(*args,**kwargs)
    def __mul__ (self,*args,**kwargs): return self.get_history().__mul__(*args,**kwargs)
    def __ne__ (self,*args,**kwargs): return self.get_history().__ne__(*args,**kwargs)
    def __new__ (self,*args,**kwargs): return self.get_history().__new__(*args,**kwargs)
    def __reduce__ (self,*args,**kwargs): return self.get_history().__reduce__(*args,**kwargs)
    def __reduce_ex__ (self,*args,**kwargs): return self.get_history().__reduce_ex__(*args,**kwargs)
    def __repr__ (self,*args,**kwargs): return self.get_history().__repr__(*args,**kwargs)
    def __rmul__ (self,*args,**kwargs): return self.get_history().__rmul__(*args,**kwargs)
    def __setitem__ (self,*args,**kwargs): return self.get_history().__setitem__(*args,**kwargs)
    def __setslice__ (self,*args,**kwargs): return self.get_history().__setslice__(*args,**kwargs)
    def __str__ (self,*args,**kwargs): return self.get_history().__str__(*args,**kwargs)
    def append (self,*args,**kwargs): return self.get_history().append(*args,**kwargs)
    def count (self,*args,**kwargs): return self.get_history().count(*args,**kwargs)
    def extend (self,*args,**kwargs): return self.get_history().extend(*args,**kwargs)
    def index (self,*args,**kwargs): return self.get_history().index(*args,**kwargs)
    def insert (self,*args,**kwargs): return self.get_history().insert(*args,**kwargs)
    def pop (self,*args,**kwargs): return self.get_history().pop(*args,**kwargs)
    def remove (self,*args,**kwargs): return self.get_history().remove(*args,**kwargs)
    def reverse (self,*args,**kwargs): return self.get_history().reverse(*args,**kwargs)
    def sort (self,*args,**kwargs): return self.get_history().sort(*args,**kwargs)

    def redo (self,*args,**kwargs):
        return self.get_history().redo(*args,**kwargs)

    def undo (self,*args,**kwargs):
        return self.get_history().undo(*args,**kwargs)
    
    def reapply (self,*args,**kwargs): return self.get_history().reapply(*args,**kwargs)

    def get_all_histories (self): return self.histories.values()

    def get_history (self):
        hid=self.get_current_id()
        if self.histories.has_key(hid):
            #debug('Returning history %s for id %s'%([repr(i) for i in self.histories[hid]],hid),0)
            return self.histories[hid]
        else:
            #debug('Creating new history for id %s'%hid,0)
            self.histories[hid]=self.make_history()
            return self.histories[hid]

    def make_history (self):
        uhl = UndoHistoryList(self.undo_widget,self.redo_widget,None,None)
        for h in self.action_hooks: uhl.add_action_hook(h)
        return uhl

    def switch_context (self, hid):
        # set sensitivity for current context
        debug('switching context...',0)
        self.get_history().gui_update()
            
if __name__ == '__main__':
    #txt = raw_input('Text: ')
    #history = []
    #utc = UndoableTextChange(None,None,history,text=txt)
    #history.append(utc)
    #while txt:
    #    txt = raw_input('Text: ')
    #    history[-1].add_text(txt)
    import gtk
    w = gtk.Window()
    e = gtk.Entry()
    sb = gtk.SpinButton()
    adj = sb.get_adjustment()
    adj.upper=100
    adj.lower=-100
    adj.step_increment = 1
    adj.page_increment = 10
    tv = gtk.TextView()
    ub = gtk.Button(stock=gtk.STOCK_UNDO)
    rb = gtk.Button(stock=gtk.STOCK_REDO)
    sc = gtk.Button('show changes')
    vb = gtk.VBox()
    bb = gtk.HButtonBox()
    bb.add(ub)
    bb.add(rb)
    bb.add(sc)
    vb.add(bb)
    vb.add(e)
    vb.add(tv)
    vb.add(sb); sb.show()
    w.add(vb)
    uhl = UndoHistoryList(ub,rb,signal='clicked')
    UndoableTextView(tv,uhl)
    UndoableEntry(e,uhl)
    UndoableGenericWidget(sb,uhl)
    w.show_all()
    w.connect('delete-event',lambda *args:gtk.main_quit())
    def show_changes (*args):
        for c in uhl:
            if hasattr(c,'initial_text'):
                print c,' initial: ',c.initial_text,' current: ',c.text
            else:
                print c
    ub.connect('clicked',lambda *args: debug('Undo clicked!',0))
    sc.connect('clicked',show_changes)
    rb.connect('clicked',lambda *args: debug('Redo clicked!',0))    
    gtk.main()


