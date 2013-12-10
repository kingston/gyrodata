import numpy as np
from numpy import *
from scipy import signal
import gyrodata
import statsmodels.tsa.arima_model as ap
import time
import pylab

import process

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(features, entry, config):
    # require gyro and acc data
    if not config['data-filters']['gyrofile']: return
    if not config['data-filters']['accfile']: return

    accData = np.array(readNumericData(entry['accfile']))
    gyroData = np.array(readNumericData(entry['gyrofile']))

    # clean data up
    accData, gyroData = process.cleanData(accData, gyroData)
    # process data
    accData, gyroData = process.processData(accData, gyroData)

    #features += accData.mean(axis=0)[1:].tolist()
    features += accData.std(axis=0)[1:].tolist()
    totalAcc = sqrt((square(accData[:,1]) + square(accData[:,2]) + square(accData[:,3])))
    
    medFilterAccX = signal.medfilt(accData[:,1],11)
    medFilterAccY = signal.medfilt(accData[:,2],11)
    medFilterAccZ = signal.medfilt(accData[:,3],11)
    
    b, a = signal.butter(3, 10.0/25, btype='low')
    butterAccX = signal.filtfilt(b,a,medFilterAccX)
    butterAccY = signal.filtfilt(b,a,medFilterAccY)
    butterAccZ = signal.filtfilt(b,a,medFilterAccZ)
    
    b, a = signal.butter(3, 0.3/25, btype='low')
    gravityAccX = signal.filtfilt(b,a,butterAccX)
    gravityAccY = signal.filtfilt(b,a,butterAccY)
    gravityAccZ = signal.filtfilt(b,a,butterAccZ)

    
    b, a = signal.butter(3, 0.3/25, btype='high')
    bodyAccX = signal.filtfilt(b,a,butterAccX)
    bodyAccY = signal.filtfilt(b,a,butterAccY)
    bodyAccZ = signal.filtfilt(b,a,butterAccZ)
    totalAcc = sqrt(square(bodyAccX)+square(bodyAccY)+square(bodyAccZ))
    #features.append(mean(totalAcc))

    #features.append(mean(bodyAccX))
    #features.append(std(bodyAccX))
    #features.append(mean(bodyAccY))
    #features.append(std(bodyAccY))
    #features.append(mean(bodyAccZ))
    #features.append(std(bodyAccZ))
    #features.append(mean(gravityAccZ))
    #features.append(std(gravityAccZ))
    #features.append(mean(gravityAccX))
    #features.append(std(gravityAccX))
    #features.append(mean(gravityAccY))
    #features.append(std(gravityAccY))
    
    #features.append(sqrt(mean(square(bodyAccX))))
    features.append(sqrt(mean(square(bodyAccY))))
    #features.append(sqrt(mean(square(bodyAccZ))))
    
    #fx,Px = signal.welch(bodyAccX, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
    #fy,Py = signal.welch(bodyAccY, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
    #fz,Pz = signal.welch(bodyAccZ, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
    
    #features.append(sum(square(Px)))
    #pylab.show()
    
    
    
    bodyJerkX=diff(bodyAccX,n=1)
    bodyJerkY=diff(bodyAccY,n=1)
    bodyJerkZ=diff(bodyAccZ,n=1)
    #features.append(mean(bodyJerkX))
    #features.append(std(bodyJerkX))
    #features.append(mean(bodyJerkY))
    #features.append(std(bodyJerkY))
    #features.append(mean(bodyJerkZ))
    #features.append(std(bodyJerkZ))
    
