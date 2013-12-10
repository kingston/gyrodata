from numpy import *
from scipy import signal
import gyrodata
import statsmodels.tsa.arima_model as ap
import matplotlib.pyplot as plt
import time
import pylab
from scipy import signal

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]
    
def movingAverageExponential(values, alpha, epsilon = 0):

    if not 0 < alpha < 1:
        raise ValueError("out of range, alpha='%s'" % alpha)

    if not 0 <= epsilon < alpha:
        raise ValueError("out of range, epsilon='%s'" % epsilon)

    result = [None] * len(values)

    for i in range(len(result)):
        currentWeight = 1.0

        numerator = 0
        denominator = 0
        for value in values[i::-1]:
            numerator += value * currentWeight
            denominator += currentWeight

            currentWeight *= alpha
            if currentWeight < epsilon: 
                break

        result[i] = numerator / denominator

    return result

def extractFeatures(features, entry, config):
    
    if config['data-filters']['accfile']:
        #features.append(float(entry['height']))
        
        accData = array(readNumericData(entry['accfile']))
        length = len(accData[:,1])
        qtr = length/4
        accData = accData[qtr:(length-qtr),:]
        accX = accData[:,1]
        accY = accData[:,2]
        accZ = accData[:,3]
        
        #fY = signal.lfilter([.1,.1,.1,.1,.1,.1,.1,.1,.1,.1],[1],accY)
        #plt.plot(range(0,len(fY)),fY)
        #plt.show()
        filtAccX = []
        filtAccY = []
        filtAccZ = []
        for i in range(9,len(accY)):
            filtAccX.append(sum(accX[(i-9):i])/10)
            filtAccY.append(sum(accY[(i-9):i])/10)
            filtAccZ.append(sum(accZ[(i-9):i])/10)
            
        #print filtAccY
        #plt.plot(range(0,len(filtAccY)),filtAccY)
        #plt.show()
        #features.append(1.0/(1-min(filtAccX)))
        #features.append(1.0/(1-max(filtAccX)))
        features.append(1.0/(1-min(filtAccY)))
        features.append(1.0/(1-max(filtAccY)))
        features.append(max(filtAccY))
        features.append(min(filtAccY))
        #features.append(1.0/(1-min(filtAccZ)))
        #features.append(1.0/(1-max(filtAccZ)))
        
        '''
        accData = array(readNumericData(entry['accfile']))
        accData = accData[150:(len(accData[:,0])-60),:]
        #features += accData.mean(axis=0)[1:].tolist()
        #features += accData.std(axis=0)[1:].tolist()
        #totalAcc = sqrt((square(accData[:,1]) + square(accData[:,2]) + square(accData[:,3])))
        
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
        
        expAccY = movingAverageExponential(butterAccY, .995)
        widths = arange(5,10)
        peakind = signal.find_peaks_cwt(expAccY, widths)
        diffs = diff(peakind)
        medDiffs = median(diffs)
        index = 0
        for i in range(len(peakind)/2, len(peakind)-1):
            if (diffs[i] == medDiffs) or ((medDiffs -4) <= diffs[i] <= (medDiffs+4)):
                index = i
                break
        print peakind
        print diffs
        if index == 0:
            features.append(0)
        else:
            val = 0
            for i in range(peakind[index], peakind[index+1]):
                val = val + abs(bodyAccY[i])
            
            plt.plot(range(0,peakind[index+1]-peakind[index]),bodyAccY[peakind[index]:peakind[index+1]])
            plt.show()
            features.append(power(val/float(peakind[index+1]-peakind[index]), 1/float(3)))
        '''
        '''
        print peakind
        plt.plot(range(1,len(butterAccY)+1),butterAccY)
        pylab.show()
        
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
        
        #fftBodyX = signal.welch(bodyAccX, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyY = signal.welch(bodyAccY, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyZ = signal.welch(bodyAccZ, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        
        #plt.plot(fftBodyX)
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
        '''
        '''
        seqLen = float(size(totalAcc))
        features+=(size(totalAcc[totalAcc>=buckets[-1]])/seqLen)
        for j in range(size(buckets)-1):
            upperBound = totalAcc<buckets[j+1]
            lowerBound = totalAcc>=buckets[j]
            features+=(size(totalAcc[lowerBound & upperBound])/seqLen)
        '''
    if config['data-filters']['gyrofile']:
        '''
        gyroData = array(readNumericData(entry['gyrofile']))
        gyroData = gyroData[150:(len(gyroData[:,0])-60),:]
        gyroData = abs(gyroData)
        #features.append(gyroData.mean(axis=0)[2])
        
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
        
        #plt.plot(gyroData[:,0],gyroData[:,2])
        #plt.plot(gyroData[:,0],buttergyroY)
        #pylab.show()
        
        #totalgyro = sqrt(square(bodygyroX)+square(bodygyroY)+square(bodygyroZ))
        #features.append(mean(totalgyro))
        
        expY = movingAverageExponential(bodygyroY,.5)
        widths = arange(5,10)
        peakind = signal.find_peaks_cwt(bodygyroY, widths)
        if(len(diff(peakind))==0):
            features.append(0)
        else:
            features.append(median(diff(peakind)))
        print median(diff(peakind))
        #plt.plot(range(0,len(expY)),expY)
        #features.append(median(diff()
        #plt.show()
        '''
        '''
        #features.append(mean(bodygyroX))
        #features.append(std(bodygyroX))
        features.append(mean(bodygyroY))
        features.append(std(bodygyroY))
        #features.append(mean(bodygyroZ))
        #features.append(std(bodygyroZ))
        #features.append(mean(gravitygyroZ))
        #features.append(std(gravitygyroZ))
        #features.append(mean(gravitygyroX))
        #features.append(std(gravitygyroX))
        features.append(mean(gravitygyroY))
        features.append(std(gravitygyroY))
        
        #features.append(sqrt(mean(square(bodygyroX))))
        features.append(sqrt(mean(square(bodygyroY))))
        #features.append(sqrt(mean(square(bodygyroZ))))
        
        #fftBodyX = signal.welch(bodygyroX, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyY = signal.welch(bodygyroY, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyZ = signal.welch(bodygyroZ, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        
        #plt.plot(fftBodyX)
        #pylab.show()
        
        
        #wavelet = signal.ricker
        #widths = arange(1,120)
        #peakind = signal.find_peaks_cwt(bodygyroY, widths)

        #features.append(mean(diff(peakind)))

        #features.append(sum(abs(signal.cwt(bodygyroY, wavelet, widths))))
        
        
        bodyJerkX=diff(bodygyroX,n=1)
        bodyJerkY=diff(bodygyroY,n=1)
        bodyJerkZ=diff(bodygyroZ,n=1)
        #features.append(mean(bodyJerkX))
        #features.append(std(bodyJerkX))
        #features.append(mean(bodyJerkY))
        #features.append(std(bodyJerkY))
        #features.append(mean(bodyJerkZ))
        #features.append(std(bodyJerkZ))
        #print features
        '''
        '''
        totalGyro = sqrt((square(gyroData[:,1]) + square(gyroData[:,2]) + square(gyroData[:,3])))
        seqLen = float(size(totalGyro))
        features.append(size(totalGyro[totalGyro>=buckets[-1]])/seqLen)
        for j in range(size(buckets)-1):
            upperBound = totalGyro<buckets[j+1]
            lowerBound = totalGyro>=buckets[j]
            features.append(size(totalGyro[lowerBound & upperBound])/seqLen)
        '''