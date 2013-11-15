#!/usr/bin/env python

import os, yaml
from optparse import OptionParser
import gyrodata

def isValidEntry(entry, config):
    filters = config['data-filters']
    containsAttributes = ['activity', 'position']
    for attr in containsAttributes:
        if attr in filters:
            if filters[attr] not in entry[attr]:
                return False
    return True

def main():
    parser = OptionParser(usage="usage: %prog [options]source")

    parser.add_option("-c", "--config-file",
            action="store",
            dest="config",
            default="gold.yml",
            help="Configuration file for filter",)

    parser.add_option("-o", "--output",
            action="store",
            dest="output",
            default="filtered.csv",
            help="Output file",)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    try:
        with open(options.config, 'r') as configFile:
            config = yaml.load(configFile)
    except IOError:
        sys.exit("Unable to find configuration file " + options.config)

    data = gyrodata.readMetadata(args[0])

    filteredData = [entry for entry in data if isValidEntry(entry, config)]
    gyrodata.writeMetadata(filteredData, options.output)
    
if __name__ == '__main__':
    main()
