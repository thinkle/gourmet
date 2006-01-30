import sys, os.path
try:
    import gourmet
except ImportError:
    sys.path.append(os.path.join('usr','share'))
    try:
        import gourmet
    except:
        print 'No previous gourmet installation found.'
        sys.exit()
    

gourmet_base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
sys.path.append(os.path.join(gourmet_base_path,
                             'src',
                             'lib')
                )

import glob
import recipeManager
import upgradeHandler

for mkdata in glob.glob('/home/*/.gourmet/recipes.mk'):
    stat = os.stat(mkdata)
    uid,gid = stat.st_uid,stat.st_gid
    recipeManager.dbargs['file']=mkdata
    recipeManager.RecipeManager(**recipeManager.dbargs)
    se = upgradeHander.SimpleExporter()
    ofi = os.path.join(os.path.split(mkdata)[0],
                 'GOURMET_DATA_DUMP')
    se.write_data(file(ofi,'w'))
    del se
    del recipeManager
    os.chown(ofi,uid,gid)
    os.chown(mkdata,uid,gid)
