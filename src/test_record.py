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

    def test_findMaxima(self):
        array = np.array([[0,0,0],
                          [0,0,0],
                          [0,0,0]])
        freeLocs = np.array([[True, True, True],
                             [True, True, True],
                             [True, True, True]])

        ls, id = record.findMaxima(array, freeLocs, 1, 1)
        self.assertEqual(ls, [])
        self.assertEqual(id, 1)

    def test_getSurroundingFires(self):
        array = np.array([[1,2,1],
                          [0,0,0],
                          [0,2,0]])
        freeLocs = np.array([[True, False, True],
                             [True, True, True],
                             [True, False, True]])
        fire1 = firestorm.FireStorm(1, (0,1), 1)
        fire2 = firestorm.FireStorm(1, (2,1), 1)
        area1 = record.getSurroundingFires(fire1, array, freeLocs, offset=1)
        self.assertEqual(area1, 2)
        area2 = record.getSurroundingFires(fire2, array, freeLocs, offset=1)
        self.assertEqual(area2, 0)


    def test_calcAreas(self):
        array = np.array([[1, 2, 1, 1, 0],
                          [0, 0, 0, 1, 1],
                          [0, 2, 1, 0, 0]])
        freeLocs = record.initLogicalArray(array.shape)
        fire1 = firestorm.FireStorm(1, (0, 1), 1)
        fire2 = firestorm.FireStorm(2, (2, 1), 1)
        fireList = record.calcAreas([fire1, fire2], array, freeLocs, gridBoxArea=1)
        self.assertEqual(fireList[0].getAreaList()[0], 2)
        self.assertEqual(fireList[1].getAreaList()[0], 6)

    def test_checkFirePersistence(self):
        array = np.array([[1, 2, 1, 1, 0],
                          [0, 0, 0, 0, 0],
                          [0, 0, 1, 0, 0]])
        fire1 = firestorm.FireStorm(1, (0, 1), 1)
        fire2 = firestorm.FireStorm(2, (2, 1), 1)
        fire3 = firestorm.FireStorm(2, (2, 4), 1)
        popList = record.checkFirePersistence([fire1, fire2, fire3], array)
        self.assertEqual(popList, [2])

if __name__ == '__main__':
    unittest.main()
