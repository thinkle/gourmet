#!/usr/bin/env python
# Copyright (c) 2004, 2005, 2006, 2007 Tom Hinkle
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import glob
import os
import os.path
import signal
import sys
import unittest
import tempfile
from stat import ST_MTIME

import test_exportManager
import test_importer
import test_importManager
import test_interactive_importer
import test_convert
import test_db

signal.signal(signal.SIGINT, signal.SIG_DFL)


def maybe_intltool (fname):
    """Check whether the file at fname has been updated since intltool-merge was last used on it. If it has, then use
    intltool-merge to update the output file.
    """
    to_name = fname[:-3]
    if (
        (not os.path.exists(to_name))
        or
        os.stat(to_name)[ST_MTIME] < os.stat(fname)[ST_MTIME]
        ):
        os.system('intltool-merge -d i18n/ %s %s'%(fname, to_name))

for desktop_file in glob.glob('../plugins/*plugin.in') + glob.glob('../plugins/*/*plugin.in'):
    maybe_intltool(desktop_file)

tmpfile = tempfile.mktemp()  # TODO: replace deprecated mktemp()
sys.argv.append('--gourmet-directory=%s' % tmpfile)
sys.argv = sys.argv[:-1]

def suite():
    ts = unittest.TestSuite()
    for module in [test_importManager,
                   test_exportManager,
                   test_interactive_importer,
                   test_importer,
                   test_convert]:
        ts.addTest(unittest.defaultTestLoader.loadTestsFromModule(module))

    # The DB tests need to be run last as they kill all plugins
    ts.addTest(test_db.suite)
    return ts


if __name__ == '__main__':
    # unittest.main()
    runner = unittest.TextTestRunner(failfast=True)
    ts = suite()
    print "About to execute {} test cases".format(ts.countTestCases())
    tr = runner.run(ts)

    if tr.wasSuccessful():
        print "All {} tests completed successfully!".format(tr.testsRun)
    else:
        print 'Uh oh...'
        print "We had {} failures in {} tests".format(len(tr.failures), tr.testsRun)
        for er, tb in tr.failures:
            print '---'
            print "{}:{}".format(er, tb)
            print '---'
        if tr.errors:
            print 'We had {} errors in {} tests'. format(len(tr.errors), tr.testsRun)
            for er, tb in tr.errors:
                print '---'
                print "{}:{}".format(er, tb)
                print '---'
