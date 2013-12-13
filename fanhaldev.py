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
        '''
        gyroData = array(readNumericData(entry['gyrofile']))
        gyroData = gyroData[150:(len(gyroData[:,0])-60),:]

        gyroFilterAccY = signal.medfilt(gyroData[:,2],11)
        
        b, a = signal.butter(3, 10.0/25, btype='low')
        butterGyroY = signal.filtfilt(b,a,gyroFilterAccY)
        widths = arange(5,10)
        peakind = signal.find_peaks_cwt(butterGyroY, widths)
        #print entry
        print peakind
        if len(peakind)<=1: peakind = signal.find_peaks_cwt(-1*butterGyroY, widths)
        if len(peakind)<=1: 
            plt.plot(range(1,len(butterGyroY)+1),butterGyroY)
            plt.show()
        #time.sleep(100000000)

        features.append(mean(diff(peakind)))

        #features.append(sum(abs(signal.cwt(gravityAccZ, wavelet, widths))))
        '''
        # Frequency domain
        
        #totalAcc = butterGyroY
        windowSize=max(len(totalAcc),250)
        n=len(totalAcc)
        nWindows=0
        total=zeros(windowSize)
        start=0
        while start<(n-windowSize+1):
        	total=total+fft.fft(totalAcc[start:(start+windowSize)])
        	nWindows+=1
        	start+=floor(windowSize/2)
        meanFourier=total/nWindows
        features += [abs(meanFourier[0])] # DC Component
        #features += [linalg.norm(meanFourier)] # Energy
        freq = fft.fftfreq(len(meanFourier))
        idx = argmax(abs(meanFourier)**2)
        #features += [freq[idx]] # Dominant frequency
        #features += [abs(sum(meanFourier))] # Coefficients sum
        