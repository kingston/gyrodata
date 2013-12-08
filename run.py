#!/usr/bin/env python

# Processes the data and tests it for a given configuration file

import os, sys, yaml, string, random
from optparse import OptionParser

# taken from
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def safeRun(command):
    if 'PYTHON_FOLDER' in os.environ and command.startswith('python '):
        command = os.environ['PYTHON_FOLDER'] + command
    r = os.system(command)
    if r != 0:
        sys.exit("Error running command: " + command)

def runData(config, options):
    # Create temporary prefix
    prefix = "tmp/" + id_generator()
    filteredCsv = prefix + "_filtered.csv"
    featuresCsv = prefix + "_features.csv"
    outputCsv = prefix + "_output.csv"

    # Create filter data
    safeRun("python filterMetadata.py -c %s -o %s data/meta.csv" % (options.config, filteredCsv))

    # Extract features and output
    safeRun("python extractFeatures.py -c %s -o %s %s" % (options.config, featuresCsv, filteredCsv))
    safeRun("python extractOutput.py -c %s -o %s %s" % (options.config, outputCsv, filteredCsv))

    # Test data
    safeRun("python trainTest.py -c %s %s %s %s" % (options.config, featuresCsv, outputCsv, filteredCsv))

    # Remove all prefixed files
    safeRun("rm -f tmp/%s*" % prefix)

def main():
    parser = OptionParser(usage="usage: %prog [options]")

    parser.add_option("-c", "--config-file",
            action="store",
            dest="config",
            default="gold.yml",
            help="Configuration file (defaults to gold)",)

    parser.add_option("-m", "--meta-generate",
            action="store_true",
            dest="meta",
            help="Force meta data file regeneration (from corpus)",)

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("wrong number of arguments")

    # Check for valid startup
    if not os.path.isdir("corpus"):
        sys.exit("No corpus found. Please extract or symlink corpus to corpus")

    if not os.path.isdir("data"):
        os.makedirs("data")

    if not os.path.isdir("tmp"):
        os.makedirs("tmp")

    # Parse configuration file
    try:
        with open(options.config, 'r') as configFile:
            config = yaml.load(configFile)
    except IOError:
        sys.exit("Unable to find configuration file " + options.config)

    # Generate meta file if needs be
    if options.meta or not os.path.exists("data/meta.csv"):
        print "Gathering metadata..."
        safeRun("./env/bin/python extractMetadata.py -o data/meta.csv corpus")
    
    runData(config, options)

    print("Data runner has successfully ran!")

if __name__ == '__main__':
    main()
