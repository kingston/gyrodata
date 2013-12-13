#!/usr/bin/env python

import os, sys, yaml, random, math
from optparse import OptionParser
import gyrodata, datamodel
from gyroconfig import GyroConfig
import sklearn
from sklearn import cross_validation
from sklearn import preprocessing
from numpy import *
from distutils.version import StrictVersion
from matplotlib.mlab import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
import csv

metadataPath = None
cachedData = None
def getMetadata():
    if metadataPath is None:
        return None
    global cachedData
    if not cachedData:
        data = gyrodata.readMetadata(metadataPath)
        cachedData = dict(zip([e['id'] for e in data], data))
    return cachedData

def most_common_count (lst):
    return max(((item, lst.count(item)) for item in set(lst)), key=lambda a: a[1])[1]

def getModel(config):
    modelSettings = config['model']
    modelType = modelSettings['type']

    models = {
        "gaussian-naive-bayes": datamodel.predictWithGaussianNaiveBayes,
        "logistic-regression": datamodel.predictWithLogisticRegression,
        "random-forest": datamodel.predictWithRandomForest,
        "svc": datamodel.predictWithSVC,
        "lda": datamodel.predictWithLDA,
        "qda": datamodel.predictWithQDA,
        "svr": datamodel.predictWithSVR,
        "knn": datamodel.predictWithKNN,
        "perceptron": datamodel.predictWithPerceptron,
        "AdaBoost": datamodel.predictWithAdaBoost,
        "lasso": datamodel.predictWithLasso,
        "gradient-boosting": datamodel.predictWithGradientBoosting,
        "extra-trees": datamodel.predictWithExtraTrees,
    }
    if modelType in models:
        return models[modelType]
    else:
        sys.exit("Unknown model type: " + modelType)

# use only the first value of the output (excluding the ID) by default
def normalizeOutput(config, output):
    model = getModel(config)
    if model.isDiscrete:
        output = [int(l[1]) for l in output]
    else:
        output = [float(l[1]) for l in output]
    return output

def printBaseline(config, trainOutput, testOutput):
    model = getModel(config)
    isDiscrete = model.isDiscrete
    if isDiscrete:
        # assuming outputs are all non-negative
        mostCommon = bincount(trainOutput).argmax()
        baseline = len([i for i in testOutput if i == mostCommon]) / float(len(testOutput))
        print "Baseline: " + "%.2f" % (baseline * 100) + "%"
    else:
        avg = float(sum(trainOutput)) / len(trainOutput)
        baselineDifferences = sum([abs(avg - real) for real in testOutput])
        baseline = float(baselineDifferences) / len(testOutput)
        print "Baseline Difference: " + "%.2f" % baseline

def printConfusion(config, confusion):
    if config.getConfig('report/showConfusion'):
        print "Confusion matrix:"
        print confusion
        for i in range(0,confusion.shape[0]):
            if confusion.sum(axis=0)[i] != 0:
                print "Bucket " + "%.0f"%float(i) + " accuracy: " + "%.2f"%float(confusion[i][i]/confusion.sum(axis=0)[i] * 100) + "%"

def trainTest(config, X, Y, testFeatures, testOutput, showBaseline=False, confusion=None):
    trainIDs = [l[0] for l in Y]
    testIDs = [l[0] for l in testOutput]
    
    outputConfig = config['output']
    bucketConfig = outputConfig['buckets']
    numBuckets = bucketConfig['num']

    Y = normalizeOutput(config, Y)
    testOutput = normalizeOutput(config, testOutput)

    model = getModel(config)
    predicted = model(config, X, Y, testFeatures)
    isDiscrete = model.isDiscrete
    if confusion is not None:
    	for i in xrange(len(predicted)):
    		confusion[predicted[i]][testOutput[i]]+=1
    isDiscrete = model.isDiscrete
    
    numCorrect = len([i for i, j in zip(predicted, testOutput) if i == j])
    reportConfig = config.getConfig('report')
    if reportConfig.get('showIncorrect', False):
        data = getMetadata()
        for i in xrange(len(testOutput)):
            if testOutput[i] != predicted[i]:
                entry = data[testIDs[i]]
                output = "Incorrect entry:"
                output += " prediction=" + str(predicted[i])
                output += " output=" + str(testOutput[i])
                output += " ("
                attrOutput = ""
                for attr in reportConfig.get('incorrectAttrs', []):
                    attrOutput += "," + attr + "=" + entry[attr]
                output += attrOutput.strip(',')
                output += ")"
                print output
    showBaseline = reportConfig.get('showBaseline', False)
    if isDiscrete:
        accuracy = float(numCorrect) / len(testOutput)
    else:
        sumofdifferences = sum([abs(pred - real) for pred, real in zip(predicted, testOutput)])
        accuracy = float(sumofdifferences) / len(testOutput)
    return accuracy

def runWithSameTrainTest(config, features, output):
    return trainTest(config, features, output, features, output)

def runWithCrossValidation(config, features, output, skf, confusion=None):
    outputConfig = config['output']
    bucketConfig = outputConfig['buckets']
    numBuckets = bucketConfig['num']
    print numBuckets
    
    X = array(features)
    Y = array(output)
    accuracies = []
    for train_index, test_index in skf:
        X_train, X_test = X[train_index], X[test_index]
        Y_train, Y_test = Y[train_index], Y[test_index]

        accuracies.append(trainTest(config, X_train, Y_train, X_test, Y_test, confusion=confusion))

    if config.get('report/showBaseline', True):
        # just aggregate the general baseline
        normalizeY = normalizeOutput(config, Y)
        printBaseline(config, normalizeY, normalizeY) 
    return sum(accuracies) / len(accuracies)

def runWithLeaveOneOut(config, features, output):
    outputConfig = config['output']
    bucketConfig = outputConfig['buckets']
    numBuckets = bucketConfig['num']
    print numBuckets
    skf = cross_validation.LeaveOneOut(len(features))
    confusion = zeros((numBuckets,numBuckets))
    accuracy = runWithCrossValidation(config, features, output, skf, confusion=confusion)
    printConfusion(config, confusion)
    return accuracy

def runWithKFold(config, features, output):
    outputConfig = config['output']
    bucketConfig = outputConfig['buckets']
    numBuckets = bucketConfig['num']
    kConfig = config.getConfig('validation/k-fold')
    k = kConfig.get('k', 10)
    if StrictVersion(sklearn.__version__) > StrictVersion('0.12'):
        if kConfig.get('stratify', False):
            skf = cross_validation.StratifiedKFold(normalizeOutput(config, output), n_folds = k)
        else:
            skf = cross_validation.KFold(len(output), n_folds = k)
    else:
        if kConfig.get('stratify', False):
            skf = cross_validation.StratifiedKFold(normalizeOutput(config, output), k)
        else:
            skf = cross_validation.KFold(len(output), k)

    confusion=zeros((numBuckets,numBuckets))
    accuracy = runWithCrossValidation(config, features, output, skf, confusion=confusion)
    printConfusion(config, confusion)
    return accuracy

def runWithHoldout(config, features, output):
    outputConfig = config['output']
    bucketConfig = outputConfig['buckets']
    numBuckets = bucketConfig['num']
    n = len(features)
    trainSize = config.get('validation/holdout/trainSize')
    sep = int(n * trainSize)
    trainFeatures = features[0:sep]
    testFeatures = features[sep:]
    trainOutput = output[0:sep]
    testOutput = output[sep:]

    confusion=zeros((numBuckets,numBuckets))
    accuracy = trainTest(config, trainFeatures, trainOutput, testFeatures, testOutput, confusion=confusion)
    printConfusion(config, confusion)
    return accuracy

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
    elif validationType == "loo":
        return runWithLeaveOneOut(config, features, output)
    elif validationType == "same":
        return runWithSameTrainTest(config, features, output)
    else:
        sys.exit("Unknown validation type: " + validationType)

def main():
    parser = OptionParser(usage="usage: %prog [options] feature_file output_file meta_file")

    parser.add_option("-c", "--config-file",
            action="store",
            dest="config",
            default="gold.yml",
            help="Configuration file",)

    (options, args) = parser.parse_args()

    if len(args) != 3:
        parser.error("wrong number of arguments")

    config = GyroConfig.load(options.config)

    features = gyrodata.readCsvData(args[0])
    output = gyrodata.readCsvData(args[1])
    # global variable for simplicity
    global metadataPath
    metadataPath = args[2]
    model = getModel(config)

    # normalize features/output (may be false assumption)
    features = [[float(x) for x in l] for l in features]

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
