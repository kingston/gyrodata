#!/usr/bin/env python

import os, yaml
from optparse import OptionParser
import gyrodata
from numpy import *

def readNumericData(path):
    data = gyrodata.readCsvData(path)
    return [[float(x or 0) for x in l] for l in data]

def extractFeatures(entry, config):
    if config['data-filters']['accfile']:
        accData = array(readNumericData(entry['accfile']))
    if config['data-filters']['gyrofile']:
        gyroData = array(readNumericData(entry['gyrofile']))

    return accData.max(axis=0)[1:]

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
