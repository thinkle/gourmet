import Image, urllib, md5, os.path, os, StringIO

MAX_THUMBSIZE=10000000

def check_for_thumbnail (uri, type="large"):
        if not uri: return ""
        m = md5.md5(uri)
        name= os.path.join("~",".thumbnails",type,m.hexdigest() + ".png")
        name = os.path.expanduser(name)
	targetdir = os.path.split(name)[0]
	if not os.path.exists(targetdir):
	    os.makedirs(targetdir)
	if not os.path.isdir(targetdir):
	    import tempfile
	    name = tempfile.mktemp()
        try:
            fn,headers = urllib.urlretrieve(uri)
        except IOError:
            return None
        if not os.path.exists(name): return create_thumbnail(fn,name,uri,type)
        try:
            i=Image.open(name)
        except:
            return create_thumbnail(fn,name,uri,type)
        if not i.info.has_key('Thumb::MTime'):
            return create_thumbnail(fn,name,uri,type)
        mtime = i.info['Thumb::MTime']
        # hackish... we want what's after the // of the uri's
        fmtime = os.stat(fn)[8] # grab the modification time of this file
        if int(mtime) != int(fmtime):
            return create_thumbnail(fn,name,uri,type)
        return name

def create_thumbnail (path, thumbpath, uri, type="large"):
        """Create a thumbnail at path and return path"""
        mtime = os.stat(path)[8]
        size = os.path.getsize(path)
        if int(size) > MAX_THUMBSIZE:
            print 'File too large!'
            return None
        im = Image.open(path)
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
        os.chmod(thumbpath,700)
        return thumbpath
