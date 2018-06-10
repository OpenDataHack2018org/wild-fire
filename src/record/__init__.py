"""
Module with functions to record
areas and lifetimes of fires

Note that the FireStorm class has
the capability to have a new location
for every day, but this module assumes
fires are stationary (moving one gridbox
is fine)
"""
import numpy as np
import firestorm
import netCDF4

#Global to set minimum value to count as fire
FIREMIN = 0.1

def initLogicalArray(shape):
    return np.ones(shape, dtype=bool)

def loadTestData(day0=179, ndays=5):
    """ Load a few days for testing """
    datafile = '/Users/Leon/pycharm/datahack/wild-fire/data/cal_cams_gfas.nc'
    ncdata = netCDF4.Dataset(datafile)
    data = ncdata.variables['frpfire'][:]
    return data[day0:day0+ndays]

def getDist(fire1, fire2):
    """ Return distance between two fires """
    dx = fire1.locations[0][0] - fire2.locations[0][0]
    dy = fire1.locations[0][1] - fire2.locations[0][1]
    return np.sqrt(dx**2 + dy**2)

def removeDuplicates(fireList):
    """ If two maxima are adjacent then pop one """
    popList = []
    for i in range(1,len(fireList)):
        if getDist(fireList[i-1], fireList[i]) < 1.4142136:
            popList.append(i)
    for popper in popList[::-1]:
        fireList.pop(popper)

def isMaximum(array, i, j):
    """ Is location i,j in array a local maximum? """
    ioffs = [-1, 0, 1,-1, -1, 0, 1, 1]
    joffs = [ 1, 1, 1, 0, -1,-1,-1, 0]
    for io,jo in zip(ioffs, joffs):
        try:
            positives = (i + io >= 0) and (j + jo >= 0)
            if positives and ( array[i,j] < array[i+io,j+jo] ):
                return False
        except IndexError:
            pass
    return True

def findMaxima(array, freeLocs, time, nextId):
    """ Return list of firestorms from uncounted regions """
    shape = array.shape
    fireList = []
    for i in range(shape[0]):
        for j in range(shape[1]):
            if freeLocs[i,j] and array[i,j]>FIREMIN:
                if isMaximum(array, i, j):
                    fireList.append(
                        firestorm.FireStorm(nextId, (i,j), time))
                    nextId += 1
    #Neighbouring points can have equal values, choose one as max
    removeDuplicates(fireList)
    return fireList, nextId

def getSurroundingFires(fire, array, freeLocs, offset=1):
    """ How many of surrounding boxes have fires """
    extraArea = 0
    i = fire.locations[0][0]
    j = fire.locations[0][1]
    for jo in range(-1*offset, offset+1):
        if abs(jo) == offset:
            ioffs = range(-1*offset, offset+1)
        else:
            ioffs = [-1*offset, offset]
        for io in ioffs:
            try:
                positives = (i+io >= 0) and (j+jo >= 0)
                if positives and freeLocs[i+io, j+jo] and \
                        array[i+io, j+jo]>FIREMIN:
                    freeLocs[i+io, j+jo] = False
                    extraArea += 1
            except IndexError:
                pass
    return extraArea

def calcAreas(fireList, array, freeLocs, gridBoxArea=11*11):
    """ Calculate area of each fire masking as summing """
    sums = []
    for fire in fireList:
        i = fire.locations[0][0]
        j = fire.locations[0][1]
        #Original location of fire may not be on fire...
        if array[i,j] > FIREMIN:
            freeLocs[i,j] = False
            sums.append(gridBoxArea)
        else:
            sums.append(0)
    finalFires = []
    finalSums = []
    maxOffs = max(array.shape[0], array.shape[1])
    for offset in range(1, maxOffs):
        popList=[]
        for i, fire in enumerate(fireList):
            extraArea = getSurroundingFires(fire, array, freeLocs, offset=offset)
            if extraArea > 0:
                sums[i] += gridBoxArea * extraArea
            else:
                popList.append(i)
        for popper in popList[::-1]:
            finalFires.append(fireList.pop(popper))
            finalSums.append(sums.pop(popper))
        if len(fireList) == 0:
            break

    for fire, area in zip(finalFires, finalSums):
        fire.addDailyArea(area)
    return finalFires

def checkFirePersistence(fireList, array):
    """ See if fire still there """
    popList = []
    for ind, fire in enumerate(fireList):
        i = fire.locations[0][0]
        j = fire.locations[0][1]
        if array[i,j] < FIREMIN:
            #Allow fire to be within one gridbox of original location
            ioffs = [-1, 0, 1, -1, -1, 0, 1, 1]
            joffs = [1, 1, 1, 0, -1, -1, -1, 0]
            failed = True
            for io, jo in zip(ioffs, joffs):
                try:
                    positives = (i + io >= 0) and (j + jo >= 0)
                    if positives and (array[i+io, j+jo] > FIREMIN):
                        failed = False
                except IndexError:
                    pass
            if failed:
                popList.append(ind)
    return popList

def removeShortLivedFire(fireList, minLen=2):
    """ Return a list with a short lived fires removed """
    newList = []
    for fire in fireList:
        age = fire.getTimeLen()
        if age >= minLen:
            newList.append(fire)
    return newList

def saveGrowingFireStorms(fireList, filename, threshRate=150):
    """ csv file time, i, j, rate """
    with open(filename, 'w') as fh:
        for fire in finalList[::-1]:
            if fire.getMaxRate() > threshRate:
                i,j = fire.locations[0]
                t0 = fire.startTime
                rates = fire.getRateList()
                for it, rate in enumerate(rates):
                    if rate > threshRate:
                        fh.write("%i, %i, %i, %i\n" % (it+t0, i, j, rate))


if __name__ == '__main__':
    year = 2008
    #day0 = 1    #171
    for day0 in range(0, 3653, 366):
        ndays = 357     #5
        array = loadTestData(day0=day0, ndays=ndays)
        freeLocs = initLogicalArray(array[0].shape)
        nextId = 1
        fireList = []

        poppedFires = []
        for iday in range(0, ndays):
            freeLocs = initLogicalArray(array[0].shape)
            if len(fireList) < 1:
                fireList, nextId = findMaxima(array[iday], freeLocs, day0+iday, nextId)
                fireList = calcAreas(fireList, array[iday], freeLocs)
            else:
                popList = checkFirePersistence(fireList, array[iday])
                for popper in popList[::-1]:
                    poppedFires.append(fireList.pop(popper))
                fireList = calcAreas(fireList, array[iday], freeLocs)
                newList, nextId = findMaxima(array[iday], freeLocs, day0+iday, nextId)
                if len(newList)>0:
                    newList = calcAreas(newList, array[iday], freeLocs)
                    fireList.extend(newList)
        fireList.extend(poppedFires)
        finalList = removeShortLivedFire(fireList)
        saveGrowingFireStorms(finalList, 'rates_t150_y%i.csv'%year)
        year += 1