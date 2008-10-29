import Image, urllib, md5, os.path, os, StringIO
from gourmet.gdebug import debug

MAX_THUMBSIZE=10000000

# Keep track of uris we fetch...
fetched_uris = {}

def check_for_thumbnail (uri, type="large",reporthook=None):
    """Given a URI, return a file with a thumbnail of the image, or
    None if no thumbnail can be made."""
    print 'CHECK FOR THUMBNAIL',uri
    if not uri:
        return ""
    m = md5.md5(uri)
    name= os.path.join("~",".thumbnails",type,m.hexdigest() + ".png")    
    name = os.path.expanduser(name)
    targetdir = os.path.split(name)[0]
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    if not os.path.isdir(targetdir):
        import tempfile
        name = tempfile.mktemp()
    if fetched_uris.has_key(uri) and os.path.exists(fetched_uris[uri]):
        print 'USE PRE-FETCHED IMAGE'
        fn = fetched_uris[uri]
    else:
        try:
            print 'Getting',uri,reporthook
            fn,headers = urllib.urlretrieve(uri,reporthook=reporthook)
            print 'Got!',fn,headers
            fetched_uris[uri]=fn
        except IOError:
            return None
    if not os.path.exists(name):
        return create_thumbnail(fn,name,uri,type)
    try:
        i=Image.open(name)
    except:
        return create_thumbnail(fn,name,uri,type)
    if not i.info.has_key('Thumb::MTime'):
        debug('Thumbnail has no time registered, creating a new one.',1)
        return create_thumbnail(fn,name,uri,type)
    mtime = i.info['Thumb::MTime']
    # hackish... we want what's after the // of the uri's
    fmtime = os.stat(fn)[8] # grab the modification time of this file
    if int(mtime) != int(fmtime):
        debug('Thumbnail is older than file, updating thumbnail',1)
        return create_thumbnail(fn,name,uri,type)
    # make sure permissions are correct
    # since previous Gourmet's may have mucked them up :)
    os.chmod(name,0700)
    return name

def create_thumbnail (path, thumbpath, uri, type="large"):
    """Create a thumbnail at path and return path"""
    mtime = os.stat(path)[8]
    size = os.path.getsize(path)
    if int(size) > MAX_THUMBSIZE:
        debug('File too large!',0)
        return None
    try:
        im = Image.open(path)
    except:
        return None
    w,h = im.size
    if type=='large':
        geo = (256,256)
    else: geo = (128,128)
    im.thumbnail(geo)
    # set thumbnail attributes
    info={}
    info['Thumb::MTime']=str(mtime)
    info['Thumb::Image::Width']=str(w)
    info['Thumb::Image::Height'] =str(h)
    info['Software']='Gourmet Recipe Manager'
    info['URI']=str(uri)
    # now we must create our image guy
    try:
        import PngImagePlugin
        pnginfo = PngImagePlugin.PngInfo()
        use_our_png=False
    except AttributeError:
        from PngImagePluginUpToDate import _save, PngInfo
        pnginfo = PngInfo()
        # in this case, we'd better make sure our image is a PNG
        # so we can call our own local stuff more easily and add
        # key info
        s = StringIO.StringIO()
        im.save(s,'PNG')
        s.seek(0)
        im = Image.open(s)
        use_our_png=True
    for k,v in info.items():
        pnginfo.add_text(k,v)
    if use_our_png:
        _save(im,open(thumbpath,'wb'),thumbpath,pnginfo=pnginfo)
    else:
        im.save(thumbpath, pnginfo=pnginfo)
    # we must make all thumbnails permissions 700
    os.chmod(thumbpath,0700)
    return thumbpath
    
    
import os
import sys
import re
import imghdr
from getopt import getopt
from StringIO import StringIO
from PIL import Image # Require PIL module.

class ThumbnailGenerator:
    "Thumbnail image generator."
    default_geom = (100, 100)
    geomfmt = re.compile('(?P<W>\d+)x(?P<H>\d+)')

    def __init__(self):
        self.limit_geom = self.default_geom
        self.outd = '.'
        self.suf = '-thumb'

    def setoutdir(self, outd):
        self.outd = outd

    def setsuffix(self, suf):
        self.suf = suf

    def setbasesize(self, geom):
        matched = self.geomfmt.match(geom)
        if not matched:
            raise ValueError, 'Geometory format is not "XxY"'
        self.limit_geom = (int(matched.group('W')), int(matched.group('H')))

    def generate(self, fn, fp=None):
        "Generate thumbnail."
        im = Image.open(fn)
        im.thumbnail(self.limit_geom)
        base, ext = os.path.splitext(fn)
        if fp: im.save(fp, imghdr.what(fn))
        else: im.save(os.path.join(self.outd, '%s%s%s'%(base, self.suf, ext)))
        return im

    def raw_generate(self, fn):
        "Generate thumbnail (retruns rawdata)"
        im = Image.open(fn)
        im.thumbnail(self.limit_geom)
        buf = StringIO()
        im.save(buf, imghdr.what(fn))
        return buf.getvalue()

def __usage():
    print >>sys.stderr, 'usage: %s [options] imagefile ...' % sys.argv[0]

def __help():
    __usage()
    print '''options:
    -b XxY       base thumbnail size
    -h           print this usage
    -o directory output directory
    -s suffix    thumbnail suffix'''

def __main():
    optdic = {}
    arglist = []
    optlist = []
    tmp = sys.argv[1:]
    while 1:
        opts, tmp = getopt(tmp, 'b:ho:s:')
        if opts: optlist += opts
        if not tmp: break
        arglist.append(tmp[0])
        tmp = tmp[1:]

    # Examine options and filenames.
    if optlist:
        for key, val in optlist:
            if key == '-h':
                __help()
                return
            if optdic.has_key(key):
                raise ValueError, '%s option duplicated' % key
            optdic[key] = val
    if not arglist:
        __usage()
        return

    generator = ThumbnailGenerator()
    if optdic.has_key('-b'): generator.setbasesize(optdic['-b'])
    if optdic.has_key('-o'): generator.setoutdir(optdic['-o'])
    if optdic.has_key('-s'): generator.setsuffix(optdic['-s'])

    # Generate thumbnails.
    for fn in arglist:
        generator.generate(fn)

