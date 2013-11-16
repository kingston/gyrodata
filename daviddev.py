from numpy import *
import gyrodata

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(features, entry, config):
    if config['data-filters']['accfile']:
        accData = array(readNumericData(entry['accfile']))
        features += accData.max(axis=0)[1:].tolist()
    if config['data-filters']['gyrofile']:
        gyroData = array(readNumericData(entry['gyrofile']))
        features += gyroData.max(axis=0)[1:].tolist()
