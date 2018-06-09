"""
Unit test of firestorm class methods
"""
import unittest
import firestorm

class MyTest(unittest.TestCase):
    def test_addDailyArea(self):
        fs = firestorm.FireStorm(100, (44, -120), 0, initialArea=500)
        fs.addDailyArea(10)
        self.assertEqual(fs.area, [500,10])
        fs.addDailyArea(20, day=1)
        self.assertEqual(fs.area, [500,20])

    def test_getTimeLen(self):
        fs = firestorm.FireStorm(100, (44, -120), 0, initialArea=500)
        self.assertEqual(fs.getTimeLen(), 1)

    def test_getAreaList(self):
        fs = firestorm.FireStorm(100, (44, -120), 0, initialArea=500)
        self.assertEqual(fs.getAreaList(), [500])

    def test_getMaxArea(self):
        fs = firestorm.FireStorm(100, (44, -120), 0, initialArea=500)
        self.assertEqual(fs.getMaxArea(), 500)

    def test_getRateList(self):
        fs = firestorm.FireStorm(100, (44, -120), 0, initialArea=500)
        fs.addDailyArea(510)
        self.assertEqual(fs.getRateList(), [10])

    def get_getMaxRate(self):
        fs = firestorm.FireStorm(100, (44, -120), 0, initialArea=500)
        fs.addDailyArea(510)
        fs.addDailyArea(550)
        self.assertEqual(fs.getMaxRate(), 40)

if __name__ == '__main__':
    unittest.main()


