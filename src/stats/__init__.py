"""
Package to create data for stats
and analyse and maybe visualise them
"""
import netCDF4
import numpy as np

def loadRawXData(year):
    """ Load all days in year """
    day0 = 0
    ndays = 357
    datafile = '/Users/Leon/pycharm/datahack/wild-fire/data/cal_era5_%i.nc' % year
    ncdata = netCDF4.Dataset(datafile)
    variableLs = ['t2m', 'd2md', 'sp', 'tp', 's10', 'lai_lv', 'swvl1']
    variables = {}
    for variable in variableLs:
        if variable == 's10':
            u10 = ncdata.variables['u10'][day0:day0+ndays]
            v10 = ncdata.variables['v10'][day0:day0+ndays]
            variables['s10'] = np.sqrt(u10*u10 + v10*v10)
        elif variable == 'd2md':
            d2m = ncdata.variables['d2m'][day0:day0 + ndays]
            variables[variable] = variables['t2m'] - d2m
        else:
            variables[variable] = ncdata.variables[variable][day0:day0+ndays]
    return variables

def loadXData(year):
    """ Load csv files """
    variableLs = ['sp', 't2m', 'd2md', 's10', 'tp', 'lai_lv', 'swvl1']
    varDict = {}
    for v in variableLs:
        varDict[v] = []
    vnames = "_".join([v for v in variableLs])
    datafile = '../data/'+vnames+'_%i.csv'%year
    with open(datafile, 'r') as fh:
        for line in fh.readlines():
            data = line.split(',')
            for v,s in zip(variableLs, data):
                varDict[v].append(float(s))
    return varDict

def loadRawYData(year=2008):
    """ Load in fires for year """
    #datafile = '/Users/Leon/pycharm/datahack/wild-fire/data/rates_y%i.csv' % year
    datafile = '/Users/Leon/pycharm/datahack/wild-fire/data/rates_t150_y%i.csv' % year
    fires = []
    with open(datafile, 'r') as fh:
        for line in fh.readlines():
            data = line.split(',')
            fires.append([ int(d) for d in data ])
    return fires

def getBounds(ind, maxBound=101):
    bnd = 2
    if ind-bnd >= 0:
        ind0 = ind-bnd
    else:
        ind0 = 0
    if ind+bnd+1 <= maxBound:
        ind1 = ind+bnd+1
    else:
        ind1 = maxBound
    return ind0, ind1

def getVarForFireEvent(fire, variables, dayOffset=0):
    """ Return values for variables for fire event """
    varsOut = []
    for variable in variables:
        data = variables[variable]
        if fire[0]-4 >= 0:
            it0 = fire[0]+dayOffset-4
        else:
            it0 = 0
        i0, i1 = getBounds(fire[1])
        j0, j1 = getBounds(fire[2])
        area = data[it0:fire[0]+dayOffset, i0:i1, j0:j1]
        varsOut.append(area.mean())
    return varsOut

def getVarForAllFires(fireList, variables, dayOffset=0):
    """ Make a list of lists with variables values """
    allVars = []
    for fire in fireList:
        varsOut = getVarForFireEvent(fire, variables, dayOffset)
        allVars.append(varsOut)
    return allVars

def saveVarsCSV(variables, allVars, year):
    """ Save vars as CSV """
    vnames = "_".join([v for v in variables])
    filename = vnames+'_t150_%i.csv'%year
    #filename = vnames+'_%i.csv'%year
    with open(filename, 'w') as fh:
        for varsOut in allVars:
            fh.write(", ".join([ '%9.6e'%var for var in varsOut ])+'\n')

if __name__ == '__main__':
    year = 2008
    #dayOffset = 0
    for dayOffset in range(0, 3653, 366):
        variables = loadRawXData(year)
        fires = loadRawYData(year)
        allVars = getVarForAllFires(fires, variables, dayOffset=-1*dayOffset)
        saveVarsCSV(variables, allVars, year)
        year += 1
