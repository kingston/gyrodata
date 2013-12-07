#!/usr/bin/env python

import os, sys, yaml, random, math
from optparse import OptionParser
import gyrodata, datamodel
from gyroconfig import GyroConfig
import sklearn
from sklearn import cross_validation
from numpy import *
from distutils.version import StrictVersion

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
        #"AdaBoost": datamodel.predictWithAdaBoost,
        "lasso": datamodel.predictWithLasso,
        "gradient-boosting": datamodel.predictWithGradientBoosting,
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

def trainTest(config, X, Y, testFeatures, testOutput, showBaseline=False, confusion=None):
    trainIDs = [l[0] for l in Y]
    testIDs = [l[0] for l in testOutput]

    Y = normalizeOutput(config, Y)
    testOutput = normalizeOutput(config, testOutput)

    model = getModel(config)
    predicted = model(config, X, Y, testFeatures)
    isDiscrete = model.isDiscrete
    if confusion is not None:
    	for i in xrange(len(predicted)):
    		confusion[predicted[i]][testOutput[i]]+=1
    
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
    if isDiscrete:
        if showBaseline:
            counts = zeros(3)
            for i in xrange(3):
                counts[i] = Y.count(i)
            mostCommon = argmax(counts)
            baselinePreds = ones(len(testOutput))*mostCommon
            baseline = len([i for i, j in zip(baselinePreds, testOutput) if i == j]) / float(len(testOutput))
            print "Baseline: " + "%.2f" % (baseline * 100) + "%"
        accuracy = float(numCorrect) / len(testOutput)
    else:
        if showBaseline:
            avg = float(sum(Y)) / len(Y)
            baselineDifferences = sum([abs(avg - real) for real in testOutput])
            baseline = float(baselineDifferences) / len(testOutput)
            print "Baseline Difference: " + "%.2f" % baseline
        sumofdifferences = sum([abs(pred - real) for pred, real in zip(predicted, testOutput)])
        accuracy = float(sumofdifferences) / len(testOutput)
    return accuracy

def runWithSameTrainTest(config, features, output):
    return trainTest(config, features, output, features, output, True)

def runWithCrossValidation(config, features, output, skf, confusion=None):
    X = array(features)
    Y = array(output)
    accuracies = []
    for train_index, test_index in skf:
        X_train, X_test = X[train_index], X[test_index]
        Y_train, Y_test = Y[train_index], Y[test_index]

        accuracies.append(trainTest(config, X_train, Y_train, X_test, Y_test, confusion=confusion))
    return sum(accuracies) / len(accuracies)

def runWithLeaveOneOut(config, features, output):
    skf = cross_validation.LeaveOneOut(len(features))
    confusion = zeros((3,3))
    accuracy = runWithCrossValidation(config, features, output, skf, confusion=confusion)
    print "Confusion matrix:"
    print confusion
    print "Small marginal: " + "%.2f"%float(confusion[0][0]/confusion.sum(axis=0)[0] * 100) + "%"
    print "Medium marginal: " + "%.2f"%float(confusion[1][1]/confusion.sum(axis=0)[1] * 100) + "%"
    print "Large marginal: " + "%.2f"%float(confusion[2][2]/confusion.sum(axis=0)[2] * 100) + "%"
    return accuracy

def runWithKFold(config, features, output):
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

    confusion=zeros((3,3))
    accuracy = runWithCrossValidation(config, features, output, skf, confusion=confusion)
    print "Confusion matrix:"
    print confusion
    print "Small marginal: " + "%.2f"%float(confusion[0][0]/confusion.sum(axis=0)[0] * 100) + "%"
    print "Medium marginal: " + "%.2f"%float(confusion[1][1]/confusion.sum(axis=0)[1] * 100) + "%"
    print "Large marginal: " + "%.2f"%float(confusion[2][2]/confusion.sum(axis=0)[2] * 100) + "%"
    return accuracy

def runWithHoldout(config, features, output):
    n = len(features)
    trainSize = config.get('validation/holdout/trainSize')
    sep = int(n * trainSize)
    trainFeatures = features[0:sep]
    testFeatures = features[sep:]
    trainOutput = output[0:sep]
    testOutput = output[sep:]

    confusion=zeros((3,3))
    accuracy = trainTest(config, trainFeatures, trainOutput, testFeatures, testOutput, True, confusion=confusion)
    print "Confusion matrix:"
    print confusion
    print "Small marginal: " + "%.2f"%float(confusion[0][0]/confusion.sum(axis=0)[0] * 100) + "%"
    print "Medium marginal: " + "%.2f"%float(confusion[1][1]/confusion.sum(axis=0)[1] * 100) + "%"
    print "Large marginal: " + "%.2f"%float(confusion[2][2]/confusion.sum(axis=0)[2] * 100) + "%"
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
