import gettext, os, os.path

if os.name == 'posix':
    # somewhat hackish -- we assume USR ==
    #usr_share = os.path.join(os.path.split(datad)[0])
    #print 'trying in %s'%usr_share
    #if not os.path.exists(os.path.join(usr,'locale')):
    #    usr_share = os.path.join('/usr','share')
    # try /usr/share/
    import glob
    locale_dirs = [
        os.path.join(os.path.sep,'usr','share','locale'),
        os.path.join(os.path.sep,'usr','local','share','locale'),
        'locale',
        os.path.join(os.path.sep,'opt','locale')
        ]
    DIR = None
    for l in locale_dirs:
        if glob.glob(os.path.join(l,'*','*','gourmet.mo')):
            DIR = l
            break

# FOOLISHLY REPEATED CODE -- DUPLICATED IN GGLOBALS.PY
elif os.name == 'nt': 
    #datad = os.path.join('Program Files','Gourmet Recipe Manager','data')
    # We're going to look in a number of places, starting with our current location
    if os.path.exists('app.glade'):
        datad = ''
    elif os.path.exists(os.path.join('data','app.glade')):
        datad = 'data'
    elif os.path.exists(os.path.join('..','data','app.glade')):
        datad = os.path.join('..','data')
    else:
        pybase = os.path.split(__file__)[0]
        if os.path.exists(os.path.join(pybase,'app.glade')):
            datad = pybase
        elif os.path.exists(os.path.join(pybase,'data','app.glade')):
            # look in a "data" directory directly above the directory we are in
            datad = os.path.join(pybase,'data')
        else: # otherwise, backup a directory and look there...
            pybase = os.path.split(pybase)[0]
            if os.path.exists(os.path.join(pybase,'data','app.glade')):
                datad = os.path.join(pybase,'data')
            else:
                # assume we are in Python\Lib\site-packages\gourmet\
                # back up four direcotires and add gourmet\data\
                pybase = os.path.split(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])[0]
                gourmetd = os.path.join(pybase,'gourmet')
                datad = os.path.join(gourmetd,'data')

    pth = datad.split(os.path.sep)
    pth = pth[:-1] # strip off data
    datad = os.path.sep.join(pth)

    DIR = os.path.join(datad,'i18n')

gettext.bindtextdomain('gourmet',DIR)
gettext.textdomain('gourmet')
gettext.install('gourmet',DIR,unicode=1)

import locale, os
try:
    if os.name == 'posix':
        locale.setlocale(locale.LC_ALL,'')

    # Windows locales are named differently, e.g. German_Austria instead of de_AT
    # Fortunately, we can find the POSIX-like type using a different method
    # After that, we set the LC_ALL environment variable for use with gettext.
    elif os.name == 'nt': 
        import win32api
        locid = win32api.GetUserDefaultLangID()
        loc = locale.windows_locale[locid]
        os.environ["LC_ALL"] = loc

except locale.Error:
    print 'Unable to properly set locale %s.%s'%(locale.getdefaultlocale())
