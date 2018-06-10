"""
Unit test of stat functions
"""
import stats
import unittest
import numpy as np

class MyTest(unittest.TestCase):
    def test_getBounds(self):
        ind0, ind1 = stats.getBounds(5, maxBound=10)
        self.assertEqual(ind0, 3)
        self.assertEqual(ind1, 8)
        ind0, ind1 = stats.getBounds(0, maxBound=10)
        self.assertEqual(ind0, 0)
        self.assertEqual(ind1, 3)
        ind0, ind1 = stats.getBounds(10, maxBound=10)
        self.assertEqual(ind0, 8)
        self.assertEqual(ind1, 10)


if __name__ == '__main__':
    unittest.main()
