import os, os.path
from gourmet.plugin import ImporterPlugin
import mcb_importer
import tempfile
import zipfile
from gettext import gettext as _

class MCBPlugin (ImporterPlugin):

    name = _('MCB File')
    patterns = ['*.mcb']
    mimetypes = ['application/zip','application/x-gzip','multipart/x-zip','multipart/x-gzip']

    def test_file (self, filename):
        return True

    def get_importer (self, filename):
        xmlfilename=''
        
        #Unzip in a temporary directory
        try:
            zf = zipfile.ZipFile(filename)
        except zipfile.BadZipfile:
            raise
        tempdir = tempfile.mkdtemp('mcb_zip')
        for name in zf.namelist():
            (dirname, filename) = os.path.split(name)
            fulldirpath = os.path.join(tempdir,dirname)
            #Create the images dir if not exists yet
            if not os.path.exists(fulldirpath):
                os.mkdir(fulldirpath, 0775)
            outfile = open(os.path.join(tempdir, name), 'wb')
            outfile.write(zf.read(name))
            outfile.close()
            #Get the path to the xml file to import it
            if filename.endswith(".xml"):
                xmlfilename = os.path.join(tempdir, filename)
        
        return mcb_importer.Converter(xmlfilename)


