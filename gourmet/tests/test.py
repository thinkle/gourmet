# Convenience for importing gourmet stuff from our local directory...
import sys, os, os.path, glob
if os.path.exists('foo'):
    os.remove('foo/gourmet')
    os.rmdir('foo')

os.mkdir('foo')
os.symlink(os.path.abspath('../lib'),'foo/gourmet')
sys.path = [os.path.abspath('foo')] + sys.path + [os.path.abspath('foo/gourmet')]
sys.argv.append('--data-directory=%s'%os.path.abspath('../../data/'))
sys.argv.append('--glade-directory=%s'%os.path.abspath('../../glade/'))
sys.argv.append('--image-directory=%s'%os.path.abspath('../../images/'))
base_path = os.path.split(__file__)[0]

def remove_sysargs ():
    sys.argv.remove('--data-directory=%s'%os.path.abspath('../../data/'))
    sys.argv.remove('--glade-directory=%s'%os.path.abspath('../../glade/'))
    sys.argv.remove('--image-directory=%s'%os.path.abspath('../../images/'))


def profile (f):
    import profile, tempfile,os.path
    import hotshot, hotshot.stats
    #profi = os.path.join(tempfile.tempdir,'GOURMET_PROFILE')
    prof = hotshot.Profile(os.path.join(tempfile.tempdir,'GOURMET_HOTSHOT_PROFILE'))
    prof.runcall(f)
    stats = hotshot.stats.load(os.path.join(tempfile.tempdir,'GOURMET_HOTSHOT_PROFILE'))
    stats.strip_dirs()
    stats.sort_stats('cumulative','calls').print_stats()

