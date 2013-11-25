#!/usr/bin/env python

import data
import numpy as np
import matplotlib.pyplot as plt
import sys

import process

dataPortion = 0.2

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
    accData = np.array(data.readNumericData(entry['accfile']))
    gyroData = np.array(data.readNumericData(entry['gyrofile']))

    accData = accData[:len(accData) * dataPortion, :]
    gyroData = gyroData[:len(gyroData) * dataPortion, :]

    accData, gyroData = process.normalizeDatasets(accData, gyroData)
    # absolute reference data
    gyroData = process.absoluteReferenceAccData(accData, gyroData)

    # plot accelerometer/gyroscope
    X = accData[:, 0]

    f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.set_title(entry['person'] + ' - accelerometer')
    ax1.plot(X, accData[:, 1])
    ax1.plot(X, accData[:, 2])
    ax1.plot(X, accData[:, 3])

    X = gyroData[:, 0]
    ax2.set_title(entry['person'] + ' - gyroscope')
    ax2.plot(X, gyroData[:, 1])
    ax2.plot(X, gyroData[:, 2])
    ax2.plot(X, gyroData[:, 3])

def main():
    metapath = "../data/meta.csv"
    meta = data.readMetadata(metapath)

    plt.ion()

    filteredMeta = [entry for entry in meta if 'walk' in entry['activityFolder'] and 'waist' in entry['position'] and entry['gyrofile']]
    for entry in filteredMeta:
        plt.clf()
        plotEntry(entry)
        plt.show()
        text = raw_input("Press enter for next one...")
        if text == 'q':
            break

    while True:
        entry = promptForEntry(meta)
        plt.clf()
        plotEntry(entry)
        plt.show()

if __name__ == '__main__':
    main()
