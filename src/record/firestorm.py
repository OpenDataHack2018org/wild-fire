"""
Class to describe individual fire storms
Has the following properties:
stormId: integer number > 0
startTime: time of start of fire
timeLen: lifetime of fire (days)
locations: array of fire centre locations
area: array of daily area m^2
maxArea: largest area of fire m^2
rate: array of daily growth rates m^2/day
maxRate: fastest growth rate of fire m^2/day
"""

class FireStorm(object):
    def __init__(self, stormId, startLoc, startTime,
                 initialArea=None):
        self.stormId = stormId
        self.locations = [startLoc]
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

    def addDailyLocation(self, location, day=None):
        if day:
            self.locations[day] = location
        else:
            self.locations.append(location)

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

    def __str__(self):
        areas = [ str(area) for area in self.getAreaList() ]
        areaStr = " ".join(areas)
        age = self.getTimeLen()
        if len(areas) < 1:
            age = 0
        loc = self.locations[0]
        fireStr = "Fire %i: Birth: %i Loc: %i %i Age: %i Areas:" % (self.stormId, self.startTime,
                                                                    loc[0], loc[1], age)
        return fireStr+areaStr
