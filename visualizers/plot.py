#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys, os, re

import process

dataPortion = 1

# import gyrodata from parent directory
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import gyrodata
import data as plotdata

def promptForEntry(meta):
    text = raw_input("Enter person ID to plot: ")
    while True:
        if not text:
            sys.exit()
        entry = data.getEntryById(meta, text)
        if entry:
            return entry
        else:
            text = raw_input("Invalid ID. Please try again: ")

def plotEntry(entry):
    accData = np.array(plotdata.readNumericData(entry['accfile']))
    gyroData = np.array(plotdata.readNumericData(entry['gyrofile']))

    accData = accData[:len(accData) * dataPortion, :]
    gyroData = gyroData[:len(gyroData) * dataPortion, :]

    accData, gyroData = process.normalizeDatasets(accData, gyroData)
    # process data
    accData, gyroData = process.processData(accData, gyroData)

    # plot accelerometer/gyroscope
    X = accData[:, 0]
    X = range(1,len(accData[:,0])+1)

    # extract sample number
    #sample = re.search('[0-9]{5,7}', entry['accfile']).group(0)
    sample = entry['person']

    f, (ax1, ax2) = plt.subplots(2, 1) #, sharex=True)
    ax1.set_title(entry['person'] + ' - ' + sample + ' - accelerometer')
    ax1.plot(X, accData[:, 1], 'r', label='x')
    ax1.plot(X, accData[:, 2], 'g', label='y')
    ax1.plot(X, accData[:, 3], 'b', label='z')

    ax1.legend()

    X = gyroData[:, 0]
    X = range(1,len(gyroData[:,0])+1)
    #sample = re.search('[0-9]{5,7}', entry['gyrofile']).group(0)
    ax2.set_title(entry['person'] + ' - ' + sample + ' - gyroscope')
    #ax2.plot(X, gyroData[:, 1], 'r', label='x')
    ax2.plot(X, gyroData[:, 2], 'g', label='y')
    #ax2.plot(X, gyroData[:, 3], 'b', label='z')

    ax2.legend()

def main():
    metapath = "../data/gyroscoper.csv"
    meta = gyrodata.readMetadata(metapath)

    plt.ion()

    filteredMeta = meta
    #filteredMeta = [entry for entry in meta if 'walk' in entry['activityFolder'] and 'waist' in entry['position'] and entry['gyrofile']]
    for entry in filteredMeta:
        plt.close()
        plt.clf()
        plotEntry(entry)
        plt.show()
        text = raw_input("Press enter for next one...")
        if text == 'q':
            break

    while True:
        plt.close()
        entry = promptForEntry(meta)
        plt.clf()
        plotEntry(entry)
        plt.show()

if __name__ == '__main__':
    main()
