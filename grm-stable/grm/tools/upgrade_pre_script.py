import sys, os.path

def dump_old_data ():

    try:
        import gourmet
    except ImportError:
        sys.path.append(os.path.join(os.path.sep+'usr','share'))
        try:
            import gourmet
        except:
            print 'No previous gourmet installation found.'
            return

    import gourmet.recipeManager as recipeManager # The *old* Gourmet
    
    # We need to get our upgradeHandler from the *new* Gourmet...
    gourmet_base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
    sys.path.append(os.path.join(gourmet_base_path,
                                 'src',
                                 'lib')
                    )
    print 'just added',sys.path[-1]
    import glob
    import upgradeHandler

    #for mkdata in glob.glob('/home/*/.gourmet/recipes.mk'):
    for mkdata in ['/home/tom/Projects/grm-db-experiments/src/lib/exporters/reference_setup/recipes.mk']:
        print 'Dumping old recipe database',mkdata,'...'
        stat = os.stat(mkdata)
        uid,gid = stat.st_uid,stat.st_gid
        recipeManager.dbargs['file']=mkdata
        try:
            recipeManager.RecipeManager(**recipeManager.dbargs)
        except:
            print 'Unable to load old database in ',mkdata
            continue
        se = upgradeHandler.SimpleExporter()
        ofi = os.path.join(os.path.split(mkdata)[0],
                     'GOURMET_DATA_DUMP')
        se.write_data(file(ofi,'w'))
        del se
        del recipeManager
        os.chown(ofi,uid,gid)
        os.chown(mkdata,uid,gid)
        print 'Saved data in backup file ',ofi
        print 'Data will be imported on first start of the new Gourmet by the appropriate user.'

if __name__ == '__main__':
    try:
        dump_old_data()        
    except:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
