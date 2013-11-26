from numpy import *
from scipy import signal
import gyrodata
import statsmodels.tsa.arima_model as ap

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(features, entry, config):
    if config['data-filters']['accfile']:
        buckets = linspace(0, 2, num=5)
        accData = array(readNumericData(entry['accfile']))
        features += accData.mean(axis=0)[1:].tolist()
        features += accData.std(axis=0)[1:].tolist()
        totalAcc = sqrt((square(accData[:,1]) + square(accData[:,2]) + square(accData[:,3])))
        #features+=mean(totalAcc)
        #features+=mean(square(accData[:,1]))
        #features+=mean(square(accData[:,2]))
        #features+=mean(square(accData[:,3]))
        wavelet = signal.ricker
        widths = arange(1, 4)
        peakind = signal.find_peaks_cwt(totalAcc, widths)
        #features=peakind
        x=[]
        x.append(peakind[1] - peakind[0])
        for i in range(2,len(peakind)):
            x.append(peakind[i]-peakind[i-1])
        features+=(mean(x))
        #features+=((signal.cwt(totalAcc,wavelet,widths))[1,:]).tolist()
        #features=x
        features += sum(abs(signal.cwt(totalAcc, wavelet, widths)))
        #print features
        #Pxx_den = signal.welch(totalAcc, 100, nperseg=1024)
        #features+=mean(square(Pxx_den))
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