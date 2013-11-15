#!/usr/bin/env python

import os, yaml
from optparse import OptionParser
import gyrodata

def extractOutput(entry, config):
    outputConfig = config['output']
    variable = outputConfig['variable']
    isBucketed = outputConfig['is-bucketed']
    output = entry[variable]
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
    output = [extractOutput(entry, config) for entry in data]
    gyrodata.writeCsvData(output, options.output)
    
if __name__ == '__main__':
    main()
