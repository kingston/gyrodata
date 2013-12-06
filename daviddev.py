from numpy import *
<<<<<<< HEAD
import scipy
from scipy import signal
from scipy import fftpack
import gyrodata
import statsmodels.tsa.arima_model as ap
import matplotlib.pyplot as plt
import time
import pylab
from scipy import signal
import gyrodata
import statsmodels.tsa.arima_model as ap

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(features, entry, config):
    #print scipy.version.version
    if config['data-filters']['accfile']:
        accData = array(readNumericData(entry['accfile']))
        #accData = accData[120:(len(accData[:,0])-50),:]
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
        
        '''
        widths = arange(1, 4)
        peakind = signal.find_peaks_cwt(totalAcc, widths)
        x=[]
        x.append(peakind[1] - peakind[0])
        for i in range(2,len(peakind)):
            x.append(peakind[i]-peakind[i-1])
        features+=(mean(x))
        features += sum(abs(signal.cwt(totalAcc, wavelet, widths)))
        #features+=((signal.cwt(totalAcc,wavelet,widths))[1,:]).tolist()
        #features=x
        features += sum(abs(signal.cwt(totalAcc, wavelet, widths)))
        #print features
        #Pxx_den = signal.welch(totalAcc, 100, nperseg=1024)
        #features+=mean(square(Pxx_den))
        '''
        '''
        model = ap.ARMA(totalAcc)
        result=model.fit(order=(2,1),trend='c',disp=-1)
        features+=sum(result.params)
        '''
        '''
        seqLen = float(size(totalAcc))
        features+=(size(totalAcc[totalAcc>=buckets[-1]])/seqLen)
        for j in range(size(buckets)-1):
            upperBound = totalAcc<buckets[j+1]
            lowerBound = totalAcc>=buckets[j]
            features+=(size(totalAcc[lowerBound & upperBound])/seqLen)
        '''

        
        # Frequency domain
        windowSize=min(250,len(totalAcc))
        n=len(totalAcc)
        nWindows=0
        total=zeros(windowSize)
        startBuffer = 0
        endBuffer = 0
        start=0+startBuffer
        while start<(n-windowSize+1-endBuffer):
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
        

    if config['data-filters']['gyrofile']:
        gyroData = array(readNumericData(entry['gyrofile']))
        #gyroData = gyroData[120:(len(gyroData[:,0])-50),:]
        features += gyroData.mean(axis=0)[1:].tolist()
        features += gyroData.std(axis=0)[1:].tolist()
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
        
        #plt.plot(gyroData[:,0],gyroData[:,2])
        #plt.plot(gyroData[:,0],buttergyroY)
        #pylab.show()
        
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
        
        #fftBodyX = spectral.welch(bodygyroX, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyY = spectral.welch(bodygyroY, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        #fftBodyZ = spectral.welch(bodygyroZ, fs=50.0, nperseg=128, noverlap=128.0/2, nfft=None, detrend='constant', return_onesided=False, scaling='density', axis=-1)
        
        plt.plot(fftBodyX)
        pylab.show()
        
        
        
        bodyJerkX=diff(bodygyroX,n=1)
        bodyJerkY=diff(bodygyroY,n=1)
        bodyJerkZ=diff(bodygyroZ,n=1)
        #features.append(mean(bodyJerkX))
        #features.append(std(bodyJerkX))
        #features.append(mean(bodyJerkY))
        #features.append(std(bodyJerkY))
        features.append(mean(bodyJerkZ))
        features.append(std(bodyJerkZ))
        
        buckets = linspace(0, 2, num=5)
        features += gyroData.mean(axis=0)[1:].tolist()
        features += gyroData.std(axis=0)[1:].tolist()
        
        totalGyro = sqrt((square(gyroData[:,1]) + square(gyroData[:,2]) + square(gyroData[:,3])))
        seqLen = float(size(totalGyro))
        features.append(size(totalGyro[totalGyro>=buckets[-1]])/seqLen)
        for j in range(size(buckets)-1):
            upperBound = totalGyro<buckets[j+1]
            lowerBound = totalGyro>=buckets[j]
            features.append(size(totalGyro[lowerBound & upperBound])/seqLen)
