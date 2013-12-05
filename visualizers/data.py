# Library for accessing gyro data
import os, csv, sys

# import gyrodata from parent directory
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import gyrodata

def readNumericData(path):
    data = gyrodata.readCsvData("../" + path)
    return [[float(x or 0) for x in l] for l in data]

def getEntryById(meta, id):
    for entry in meta:
        if id in entry['accfile']:
            return entry
    return None
