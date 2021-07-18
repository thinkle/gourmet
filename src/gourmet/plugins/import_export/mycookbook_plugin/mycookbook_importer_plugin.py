import os
import os.path
import tempfile
import zipfile

from lxml import etree

from gourmet.i18n import _
from gourmet.plugin import ImporterPlugin

from . import mycookbook_importer


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
            if not filename:
                continue
            fulldirpath = os.path.join(tempdir,dirname)
            #Create the images dir if not exists yet
            if not os.path.exists(fulldirpath):
                os.mkdir(fulldirpath, 0o775)
            outfile = open(os.path.join(tempdir, name), 'wb')
            outfile.write(zf.read(name))
            outfile.close()
            #Get the path to the xml file to import it
            if filename.endswith(".xml"):
                xmlfilename = os.path.join(tempdir, filename)

                #fix the xml file
                parser = etree.XMLParser(recover=True)
                tree = etree.parse(xmlfilename, parser)
                fixedxmlfilename = xmlfilename+'fixed'
                with open(fixedxmlfilename, 'wb') as fout:
                    tree.write(fout, xml_declaration=True,
                               encoding='utf-8', pretty_print=True)

        zf.close()

        return mycookbook_importer.Converter(fixedxmlfilename)
