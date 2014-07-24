import gtk
from sqlalchemy.types import Boolean, Integer, String, Text, Float, LargeBinary
from sqlalchemy import inspect

sqlalchemy_type_map = {Boolean: bool,
                       Integer: int,
                       String: str,
                       Text: str,
                       Float: float,
                       LargeBinary: object
                       }

def map_sqlalchemy_type(saType):
    for sa, py in sqlalchemy_type_map.iteritems():
        if isinstance(saType, sa):
            return py

class SqlaModel(gtk.GenericTreeModel):

    def __init__(self, sqla_type, records = list()):
        gtk.GenericTreeModel.__init__(self)
        self.column_types = inspect(sqla_type).all_orm_descriptors
        self.column_types = [object] + list(self.column_types)
        self.column_names = [i.name if hasattr(i, 'name') else
                             i.__name__ if hasattr(i, '__name__') else
                             'unnamed'
                             for i in self.column_types]
        self.records = records
        #self.emit('page-changed')

    def get_column_names(self):
        return self.column_names

    def get_column_index(self, name):
        return self.column_names.index(name)

    def on_get_flags(self):
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return len(self.column_types)

    def on_get_column_type(self, index):
        if index == 0:
            return self.column_types[0]
        if hasattr(self.column_types[index], 'type') and \
           map_sqlalchemy_type(self.column_types[index].type):
            return map_sqlalchemy_type(self.column_types[index].type)
        else:
            return str

    # alternatively, we could use the recipe id
    def on_get_iter(self, path):
        if len(self.records) == 0:
            return None
        return self.records[path[0]]

    def on_get_path(self, rowref):
        return self.records.index(rowref)

    def on_get_value(self, rowref, column):
        if column == 0:
            return rowref
        return getattr(rowref, self.column_names[column])

    def on_iter_next(self, rowref):
        try:
            i = self.records.index(rowref)+1
            return self.records[i]
        except IndexError:
            return None

    def on_iter_children(self, rowref):
        if rowref:
            return None
        return self.records[0]

    def on_iter_has_child(self, rowref):
        return False

    def on_iter_n_children(self, rowref):
        if rowref:
            return 0
        return len(self.records)

    def on_iter_nth_child(self, rowref, n):
        if rowref:
            return None
        try:
            return self.records[n]
        except IndexError:
            return None

    def on_iter_parent(self, child):
        return None

    def update_recipe (self, recipe):
        pass