"""
Module with functions to record
areas and lifetimes of fires
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
            if array[i,j] < array[i+io,j+jo]:
                return False
        except IndexError:
            pass
    return True

def findMaxima(array, freeLocs, time, nextId):
    """ Return list of firestorms from uncounted regions """
    shape = array.shape
    fireList = []
    for i in range(shape[1]):
        for j in range(shape[0]):
            if freeLocs[i,j] and array[i,j]>FIREMIN:
                if isMaximum(array, i, j):
                    fireList.append(
                        firestorm.FireStorm(nextId, (i,j), time))
                    nextId += 1
    #Neighbouring points can have equal values, choose one as max
    removeDuplicates(fireList)
    return fireList, nextId

