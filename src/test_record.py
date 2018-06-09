"""
Unit test of record functions
"""
import record.firestorm as firestorm
import record
import unittest
import numpy as np

class MyTest(unittest.TestCase):
    def test_isMaximum_true(self):
        array = np.ones((4,4))
        array[1,2] = 2
        self.assertTrue(self, record.isMaximum(array,1,2))

    def test_isMaximum_false(self):
        array = np.ones((4, 4))
        array[1, 2] = 2
        self.assertTrue(self, not record.isMaximum(array,2,2))

    def test_removeDuplicates(self):
        ls = [ firestorm.FireStorm(1, (1,1), 1),
               firestorm.FireStorm(2, (2,2), 1)]
        record.removeDuplicates(ls)
        self.assertTrue(len(ls), 1)

if __name__ == '__main__':
    unittest.main()
