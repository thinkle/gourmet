#!/usr/bin/env python
# Copyright (c) 2004, 2005, 2006, 2007 Tom Hinkle
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import glob
import os
import os.path
#import sys
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys
import unittest
from stat import ST_MTIME

import gourmet.tests.test_convert
import gourmet.tests.test_db
import gourmet.tests.test_exportManager
import gourmet.tests.test_importManager
import gourmet.tests.test_interactive_importer


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

for desktop_file in glob.glob('../plugins/*plugin.in') + glob.glob('../plugins/*/*plugin.in'):
    maybe_intltool(desktop_file)

sys.path = ['../../'] + sys.path
sys.argv.append('--gourmet-directory=%s'%os.tempnam())
# No longer necessary
#sys.argv.append('--data-directory=%s'%os.path.abspath('../data/'))
#sys.argv.append('--glade-directory=%s'%os.path.abspath('../glade/'))
#sys.argv.append('--image-directory=%s'%os.path.abspath('../images/'))
# End no longer necessary stuff
sys.argv = sys.argv[:-1]

testsuite = unittest.TestSuite()
for module in [

    gourmet.tests.test_importManager,
    gourmet.tests.test_exportManager,
    gourmet.tests.test_interactive_importer,
    gourmet.tests.test_importer,
    gourmet.tests.test_convert,
    ]:
    testsuite.addTest(
        unittest.defaultTestLoader.loadTestsFromModule(
            module
            )
        )
# We have to run the DB tests last as they kill all plugins
testsuite.addTest(gourmet.tests.test_db.suite)

tr = unittest.TestResult()
testsuite.run(tr)
if tr.wasSuccessful():
    print('All ',tr.testsRun,'tests completed successfully!')
else:
    print('Uh oh...')
    print('We had ',len(tr.failures),'failures in ',tr.testsRun,'tests')
    for er,tb in tr.failures:
        print('---')
        print(er,':',tb)
        print('---')
    if tr.errors:
        print('We had ',len(tr.errors),' errors in',tr.testsRun,'tests')
        for er,tb in tr.errors:
            print('---')
            print(er,':',tb)
            print('---')
