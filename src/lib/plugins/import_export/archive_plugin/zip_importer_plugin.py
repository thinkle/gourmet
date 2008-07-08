from gourmet.plugin import ImporterPlugin
from gourmet.importers.importManager import ImportFileList
from zip_readers import archive_to_filelist

class ArchiveImporterPlugin (ImporterPlugin):

    get_source = False
    name = 'Archive (zip, tarball.)'
    patterns = ['*.%s'%suffix for suffix in
                ['zip',
                 'tar','tar.gz','tgz','tar.bz2',
                 'gzip','gz']
                ]
    mimetypes = ['application/tar','application/zip','application/gzip']

    def test_file (self, filename):
        '''Given a filename, test whether the file is of this type.'''
        # Lame lame test...
        return ( filename.lower().split('.')[-1] in self.patterns )

    def get_importer (self, filename):
        flist = archive_to_filelist(filename)
        ifl = ImportFileList(flist)
        raise ifl
