#!/usr/bin/env python

import os, yaml
from optparse import OptionParser
import gyrodata

def log(config, message):
    if 'verbose' in config and config['verbose']:
        print message

def runData(config, features, output):
    return 1

def main():
    parser = OptionParser(usage="usage: %prog [options] feature_file output_file")

    parser.add_option("-c", "--config-file",
            action="store",
            dest="config",
            default="gold.yml",
            help="Configuration file",)

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("wrong number of arguments")

    try:
        with open(options.config, 'r') as configFile:
            config = yaml.load(configFile)
    except IOError:
        sys.exit("Unable to find configuration file " + options.config)

    features = gyrodata.readCsvData(args[0])
    output = gyrodata.readCsvData(args[1])

    accuracy = runData(config, features, output)
    print ""
    print "Accuracy: " + "%.2f" % (accuracy * 100) + "%"

if __name__ == '__main__':
    main()
