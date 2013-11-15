#!/usr/bin/env python

import os, sys, yaml, random, math
from optparse import OptionParser
import gyrodata, datamodel
from sklearn import cross_validation
from numpy import *

def most_common_count (lst):
    return max(((item, lst.count(item)) for item in set(lst)), key=lambda a: a[1])[1]

def getModel(config):
    modelSettings = config['model']
    modelType = modelSettings['type']

    models = {
        "gaussian-naive-bayes": datamodel.predictWithGaussianNaiveBayes,
        "logistic-regression": datamodel.predictWithLogisticRegression,
        "svc": datamodel.predictWithSVC,
        "svr": datamodel.predictWithSVR,
    }
    if modelType in models:
        return models[modelType]
    else:
        sys.exit("Unknown model type: " + modelType)

def trainTest(config, X, Y, testFeatures, testOutput, showBaseline=False):
    model = getModel(config)
    predicted = model(config, X, Y, testFeatures)
    isDiscrete = model.isDiscrete

    if isDiscrete:
        numCorrect = len([i for i, j in zip(predicted, testOutput) if i == j])
        if showBaseline:
            baseline = float(most_common_count(testOutput)) / len(testOutput)
            print "Baseline: " + "%.2f" % (baseline * 100) + "%"
        accuracy = float(numCorrect) / len(testOutput)
    else:
        if showBaseline:
            avg = float(sum(testOutput)) / len(testOutput)
            baselineDifferences = sum([abs(avg - real) for real in testOutput])
            baseline = float(baselineDifferences) / len(testOutput)
            print "Baseline Difference: " + "%.2f" % baseline
        sumofdifferences = sum([abs(pred - real) for pred, real in zip(predicted, testOutput)])
        accuracy = float(sumofdifferences) / len(testOutput)
    return accuracy

def runWithKFold(config, features, output):
    k = config['validation']['k-fold']['k']
    if config['validation']['k-fold']['stratify']:
        skf = cross_validation.StratifiedKFold(output, n_folds = k)
    else:
        skf = cross_validation.KFold(len(output), n_folds = k)

    X = array(features)
    Y = array(output)
    accuracies = []
    for train_index, test_index in skf:
        X_train, X_test = X[train_index], X[test_index]
        Y_train, Y_test = Y[train_index], Y[test_index]

        accuracies.append(trainTest(config, X_train, Y_train, X_test, Y_test))
    return sum(accuracies) / len(accuracies)

def runWithHoldout(config, features, output):
    n = len(features)
    trainSize = config['validation']['holdout']['trainSize']
    sep = int(n * trainSize)
    trainFeatures = features[0:sep]
    testFeatures = features[sep:]
    trainOutput = output[0:sep]
    testOutput = output[sep:]

    return trainTest(config, trainFeatures, trainOutput, testFeatures, testOutput, True)

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
    elif validationType == "k-fold":
        return runWithKFold(config, features, output)
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
    model = getModel(config)

    # normalize features/output (may be false assumption)
    features = [[float(x) for x in l] for l in features]
    if model.isDiscrete:
        output = [int(l[0]) for l in output]
    else:
        output = [float(l[0]) for l in output]

    print ""
    accuracy = runData(config, features, output)
    # Output accuracy correctly
    if model.isDiscrete:
        print "Accuracy: " + "%.2f" % (accuracy * 100) + "%"
    else:
        print "Average Absolute Error: " + "%.2f" % accuracy

def log(config, message):
    if 'verbose' in config and config['verbose']:
        print message


if __name__ == '__main__':
    main()
