import data
import numpy as np
import scipy
from scipy import integrate, signal
import math
from math import *
from numpy.linalg import inv

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

def processData(accData, gyroData):
    gyro = []
    for i in range(3):
        # interpolate data with accelerometer data and convert to radians
        gyro.append(np.interp(accData[:, 0], gyroData[:, 0], gyroData[:, i + 1]) / 360 * 2 * math.pi)
    gyroData = np.column_stack((accData[:, 0], gyro[0], gyro[1], gyro[2]))

    for i in range(len(accData)):
        tx = gyroData[i, 1]
        ty = gyroData[i, 2]
        tz = gyroData[i, 3]
        Rx = np.array([[1,0,0], [0, cos(tx), -sin(tx)], [0, sin(tx), cos(tx)]])
        Ry = np.array([[cos(ty), 0, -sin(ty)], [0, 1, 0], [sin(ty), 0, cos(ty)]])
        Rz = np.array([[cos(tz), -sin(tz), 0], [sin(tz), cos(tz), 0], [0,0,1]])
        R = np.dot(Rx, np.dot(Ry, Rz))

        vec = (accData[i, 1], accData[i, 2], accData[i, 3])
        (accData[i, 1], accData[i, 2], accData[i, 3]) = np.dot(inv(R), vec)

    return (accData, gyroData)

    # reinterpolate acceleration data into even samples
    minTime = accData[:, 0].min()
    maxTime = accData[:, 0].max()
    newTime, step = scipy.linspace(minTime, maxTime, num=len(accData[:, 0]), retstep = True)
    for i in range(3):
        accData[:, i + 1] = np.interp(newTime, accData[:, 0], accData[:, i + 1])
    accData[:, 0] = newTime

    # apply fft transform
    for i in range(3):
        FFT = abs(scipy.fft(accData[:, i + 1]))
        #freqs = scipy.fftpack.fftfreq(len(newTime), step)
        #accData[:, 0] = freqs
        accData[:, i + 1] = scipy.log10(FFT)

    gyro = [];
    for i in range(3):
        # Convert gyrometer data to radians
        gyro.append(gyroData[:, i + 1] * 2 * math.pi)
        # Integrate data for approximate location
        gyro[i] = integrate.cumtrapz(gyro[i], gyroData[:, 0], initial=0)
        # apply high pass filter to reduce drift
        # and we don't care about overall change in motion
        #
        
        # interpolate data with accelerometer data
        gyro[i] = np.interp(accData[:, 0], gyroData[:, 0], gyro[i])

    gyroData = np.column_stack((accData[:, 0], gyro[0], gyro[1], gyro[2]))
    # interpolate gyro data
    yGyro = np.interp(accData[:, 0], gyroData[:, 0], gyroData[:, 2])
    zGyro = np.interp(accData[:, 0], gyroData[:, 0], gyroData[:, 3])

    return (accData, gyroData)
