import urllib, hashlib, os.path, os, StringIO
from gourmet.gdebug import debug
try:
    from PIL import Image
except ImportError:
    import Image

MAX_THUMBSIZE=10000000

# Keep track of uris we fetch...
fetched_uris = {}

def check_for_thumbnail (uri, type="large",reporthook=None):
    """Given a URI, return a file with a thumbnail of the image, or
    None if no thumbnail can be made."""
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
        fn = fetched_uris[uri]
    else:
        try:
            fn,headers = urllib.urlretrieve(uri,reporthook=reporthook)
            fetched_uris[uri]=fn
        except UnicodeError:
            try:
                fn,headers = urllib.urlretrieve(urllib.quote(uri),reporthook=reporthook)
            except IOError:
                return None
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
        from PIL import PngImagePlugin
    except ImportError:
        import PngImagePlugin
    pnginfo = PngImagePlugin.PngInfo()

    for k,v in info.items():
        pnginfo.add_text(k,v)
    im.save(thumbpath, pnginfo=pnginfo)
    # we must make all thumbnails permissions 700
    os.chmod(thumbpath,0700)
    return thumbpath

