import zipfile, StringIO, tempfile, os, os.path
import tarfile, gzip
from gourmet.importers.webextras import read_socket_w_progress
from gourmet.importers.importer import add_to_fn
from gourmet.gdebug import *

# This is simply a convenience. We read a zipfile, and then hand out a
# list of files which we can use to import from using our other
# importers.
#
# We will also conveniently handle tarballs

def archive_to_filelist (fi, progress=None, name='zipfile'):
    if tarfile.is_tarfile(fi):
        debug('tarball_to_filelist',0)
        return tarball_to_filelist(fi,progress,name)
    else:
        try:
            ifi = gzip.open(fi,'r')
            # we move forward a byte to trigger an error if this
            # is not a gzip file (hackish, I know)
            ifi.seek(1)
            ifi.seek(0)
            ifi.name = os.path.splitext(fi)[0]
            debug('returning ungzipped file %s'%ifi,0)
            return [ifi]
        except IOError:
            return zipfile_to_filelist(fi,progress,name)

def zipfile_to_filelist (fi, progress=None, name="zipfile"):
    """Take our zipfile and return a list of files.

    We're quite liberal in what we allow fi to be.  If fi is a string,
    we open it as a filename.  if fi is a file object, we handle it,
    even if it's an icky file object that needs some messy
    manipulation to work (i.e. a urllib.urlopen() object).
    """
    # handle filename
    if type(fi)==str: fi = open(fi,'rb')
    # handle unseekable
    elif not hasattr(fi,'seek'):
        # slurp up the file into a StringIO so we can seek within it
        debug('Slurping up file into StringIO',1)
        tmpfi=StringIO.StringIO(read_socket_w_progress(fi,progress,_('Loading zip archive')))
        fi.close()
        fi = tmpfi
    # and now we actually do our work...
    debug('ZipFile(fi)',1)
    zf=zipfile.ZipFile(fi)
    flist=[]
    fbase = os.path.join(tempfile.tempdir, name)
    while os.path.exists(fbase):
        fbase=add_to_fn(fbase)
    os.mkdir(fbase)
    nlist = zf.namelist()
    totlen=float(len(nlist))
    for i,n in enumerate(nlist):
        debug('Unzipping item %s'%i,1)
        if progress: progress(float(i)/totlen,_("Unzipping zip archive"))
        fn = os.path.join(fbase,n)
        ifi=open(fn,'wb')
        ifi.write(zf.read(n))
        ifi.close()
        flist.append(fn)
    zf.close()
    debug('zipfile returning filelist %s'%flist,1)
    return flist

def tarball_to_filelist (fi, progress=None, name="zipfile"):
    tb = tarfile.TarFile.open(fi,mode='r')
    fi_info = tb.next()
    filist = []
    while fi_info:
        fi = tb.extractfile(fi_info)
        if fi: filist.append(fi)
        fi_info = tb.next()
    debug('tarball_to_filelist returning %s'%filist,0)
    return filist
        
