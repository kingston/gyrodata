import data
import numpy as np

def filterByTime(start, end, data):
    return data[(data[:, 0] >= start) & (data[:, 0] <= end)]

def normalizeDatasets(accData, gyroData):
    start = max(accData[:, 0].min(), gyroData[:, 0].min())
    end = min(accData[:, 0].max(), gyroData[:, 0].max())
    return (filterByTime(start, end, accData), filterByTime(start, end, gyroData))

def absoluteReferenceAccData(accData, gyroData):
    # interpolate gyro data
    xGyro = np.interp(accData[:, 0], gyroData[:, 0], gyroData[:, 1])
    yGyro = np.interp(accData[:, 0], gyroData[:, 0], gyroData[:, 2])
    zGyro = np.interp(accData[:, 0], gyroData[:, 0], gyroData[:, 3])
    gyroData = np.column_stack((accData[:, 0], xGyro, yGyro, zGyro))

    # calculate absolute reference

    return gyroData
