"""
Class to describe individual fire storms
Has the following properties:
stormId: integer number > 0
startLoc: (lat, lon) of initial centre of fire
startTime: time of start of fire
timeLen: lifetime of fire (days)
area: array of daily area m^2
maxArea: largest area of fire m^2
rate: array of daily growth rates m^2/day
maxRate: fastest growth rate of fire m^2/day
"""

class FireStorm(object):
    def __init__(self, stormId, startLoc, startTime,
                 initialArea=None):
        self.stormId = stormId
        self.startLoc = startLoc
        self.startTime = startTime
        if initialArea:
            self.area=[initialArea]
        else:
            self.area = []

    def addDailyArea(self, area, day=None):
        if day:
            self.area[day] = area
        else:
            self.area.append(area)

    def getTimeLen(self):
        if len(self.area) > 0:
            return len(self.area)
        else:
            return None

    def getAreaList(self):
        return self.area

    def getMaxArea(self):
        if len(self.area) > 0:
            return max(self.area)
        else:
            return None

    def getRateList(self):
        if len(self.area) > 1:
            rate = [ a1 - a0 for a0,a1 in zip(self.area[:-1], self.area[1:]) ]
            return rate
        else:
            return None

    def getMaxRate(self):
        if len(self.area) > 1:
            rate = [ a1 - a0 for a0,a1 in zip(self.area[:-1], self.area[1:]) ]
            return max(rate)
        else:
            return None
