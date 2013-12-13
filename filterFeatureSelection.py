#!/usr/bin/env python

# Uses filter feature selection to get most important features

import os, sys, yaml, random, math
from optparse import OptionParser
import gyrodata, datamodel
from gyroconfig import GyroConfig
import sklearn
from sklearn import cross_validation
from sklearn import preprocessing
import numpy as np
from distutils.version import StrictVersion
from matplotlib.mlab import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
from numpy.linalg import *
import csv

def runData(config, features, output):
    # format output
    output = [int(l[1]) for l in output]
    outputClassSize = len(set(output))

    # arraify features and output
    features = np.array(features)
    output = np.array(output)

    results = []
    for i in range(features.shape[1]):
        xs = features[:, i]
        # normalize data
        xs = (xs - xs.mean()) / xs.std()

        # condition data on output
        means = []
        print np.histogram(xs, len(xs) / outputClassSize / 3)
        for o in range(outputClassSize):
            idx = np.where(output == o)[0] 
            relevantFeatures = xs[idx]
            # turn into histogram

            means.append(relevantFeatures.mean())
        results.append((np.array(means).std(), i))

    results = sorted(results, key=lambda e: e[0], reverse=True)
    for result in results:
        print "Feature " + str(result[1] + 1) + ": " + str(result[0])

def main():
    parser = OptionParser(usage="usage: %prog [options] feature_file output_file meta_file")

    parser.add_option("-c", "--config-file",
            action="store",
            dest="config",
            default="gold.yml",
            help="Configuration file",)

    (options, args) = parser.parse_args()

    if len(args) != 3:
        parser.error("wrong number of arguments")

    config = GyroConfig.load(options.config)

    features = gyrodata.readCsvData(args[0])
    output = gyrodata.readCsvData(args[1])

    # normalize features/output (may be false assumption)
    features = [[float(x) for x in l] for l in features]

    print ""
    runData(config, features, output)

def log(config, message):
    if 'verbose' in config and config['verbose']:
        print message


if __name__ == '__main__':
    main()
