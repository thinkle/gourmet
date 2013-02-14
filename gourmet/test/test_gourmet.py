#!/usr/bin/env python
# Copyright (c) 2004, 2005, 2006, 2007 Tom Hinkle
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

#import sys
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys, os, os.path, glob
from stat import ST_MTIME

def maybe_intltool (fname):
    '''Check whether the file at fname has been updated since
    intltool-merge was last used on it. If it has, then use
    intltool-merge to update the output file.

    '''
    to_name = fname[:-3]
    if (
        (not os.path.exists(to_name))
        or
        os.stat(to_name)[ST_MTIME] < os.stat(fname)[ST_MTIME]
        ):
        os.system('intltool-merge -d i18n/ %s %s'%(fname, to_name))

for desktop_file in glob.glob('lib/plugins/*plugin.in') + glob.glob('lib/plugins/*/*plugin.in'):
    maybe_intltool(desktop_file)

if os.path.exists('foo'):
    os.remove('foo/gourmet')
    os.rmdir('foo')

os.mkdir('foo')
os.symlink(os.path.abspath('lib'),'foo/gourmet')
sys.path = [os.path.abspath('foo')] + sys.path
sys.argv.append('--gourmet-directory=%s'%os.path.abspath('/tmp/asdfqwer122'))
sys.argv.append('--data-directory=%s'%os.path.abspath('../data/'))
sys.argv.append('--glade-directory=%s'%os.path.abspath('../glade/'))
sys.argv.append('--image-directory=%s'%os.path.abspath('../images/'))
import gourmet.gglobals
sys.argv = sys.argv[:-4]
import gourmet.backends.test_db

#import gourmet.test_reccard
import gourmet.importers.test_interactive_importer
import gourmet.importers.test_importer
import gourmet.importers.test_importManager
import gourmet.test_convert
import gourmet.exporters.test_exportManager
import unittest
testsuite = unittest.TestSuite()
for module in [
    gourmet.importers.test_importManager,    
    gourmet.exporters.test_exportManager,
    gourmet.importers.test_interactive_importer,
    gourmet.importers.test_importer,
    gourmet.test_convert,
    ]:
    testsuite.addTest(
        unittest.defaultTestLoader.loadTestsFromModule(
            module
            )
        )
testsuite.addTest(gourmet.backends.test_db.suite)
tr = unittest.TestResult()
testsuite.run(tr)
if tr.wasSuccessful():
    print 'All ',tr.testsRun,'tests completed successfully!'
else:
    print 'Uh oh...'
    print 'We had ',len(tr.failures),'failures in ',tr.testsRun,'tests'
    for er,tb in tr.failures:
        print '---'
        print er,':',tb
        print '---'
    if tr.errors:
        print 'We had ',len(tr.errors),' errors in',tr.testsRun,'tests'
        for er,tb in tr.errors:
            print '---'
            print er,':',tb
            print '---'
