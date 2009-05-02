import Image, urllib, hashlib, os.path, os, StringIO
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
    m = hashlib.md5(uri)
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

