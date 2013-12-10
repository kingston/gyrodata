#!/usr/bin/env python

import os, yaml, random
from optparse import OptionParser
from gyroconfig import GyroConfig
import gyrodata
from numpy import *
import kingstondev, fanhaldev, daviddev, daviddev1, daviddev2, daviddev3, basic, fdev, kingston

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(entry, config):
    features = []
    featureConfig = config.getConfig('features')

    if featureConfig['kingstonreal']:
        kingston.extractFeatures(features, entry, config)

    if featureConfig['kingston']:
        kingstondev.extractFeatures(features, entry, config)

    if featureConfig['fanhal']:
        fanhaldev.extractFeatures(features, entry, config)

    if featureConfig['david']:
        daviddev.extractFeatures(features, entry, config)
    
    if featureConfig['david1']:
        daviddev1.extractFeatures(features, entry, config)
        
    if featureConfig['david2']:
        daviddev2.extractFeatures(features, entry, config)
        
    if featureConfig['david3']:
        daviddev3.extractFeatures(features, entry, config)
        
    if featureConfig['basic']:
        basic.extractFeatures(features, entry, config)

    if featureConfig['fdev']:
        fdev.extractFeatures(features, entry, config)
        
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

    config = GyroConfig.load(options.config)

    data = gyrodata.readMetadata(args[0])
    features = [extractFeatures(entry, config) for entry in data]
    gyrodata.writeCsvData(features, options.output)
    
if __name__ == '__main__':
    main()
