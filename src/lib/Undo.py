from gdebug import debug
import gtk, difflib

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
                  is_undo=False):
        if not action_args: action_args=[]
        if not undo_action_args: undo_action_args=[]
        self.history=history
        self.action=action
        self.inverse_action=inverse
        self.get_reapply_action_args = get_reapply_action_args
        self.undo_action_args = undo_action_args
        self.get_reundo_action_args=get_reundo_action_args
        self.reapply_name = reapply_name
        self.reundo_name = reundo_name
        self.is_undo=is_undo
        if self.get_reapply_action_args:
            self.reapplyable = True
        else:
            self.reapplyable = False
        self.action_args = action_args

    def perform (self):
        print 'performing %s(*%s)'%(self.action,self.action_args)
        self.action(*self.action_args)
        self.history.append(self)

    def inverse (self):        
        u = UndoableObject(self.inverse_action, self.action, self.history,
                           action_args=self.undo_action_args,
                           undo_action_args=self.action_args,
                           get_reapply_action_args=self.get_reundo_action_args,
                           get_reundo_action_args=self.get_reapply_action_args,
                           is_undo=not self.is_undo)
        self.history.remove(self)
        u.perform()

    def reapply (self):
        if self.get_reapply_action_args:
            args,undoargs = self.get_reapply_action_args()
            print 'reapply args = ',args
            print 'reundo args = ',undoargs
            u = UndoableObject(self.action,self.inverse_action,self.history,
                               action_args=args,
                               undo_action_args=undoargs,
                               get_reapply_action_args=self.get_reapply_action_args,
                               reapply_name=self.reundo_name, reundo_name=self.reapply_name)
            print 'performing'
            u.perform()

class UndoableTextChange (UndoableObject):
    def __init__ (self, action, inverse, history, initial_text="",text=""):
        self.initial_text = initial_text
        self.text = text
        UndoableObject.__init__(self,action,inverse,history)
        
        if len(self.text) > len(self.initial_text):
            self.mode = 'add'
        elif len(self.text) < len(self.initial_text):
            self.mode = 'delete'
        self.change = self.find_change(self.text)

    def find_change (self, text2=None):
        if not text2: text2=self.text
        if not hasattr(self,'sm'):
            self.sm = difflib.SequenceMatcher(None,self.initial_text,text2)
        else:
            self.sm.set_seq2(text2)
        print 'sm.a=',self.sm.a,' sm.b=',self.sm.b
        blocks=self.sm.get_matching_blocks()
        print 'blocks=',blocks
        # we only are interested in similar blocks at different positions
        # (which tell us where the changes happened).
        ch_blocks = filter(lambda x: x[0] != x[1] and x[2] != 0, blocks)
        print 'ch_blocks=',ch_blocks
        if ch_blocks and len(ch_blocks)>1:
            raise "WTF"
        if ch_blocks:
            i,j,n = ch_blocks[0]
            change_length = j-i
            change_index = i
            print [change_index,change_length]
            return [change_index,change_length]
        else:
            if self.mode=='add':
                print [len(self.initial_text),len(text2)-len(self.initial_text)]
                return [len(self.initial_text),len(text2)-len(self.initial_text)]
            else:
                print [len(self.initial_text),len(self.initial_text)-len(text2)]
                return [len(self.initial_text),len(self.initial_text)-len(text2)]

    def add_text (self, new_text):
        new_change = self.find_change(new_text)
        print 'change=',self.change,'new_change = ',new_change
        if (new_change[0]==self.change[0] and # index of change is the same
            (new_change[0] > 0) == (self.change[0] > 0) and # sign is the same
            abs(new_change[1]) > abs(self.change[1])): # change is being added to
            self.text = new_text
            self.change = new_change
        else:
            # otherwise we create a new undo object for a new kind of change!
            print 'getting new history ','change=',self.change,' nc=',new_change
            print 'sign: ',(new_change[0] > 0) == (self.change[0] > 0)
            print 'index: ',(new_change[0]==self.change[0])
            print 'adding: ',(abs(new_change[1]) > abs(self.change[1]))
            self.history.append(UndoableTextChange(self.action,self.inverse_action,self.history,
                                                   initial_text=self.text, text=new_text)
                                )

class UndoHistoryList (list):
    """An UndoHistoryList."""
    def __init__ (self, undo_widget, redo_widget, reapply_widget=None, signal='activate'):
        self.undo_widget = undo_widget
        self.redo_widget = redo_widget
        self.reapply_widget = reapply_widget
        list.__init__(self)
        self.gui_update()
        if signal:
            self.undo_widget.connect(signal,self.undo)
            self.redo_widget.connect(signal,self.redo)
            self.reapply_widget.connect(signal,self.reapply)

    def undo (self, *args):
        index = -1
        try:
            while self[index].is_undo:
                index = index - 1
        except:
            debug('All %s available action are .is_undo=True'%len(self),0)
            raise
        print 'Undoing action at index: ',index
        self[index].inverse()

    def redo (self, *args):
        index = -1
        try:
            while not self[index].is_undo:
                index = index - 1
        except:
            debug('All %s available actions are is_undo=False'%len(self),0)
            raise
        self[index].inverse()

    def reapply (self, *args):
        debug('Reapplying',0)
        self[-1].reapply()

    def gui_update (self):
        if len(self) >= 1:
            undoables = [x.is_undo for x in self]
            if False in undoables:
                self.undo_widget.set_sensitive(True)
            else:
                self.undo_widget.set_sensitive(False)
            if True in undoables:
                self.redo_widget.set_sensitive(True)
            else:
                self.redo_widget.set_sensitive(False)
            if self[-1].reapplyable:
                self.reapply_widget.set_sensitive(True)
                if self[-1].reapply_name:
                    if type(self.reapply_widget)==gtk.MenuItem:
                        alabel = self.reapply_widget.get_children()[0]
                        alabel.set_text_with_mnemonic(self[-1].reapply_name)
                        alabel.set_use_markup(True)
        else:
            self.redo_widget.set_sensitive(False)
            self.undo_widget.set_sensitive(False)
            self.reapply_widget.set_sensitive(False)
            
    def append (self,obj):
        debug('Appending %s'%obj,0)
        list.append(self,obj)
        self.gui_update()

    def remove (self,obj):
        debug('Removing %s'%obj,0)        
        list.remove(self,obj)
        self.gui_update()
            
if __name__ == '__main__':
    txt = raw_input('Text: ')
    history = []
    utc = UndoableTextChange(None,None,history,text=txt)
    history.append(utc)
    while txt:
        txt = raw_input('Text: ')
        history[-1].add_text(txt)
        print 'History List: ',history
