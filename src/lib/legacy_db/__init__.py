import glob, os

# We dump legacy databases by default into data files that Gourmet
# will automatically import. This isn't too sophisticated at the
# moment.
import db_085.rmetakit, db_08.rmetakit

legacy_modules = {'.mk':[db_085.rmetakit,db_08.rmetakit],
                  #[__import__(f,{},['rmetakit']) for f in ['db_085.rmetakit','db_08.rmetakit']],
                  #'.db':[] # No legacy SQL support at present...
                  }

def load_db (file, mod):
    return mod.RecData(file=file)    

def get_file_for_ending (dir, ending):
    """Look for legacy DBs sitting in dir and dump them.

    This could be more complicated in the future...."""
    potential_dbs = glob.glob(os.path.join(dir,'*%s'%ending))
    if not potential_dbs:
        print 'no potential'
        return
    elif len(potential_dbs)>1:
        latest = 0
        my_pd = None
        for pd in potential_dbs:
            modtime = os.path.getmtime(os.path.abspath(pd))
            if modtime > latest:
                latest = modtime
                pd = my_pd
        return my_pd
    else:
        return potential_dbs[0]
                        
def get_legacy_db_in_directory (dir):
    for ending in legacy_modules:                
        # Now we have a potential database...
        fi = get_file_for_ending(dir,ending)
        if fi:
            print 'we have ',fi,'and ',legacy_modules[ending]
            mods = legacy_modules[ending]
            for m in mods:
                try:
                    rm = load_db(fi,m)
                except:
                    print 'Failed to load for ',m
                    import traceback; traceback.print_exc()
                else:
                    return rm,fi
                    
def backup_legacy_data (dir,progress_dialog=None,set_prog=None):
    import gourmet.upgradeHandler
    print 'Looking in ',dir
    result = get_legacy_db_in_directory(dir)
    if result:
        rm,finame = result
        if progress_dialog: progress_dialog.show()
        se = gourmet.upgradeHandler.SimpleExporter(set_prog)
        ofi = file(os.path.join(dir,'GOURMET_DATA_DUMP'),'w')
        se.write_data(ofi,
                      rm)
        ofi.close()
        del rm
    
if __name__ == '__main__':
    backup_dir = '/home/tom/Projects/grm-db-experiments/src/tests/085_setup/'
    print 'Backing up data in',backup_dir
    backup_legacy_data(backup_dir)
    print 'Backed up data'
    
