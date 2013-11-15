#!/usr/bin/env python

import os, yaml, random
from optparse import OptionParser
import gyrodata, datamodel

def parseEntry(entry, variable):
    if variable == "age":
        return float(entry['age'].split(';')[0])
    return float(entry[variable])

def extractMetadata(data, config):
    outputConfig = config['output']
    variable = outputConfig['variable']
    isBucketed = outputConfig['is-bucketed']

    metadata = {}

    if isBucketed:
        bucketConfig = outputConfig['buckets']
        # find bucket points
        outputs = sorted([parseEntry(entry, variable) for entry in data])
        numOutputs = len(outputs)
        numBuckets = bucketConfig['num']
        metadata['splits'] = [outputs[i * (numOutputs / numBuckets)] for i in range(1, numBuckets)]
    return metadata

def extractOutput(entry, metadata, config):
    outputConfig = config['output']
    variable = outputConfig['variable']
    isBucketed = outputConfig['is-bucketed']
    output = parseEntry(entry, variable)
    if isBucketed:
        i = 0
        for split in metadata['splits']:
            if output <= split:
                break
            i += 1
        output = i
    return [output]

def main():
    parser = OptionParser(usage="usage: %prog [options] data")

    parser.add_option("-c", "--config-file",
            action="store",
            dest="config",
            default="gold.yml",
            help="Configuration file for outputs",)

    parser.add_option("-o", "--output",
            action="store",
            dest="output",
            default="filtered.csv",
            help="Output file of outputs",)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    try:
        with open(options.config, 'r') as configFile:
            config = yaml.load(configFile)
    except IOError:
        sys.exit("Unable to find configuration file " + options.config)

    data = gyrodata.readMetadata(args[0])
    metadata = extractMetadata(data, config)
    output = [extractOutput(entry, metadata, config) for entry in data]
    gyrodata.writeCsvData(output, options.output)
    
if __name__ == '__main__':
    main()
