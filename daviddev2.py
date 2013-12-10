from numpy import *
from scipy import signal
import gyrodata
import statsmodels.tsa.arima_model as ap
import matplotlib.pyplot as plt
import time
import pylab

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(features, entry, config):
    '''
    if config['data-filters']['accfile']:
        
        accData = array(readNumericData(entry['accfile']))
        accData = accData[150:(len(accData[:,0])-60),:]
        features += accData.mean(axis=0)[1:].tolist()
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
        
        #plt.plot(accData[:,0],accData[:,2])
        #plt.plot(accData[:,0],butterAccY)
        #pylab.show()
        
        totalAcc = sqrt(square(bodyAccX)+square(bodyAccY)+square(bodyAccZ))
        features.append(mean(totalAcc))
        
        
        features.append(mean(bodyAccX))
        features.append(std(bodyAccX))
        features.append(mean(bodyAccY))
        features.append(std(bodyAccY))
        features.append(mean(bodyAccZ))
        features.append(std(bodyAccZ))
        features.append(mean(gravityAccZ))
        features.append(std(gravityAccZ))
        features.append(mean(gravityAccX))
        features.append(std(gravityAccX))
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
        features.append(mean(bodyJerkZ))
        features.append(std(bodyJerkZ))
        
        #wavelet = signal.ricker
        #widths = arange(120,150)
        #peakind = signal.find_peaks_cwt(bodyAccZ, widths)

        #features.append(mean(peakind))

        #features.append(sum(abs(signal.cwt(gravityAccZ, wavelet, widths))))
    
    
        seqLen = float(size(totalAcc))
        features+=(size(totalAcc[totalAcc>=buckets[-1]])/seqLen)
        for j in range(size(buckets)-1):
            upperBound = totalAcc<buckets[j+1]
            lowerBound = totalAcc>=buckets[j]
            features+=(size(totalAcc[lowerBound & upperBound])/seqLen)
    
    '''
    if config['data-filters']['gyrofile']:
        
        
        gyroData = array(readNumericData(entry['gyrofile']))
        gyroData = gyroData[150:(len(gyroData[:,0])-60),:]
        #features += gyroData.mean(axis=0)[1:].tolist()
        #features += gyroData.std(axis=0)[1:].tolist()
        totalgyro = sqrt((square(gyroData[:,1]) + square(gyroData[:,2]) + square(gyroData[:,3])))
        
        medFiltergyroX = signal.medfilt(gyroData[:,1],11)
        medFiltergyroY = signal.medfilt(gyroData[:,2],11)
        medFiltergyroZ = signal.medfilt(gyroData[:,3],11)
        
        b, a = signal.butter(3, 10.0/25, btype='low')
        buttergyroX = signal.filtfilt(b,a,medFiltergyroX)
        buttergyroY = signal.filtfilt(b,a,medFiltergyroY)
        buttergyroZ = signal.filtfilt(b,a,medFiltergyroZ)
        
        b, a = signal.butter(3, 0.3/25, btype='low')
        gravitygyroX = signal.filtfilt(b,a,buttergyroX)
        gravitygyroY = signal.filtfilt(b,a,buttergyroY)
        gravitygyroZ = signal.filtfilt(b,a,buttergyroZ)

        
        b, a = signal.butter(3, 0.3/25, btype='high')
        bodygyroX = signal.filtfilt(b,a,buttergyroX)
        bodygyroY = signal.filtfilt(b,a,buttergyroY)
        bodygyroZ = signal.filtfilt(b,a,buttergyroZ)
        
        
        widths = arange(5,10)
        peakind = signal.find_peaks_cwt(buttergyroY, widths)
        if(len(peakind)==1):
            peakind = signal.find_peaks_cwt(-buttergyroY, widths)

        features.append(median(diff(peakind)))
        
        print median(diff(peakind))
        #plt.plot(range(1,len(bodygyroY)+1),buttergyroY)
        #plt.plot(gyroData[:,0],buttergyroY)
        #plt.show()
        '''
        totalgyro = sqrt(square(bodygyroX)+square(bodygyroY)+square(bodygyroZ))
        features.append(mean(totalgyro))
        
        
        features.append(mean(bodygyroX))
        features.append(std(bodygyroX))
        features.append(mean(bodygyroY))
        features.append(std(bodygyroY))
        features.append(mean(bodygyroZ))
        features.append(std(bodygyroZ))
        features.append(mean(gravitygyroZ))
        features.append(std(gravitygyroZ))
        features.append(mean(gravitygyroX))
        features.append(std(gravitygyroX))
        #features.append(mean(gravitygyroY))
        #features.append(std(gravitygyroY))
        
        #features.append(sqrt(mean(square(bodygyroX))))
        features.append(sqrt(mean(square(bodygyroY))))
        #features.append(sqrt(mean(square(bodygyroZ))))
        
        #fftBodyX = signal.welch(bodygyroX, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyY = signal.welch(bodygyroY, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyZ = signal.welch(bodygyroZ, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        
        #plt.plot(fftBodyX)
        #pylab.show()
        
        
        
        bodyJerkX=diff(bodygyroX,n=1)
        bodyJerkY=diff(bodygyroY,n=1)
        bodyJerkZ=diff(bodygyroZ,n=1)
        #features.append(mean(bodyJerkX))
        #features.append(std(bodyJerkX))
        #features.append(mean(bodyJerkY))
        #features.append(std(bodyJerkY))
        features.append(mean(bodyJerkZ))
        features.append(std(bodyJerkZ))
        
        
        totalGyro = sqrt((square(gyroData[:,1]) + square(gyroData[:,2]) + square(gyroData[:,3])))
        seqLen = float(size(totalGyro))
        features.append(size(totalGyro[totalGyro>=buckets[-1]])/seqLen)
        for j in range(size(buckets)-1):
            upperBound = totalGyro<buckets[j+1]
            lowerBound = totalGyro>=buckets[j]
            features.append(size(totalGyro[lowerBound & upperBound])/seqLen)
        '''