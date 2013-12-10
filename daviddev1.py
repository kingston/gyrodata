from numpy import *
from scipy import signal
import gyrodata
import statsmodels.tsa.arima_model as ap
import matplotlib.pyplot as plt

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(features, entry, config):
    if config['data-filters']['accfile']:
        '''
        accData = array(readNumericData(entry['accfile']))
        medFilterAccX = signal.medfilt(accData[:,1],11)
        medFilterAccY = signal.medfilt(accData[:,2],11)
        medFilterAccZ = signal.medfilt(accData[:,3],11)
        
        b, a = signal.butter(3, 10.0/25, btype='low')
        butterAccX = signal.filtfilt(b,a,medFilterAccX)
        butterAccY = signal.filtfilt(b,a,medFilterAccY)
        butterAccZ = signal.filtfilt(b,a,medFilterAccZ)
        
        features.append((corrcoef(butterAccX,butterAccY))[1,:].tolist())
        features.append((corrcoef(butterAccX,butterAccZ))[1,:].tolist())
        features.append((corrcoef(butterAccY,butterAccZ))[1,:].tolist())
        
        absY = abs(butterAccY)
        #features.append((sum(absY)/len(absY)-min(accData[:,2]))/(max(accData[:,2])-min(accData[:,2])))
        #features.append(power(max(absY)-min(absY),1/4.0))
        features.append(power(sum(absY)/len(absY),1/3.0))
        '''
        buckets = linspace(0, 2, num=9)
        
        accData = array(readNumericData(entry['accfile']))
        accData = accData[150:(len(accData[:,0])-60),:]
        totalAcc = accData[:,1] + accData[:,2] + accData[:,3]
        totalAcc = signal.medfilt(totalAcc,11)
        '''
        medFilterAccX = signal.medfilt(accData[:,1],11)
        medFilterAccY = signal.medfilt(accData[:,2],11)
        medFilterAccZ = signal.medfilt(accData[:,3],11)
        
        b, a = signal.butter(3, 10.0/25, btype='low')
        butterAccX = signal.filtfilt(b,a,medFilterAccX)
        butterAccY = signal.filtfilt(b,a,medFilterAccY)
        butterAccZ = signal.filtfilt(b,a,medFilterAccZ)
        totalAcc=signal.filtfilt(b,a,totalAcc)
        features.append(mean(butterAccX))
        features.append(mean(butterAccY))
        features.append(mean(butterAccZ))
        features.append(std(butterAccX))
        features.append(std(butterAccY))
        features.append(std(butterAccZ))
        plt.plot(range(1,len(butterAccZ)+1),butterAccZ)
        plt.show()
        #features += accData.std(axis=0)[1:].tolist()
        '''
        #totalAcc = butterAccX+butterAccY+butterAccZ
        #plt.plot(range(1,len(totalAcc)+1),totalAcc)
        #plt.show()
        #features+=mean(totalAcc)
        #features+=mean(square(accData[:,1]))
        #features+=mean(square(accData[:,2]))
        #features+=mean(square(accData[:,3]))
        #wavelet = signal.ricker
        #widths = arange(1, 4)
        #peakind = signal.find_peaks_cwt(totalAcc, widths)
        #features=peakind
        #x=[]
        #x.append(peakind[1] - peakind[0])
        #for i in range(2,len(peakind)):
        #    x.append(peakind[i]-peakind[i-1])
        #features.append(mean(x))
        #features+=((signal.cwt(totalAcc,wavelet,widths))[1,:]).tolist()
        #features=x
        #features.append(sum(abs(signal.cwt(totalAcc, wavelet, widths))))
        #print features
        #Pxx_den = signal.welch(totalAcc, 100, nperseg=1024)
        #features+=mean(square(Pxx_den))
        '''
        model = ap.ARMA(totalAcc)
        result=model.fit(order=(2,1),trend='c',disp=-1)
        features+=sum(result.params)
        '''
        
        seqLen = float(size(totalAcc))
        features.append(size(totalAcc[totalAcc>=buckets[-1]])/seqLen)
        for j in range(size(buckets)-1):
            upperBound = totalAcc<buckets[j+1]
            lowerBound = totalAcc>=buckets[j]
            features.append(size(totalAcc[lowerBound & upperBound])/seqLen)
        
    '''
    if config['data-filters']['gyrofile']:
        gyroData = array(readNumericData(entry['gyrofile']))
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
    '''