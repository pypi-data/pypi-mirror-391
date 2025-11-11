import unittest
from vdutils.tests.test_convaddr import TestClass as TestClassConvAddr
from vdutils.tests.test_cordate import TestClass as TestClassCordate
from vdutils.tests.test_genpnu import TestClass as TestClassGenPnu
from vdutils.tests.test_vid import TestClass as TestClassVid


def suite():
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    test_suite.addTest(test_loader.loadTestsFromTestCase(TestClassConvAddr))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestClassCordate))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestClassGenPnu))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestClassVid))

    return test_suite

def __run_test__():
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = suite()
    result = runner.run(test_suite)

# python -m unittest vdutils.tests.tests 
if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = suite()
    result = runner.run(test_suite)