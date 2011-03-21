import unittest
from youtubed2x_lib.tests.parsertest import ParserTest

if __name__ == "__main__":
    suite = unittest.TestLoader ().loadTestsFromTestCase (ParserTest)
    unittest.TextTestRunner (verbosity=2).run (suite)
