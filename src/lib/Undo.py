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
                  is_undo=False):
        if not action_args: action_args=[]
        if not undo_action_args: undo_action_args=[]
        self.history=history
        self.action=action
        self.inverse_action=inverse
        self.get_reapply_action_args = get_reapply_action_args
        self.undo_action_args = undo_action_args
        self.get_reundo_action_args=get_reundo_action_args
        self.is_undo=is_undo
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
                           is_undo=not self.is_undo)
        self.history.remove(self)
        u.perform()

    def reapply (self):
        if self.get_reapply_action_args:
            args = self.action(*self.get_reapply_action_args())
            u = UndoableObject(self.action,self.inverse,args,self.get_reapply_action_args)
            u.perform()

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
        while self[index].is_undo:
            index = index - 1
        self[index].inverse()

    def redo (self, *args):
        index = -1
        while not self[index].is_undo:
            index = index - 1
        self[index].inverse()

    def reapply (self, *args):
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
        else:
            self.redo_widget.set_sensitive(False)
            self.undo_widget.set_sensitive(False)
            self.reapply_widget.set_sensitive(False)
            
    def append (self,obj):
        list.append(self,obj)
        self.gui_update()

    def remove (self,obj):
        list.remove(self,obj)
        self.gui_update()
            
