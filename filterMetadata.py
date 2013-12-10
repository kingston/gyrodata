#!/usr/bin/env python

import os, yaml
from optparse import OptionParser
import gyrodata
from itertools import groupby
from operator import itemgetter

def isValidEntry(entry, config):
    filters = config['data-filters']
    identicalAttributes = ['gender']
    containsAttributes = ['activity', 'position', 'activityFolder', 'mount', 'direction']
    presentAttributes = ['accfile', 'gyrofile', 'weight', 'height', 'age']

    for attr in identicalAttributes:
        if attr in filters:
            if filters[attr] and filters[attr] != entry[attr]:
                return False

    for attr in containsAttributes:
        if attr in filters:
            if filters[attr] and filters[attr] not in entry[attr]:
                return False

    for attr in presentAttributes:
        if attr in filters:
            if filters[attr] and filters[attr] and not entry[attr]:
                return False
    
    if 'extreme' in filters:
        variable = filters['extreme']
        splits = config['output']['buckets']['splits']
        if float(entry[variable]) >= float(splits[0]) and float(entry[variable]) <= float(splits[1]):
            return False

    def checkValidFile(path, numKeys, minRecords):
            # check for valid values in acc file
            data = gyrodata.readCsvData(path)
            if len(data) < minRecords:
                return False
            # count all non-falsy keys
            keys = [len([e for e in l if e]) for l in data]
            return max(keys) == numKeys

    if filters['accfile'] and not checkValidFile(entry['accfile'], 4, filters['minRecords']):
        return False
    if filters['gyrofile'] and not checkValidFile(entry['gyrofile'], 4, filters['minRecords']):
        return False
    return True

def main():
    parser = OptionParser(usage="usage: %prog [options] source")

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

    # filter by person
    if config['data-filters']['unique']:
        filteredData = [group.next() for key, group in groupby(filteredData, key=itemgetter('person'))]

    print("Loaded %d entries!" % (len(filteredData)))

    gyrodata.writeMetadata(filteredData, options.output)
    
if __name__ == '__main__':
    main()
