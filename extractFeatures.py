#!/usr/bin/env python

import os, yaml, random
from optparse import OptionParser
import gyrodata
from numpy import *
import kingstondev, fanhaldev, daviddev, kingston

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(entry, config):
    features = []
    featureConfig = config['features']

    if featureConfig['kingstonreal']:
        kingston.extractFeatures(features, entry, config)

    if featureConfig['kingston']:
        kingstondev.extractFeatures(features, entry, config)

    if featureConfig['fanhal']:
        fanhaldev.extractFeatures(features, entry, config)

    if featureConfig['david']:
        daviddev.extractFeatures(features, entry, config)

    if featureConfig['max-point']:
        if config['data-filters']['accfile']:
            accData = array(readNumericData(entry['accfile']))
            features += accData.max(axis=0)[1:].tolist()
        if config['data-filters']['gyrofile']:
            gyroData = array(readNumericData(entry['gyrofile']))
            features += gyroData.max(axis=0)[1:].tolist()

    return features

def main():
    parser = OptionParser(usage="usage: %prog [options] data")

    parser.add_option("-c", "--config-file",
            action="store",
            dest="config",
            default="gold.yml",
            help="Configuration file for features",)

    parser.add_option("-o", "--output",
            action="store",
            dest="output",
            default="filtered.csv",
            help="Output file of features",)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    try:
        with open(options.config, 'r') as configFile:
            config = yaml.load(configFile)
    except IOError:
        sys.exit("Unable to find configuration file " + options.config)

    data = gyrodata.readMetadata(args[0])
    features = [extractFeatures(entry, config) for entry in data]
    gyrodata.writeCsvData(features, options.output)
    
if __name__ == '__main__':
    main()
