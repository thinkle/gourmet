import gourmet.recipeManager as recipeManager
import pickle, os

def load_recmanager ():
    return recipeManager.RecipeManager(**recipeManager.dbargs)

def fetch_all (rm,table_object):
    if hasattr(rm,'fetch_all'):
        return rm.fetch_all(table_object)
    else:
        return table_object

def get_tables (rm):
    descs = filter(lambda s: s.find('DESC')>-1,dir(rm))
    if hasattr(rm,'_setup_table'): setter_upper = rm._setup_table
    else: setter_upper = rm.setup_table
    tables = []
    print 'descs:',descs
    for desc in descs:
        d = getattr(rm,desc)
        table_object = setter_upper(*d)
        columns = [(c[0],c[1]) for c in d[1]]
        tables.append((d[0],table_object,columns))
    return tables

marker = "GOURMET_EXPORT_OUTPUT_" 

class SimpleExporter:

    # A flag we sincerely hope none of our data contains!
    def write_data (self, outfi):
        self.outfi = outfi
        rm = load_recmanager()
        tables = get_tables(rm)
        for name,table,columns in tables:
            print 'Writing',name
            self.write_table(rm,name,table,columns)
            print 'Done!'
        self.outfi.close()

    def write_table (self, rm, name, table_object, columns):
        self.outfi.write('\n'+marker+'START_TABLE: %s'%name)
        for row in fetch_all(rm,table_object):
            self.outfi.write('\n'+marker+'START_ROW')
            for c,typ in columns:
                self.outfi.write(
                    '\n'+marker+'START_FIELD: '+c+'\n'
                    )                
                self.outfi.write(
                    pickle.dumps(getattr(row,c))
                    )
                self.outfi.write(
                    '\n'+marker+'END_FIELD: '+c+'\n'
                    )
            self.outfi.write('\n'+marker+'END_ROW')
        self.outfi.write('\n'+marker+'END_TABLE: %s'%name)

def import_backup_file (rm, backup_file, prog=None):

    if type(backup_file)==str:
        fname = backup_file
        backup_file = open(backup_file,'r')
    else:
        fname = backup_file.name
    buf = ''
    cut_markers_at = len(marker)
    tot_size = os.stat(fname).st_size
    l = backup_file.readline()
    line_count = 0
    update_prog_each = 100
    while l:
        if l.find(marker)==0:
            action = l[cut_markers_at:]
            if action.find('START_TABLE: ')==0:
                table_name = action[len('START_TABLE: '):]
            elif action.find('START_ROW')==0:
                row = {}
            elif action.find('END_ROW')==0:
                rm.do_add(table_name,row)
            elif action.find('START_FIELD: ')==0:
                col = action[len('START_FIELD: '):]
                buf = ''
            elif action.find('END_FIELD: ')==0:
                try:
                    row[col]=pickle.loads(buf)
                except:
                    print 'Error unpickling',buf
        else:
            buf += l
        l = backup_file.readline()
        if prog:
            line_count += 1
            if line_count % update_prog_each == 0:
                pos = backup_file.tell()
                prog(float(pos)/tot_size)
    backup_file.close()
    rm.save()
                                    
import xml.dom

class XmlExporter: #Memory hog

    def __init__ (self):
        impl = xml.dom.getDOMImplementation()
        doctype = impl.createDocumentType(
            'gourmet_data_dump',
            None,None)
        self.xmlDoc = impl.createDocument(None,'gourmet_data_dump',doctype)
        self.top = self.xmlDoc.documentElement

    def write_data (self, fi):
        rm = load_recmanager()
        tables = get_tables(rm)
        for name,table,columns in tables:
            self.write_table(rm,name,table,columns)
        self.xmlDoc.writexml(fi,newl='\n',addindent='\t',encoding='UTF-8')
        
    def write_table (self, rm, name, table_object, columns):
        """Table object is a database reference to a table.
        Columns are tuples with column names and types
        """
        print 'writing ',name
        row_el = self.xmlDoc.createElement(name)
        for row in fetch_all(rm,table_object):
            for c,typ in columns:
                col_el = self.xmlDoc.createElement(c)
                self.add_content(
                    col_el,
                    getattr(row,c),
                    typ
                    )
                row_el.appendChild(col_el)
        self.top.appendChild(row_el)
        print 'Done!'

    def add_content (self,col_el,
                     content,
                     typ):
        if typ in ['binary','data','bin']:
            cdata = self.xmlDoc.createCDATASection(base64.b64encode(content))
            col_el.appendChild(cdata)
        else:
            textNode = self.xmlDoc.createTextNode(xml.sax.saxutils.escape(str(content)))
            col_el.appendChild(textNode)



if __name__ == '__main__':
    import tempfile
#     print 'Dump file...'
#     e = SimpleExporter()
#     ofi = tempfile.mktemp('.gourmet_dump')
#     print 'Dumping to ',ofi
#     outfi = file(ofi,'w')
#     e.write_data(outfi)
#     outfi.close()
#     print 'Load file from',ofi,'...'
    recipeManager.dbargs['file']=tempfile.mktemp('.db')
    rm = recipeManager.RecipeManager(**recipeManager.dbargs)
    ofi = '/tmp/tmpCB4E9M.gourmet_dump'
    import gourmet.dialog_extras as de
    import gtk
    pd = de.ProgressDialog()
    pd.show()
    def prog (n):
        pd.set_progress(n,'Importing old data into new database.')
        while gtk.events_pending(): gtk.main_iteration()
    import_backup_file(rm,ofi,prog)
    print 'Done!'
    pd.hide()
    while gtk.events_pending(): gtk.main_iteration()
    print 'Loaded DB in rm'
    
