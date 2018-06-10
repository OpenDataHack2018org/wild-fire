#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()
server.retrieve({
    "class": "mc",
    "dataset": "cams_gfas",
    "date": "2008-01-01/to/2017-12-31",
    "expver": "0001",
    "levtype": "sfc",
    "param": "99.210",
    "step": "0-24",
    "stream": "gfas",
    "time": "00:00:00",
    "type": "ga",
    "target": "cal_test.nc",
    "format": "netcdf",
    "area": "42/-125/32/-115",
})
