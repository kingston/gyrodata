#!/usr/bin/env python

from mpl_toolkits.mplot3d import Axes3D
from itertools import product, combinations
import numpy as np
import matplotlib.pyplot as plt
import sys, os, re, time

import process

dataPortion = 1

# import gyrodata from parent directory
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import gyrodata
import data as plotdata

from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

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

    accData, gyroData = process.cleanData(accData, gyroData)
    # process data
    accData, gyroData = process.processData(accData, gyroData)

    # take sample of data
    accData = accData[:len(accData) * dataPortion, :]
    gyroData = gyroData[:len(gyroData) * dataPortion, :]

    # plot accelerometer/gyroscope
    X = accData[:, 0]
    #X = range(1,len(accData[:,0])+1)

    # extract sample number
    #sample = re.search('[0-9]{5,7}', entry['accfile']).group(0)
    sample = entry['person']
    print entry

    show3D = False

    if show3D:
        # animate motion
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.set_aspect("equal")
        r = [-1, 1]
        for s, e in combinations(np.array(list(product(r,r,r))), 2):
            if np.sum(np.abs(s-e)) == r[1]-r[0]:
                ax.plot3D(*zip(s,e), color="b")
        for pt in gyroData:
            print pt
            a = Arrow3D([0,1],[0,1],[0,1], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
            ax.add_artist(a)

            plt.show()
            text = raw_input("Press enter for next one...")
    else:
        f, (ax1, ax2) = plt.subplots(2, 1) #, sharex=True)
        ax1.set_title(entry['device'] + ' - ' + sample + ' - accelerometer')
        ax1.plot(X, accData[:, 1], 'r', label='x')
        ax1.plot(X, accData[:, 2], 'g', label='y')
        ax1.plot(X, accData[:, 3], 'b', label='z')

        ax1.legend()

        X = gyroData[:, 0]
        #X = range(1,len(gyroData[:,0])+1)
        #sample = re.search('[0-9]{5,7}', entry['gyrofile']).group(0)
        ax2.set_title(entry['person'] + ' - ' + sample + ' - gyroscope')
        ax2.plot(X, gyroData[:, 1], 'r', label='z')
        ax2.plot(X, gyroData[:, 2], 'g', label='x')
        ax2.plot(X, gyroData[:, 3], 'b', label='y')

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
