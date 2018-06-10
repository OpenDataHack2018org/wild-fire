#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()
server.retrieve({
    "class": "ea",
    "dataset": "era5",
    "date": "2013-01-01/to/2013-12-31",
    "expver": "1",
    "format": "netcdf",
    "area": "42/-125/32/-115",
    "levtype": "sfc",
    "number": "0",
    "param": "168.128/167.128/134.128/228.128/165.128/166.128/66.128/39.128",
    "step": "6",
    "stream": "enda",
    "time": "06:00:00",
    "type": "fc",
    "target": "cal_era5_2013.nc",
    "grid" : "0.1/0.1",
})
