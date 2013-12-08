import data
import numpy as np
import scipy
from scipy import integrate, signal
import math

def filterByTime(start, end, data):
    return data[(data[:, 0] >= start) & (data[:, 0] <= end)]

# normalize the start/end of the data
def normalizeDatasets(accData, gyroData):
    start = max(accData[:, 0].min(), gyroData[:, 0].min())
    end = min(accData[:, 0].max(), gyroData[:, 0].max())
    return (filterByTime(start, end, accData), filterByTime(start, end, gyroData))

def cleanSeparateData(data, otherData):
    # maximum threshold between samples to remove the gap
    THRESHOLD = 250
    MIN_DISTANCE = 50
    offset = 0
    prevTime = 0
    otherIdx = 0
    for i in xrange(len(data)):
        if data[i, 0] - prevTime > THRESHOLD:
            offset = offset + data[i, 0] - prevTime - MIN_DISTANCE
            while otherIdx < len(otherData) and otherData[otherIdx, 0] < data[i, 0]:
                otherData = np.delete(otherData, otherIdx, 0)
        else:
            while otherIdx < len(otherData) and otherData[otherIdx, 0] < data[i, 0]:
                otherData[otherIdx, 0] = otherData[otherIdx, 0] - offset
                otherIdx = otherIdx + 1
        prevTime = data[i, 0]
        data[i, 0] = data[i, 0] - offset
    return (data, otherData)

# clean ends of the data
def cleanEnds(accData, gyroData):
    # threshold of data to start recording
    threshold = np.std(accData[:, 1])
    start = 0
    for i in xrange(len(accData)):
        if abs(accData[i, 1]) > threshold:
            break
        start = accData[i, 0]
    end = 0
    for i in xrange(len(accData) - 1, -1, -1):
        if abs(accData[i, 1]) > threshold:
            break
        end = accData[i, 0]

    return (filterByTime(start, end, accData), filterByTime(start, end, gyroData))

# cleans up bad parts of the data (e.g. when they're putting it in their pocket)
def cleanData(accData, gyroData):
    (accData, gyroData) = cleanEnds(accData, gyroData)
    # look for empty sections in the data and remove them
    (accData, gyroData) = cleanSeparateData(accData, gyroData)
    (gyroData, accData) = cleanSeparateData(gyroData, accData)

    return normalizeDatasets(accData, gyroData)
