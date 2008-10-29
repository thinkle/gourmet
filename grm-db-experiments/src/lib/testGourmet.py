import testImporters
import testExporters
import unittest

from testImporters import ImportTestCase
from testExporters import ExportTestCase

isuite = unittest.makeSuite(ImportTestCase)
esuite = unittest.makeSuite(ExportTestCase)

all = unittest.TestSuite([isuite,esuite])

unittest.main()
