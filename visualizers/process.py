import data
import numpy as np
import scipy
from scipy import integrate, signal
import math

def filterByTime(start, end, data):
    return data[(data[:, 0] >= start) & (data[:, 0] <= end)]

def normalizeDatasets(accData, gyroData):
    start = max(accData[:, 0].min(), gyroData[:, 0].min())
    end = min(accData[:, 0].max(), gyroData[:, 0].max())
    return (filterByTime(start, end, accData), filterByTime(start, end, gyroData))

def processData(accData, gyroData):
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
