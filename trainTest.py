#!/usr/bin/env python

import os, sys, yaml, random
from optparse import OptionParser
import gyrodata, datamodel

def most_common_count (lst):
    return max(((item, lst.count(item)) for item in set(lst)), key=lambda a: a[1])[1]

def trainTest(config, X, Y, testFeatures, testOutput):
    modelSettings = config['model']
    modelType = modelSettings['type']

    # normalize input
    X = [[float(x) for x in l] for l in X]
    testFeatures = [[float(x) for x in l] for l in testFeatures]
    # normalize output (only one output for all cases we have)
    Y = [int(y[0]) for y in Y]
    testOutput = [int(y[0]) for y in testOutput]

    if modelType == "gaussian-naive-bayes":
        predicted = datamodel.predictWithGaussianNaiveBayes(config, X, Y, testFeatures)
        isDiscrete = True
    elif modelType == "logistic-regression":
        predicted = datamodel.predictWithLogisticRegression(config, X, Y, testFeatures)
        isDiscrete = True
    else:
        sys.exit("Unknown model type: " + modelType)

    numCorrect = len([i for i, j in zip(predicted, testOutput) if i == j])
    if isDiscrete:
        baseline = float(most_common_count(testOutput)) / len(testOutput)
        print "Baseline: " + "%.2f" % (baseline * 100) + "%"
    return float(numCorrect) / len(testOutput)

def runWithHoldout(config, features, output):
    n = len(features)
    trainSize = config['validation']['holdout']['trainSize']
    sep = int(n * trainSize)
    trainFeatures = features[0:sep]
    testFeatures = features[sep:]
    trainOutput = output[0:sep]
    testOutput = output[sep:]

    return trainTest(config, trainFeatures, trainOutput, testFeatures, testOutput)

def runData(config, features, output):
    validationSettings = config['validation']
    # Sort if needs be
    if validationSettings['randomizeSort']:
        data = zip(features, output)
        if 'randomSeed' in validationSettings and validationSettings['randomSeed']:
            random.seed(validationSettings['randomSeed'])
        random.shuffle(data)
        features, output = zip(*data)
    # Run with random type
    validationType = validationSettings['type']
    if validationType == "holdout":
        return runWithHoldout(config, features, output)
    else:
        sys.exit("Unknown validation type: " + validationType)

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

    print ""
    accuracy = runData(config, features, output)
    print "Accuracy: " + "%.2f" % (accuracy * 100) + "%"

def log(config, message):
    if 'verbose' in config and config['verbose']:
        print message


if __name__ == '__main__':
    main()
