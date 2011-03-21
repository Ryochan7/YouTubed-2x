import unittest
from youtubed2x_lib.tests.parsertest import ParseTest

if __name__ == "__main__":
    suite = unittest.TestLoader ().loadTestsFromTestCase (ParseTest)
    unittest.TextTestRunner (verbosity=2).run (suite)
