#Library for testing on different models
from numpy import *
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm

# Function decorators for tagging methods

def discreteResponse(func):
    func.isDiscrete = True
    return func

def continuousResponse(func):
    func.isDiscrete = False
    return func

@discreteResponse
def predictWithGaussianNaiveBayes(config, X, Y, testFeatures):
    clf = GaussianNB()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse
def predictWithLogisticRegression(config, X, Y, testFeatures):
    clf = LogisticRegression()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse
def predictWithSVC(config, X, Y, testFeatures):
    clf = svm.SVC()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@continuousResponse
def predictWithSVR(config, X, Y, testFeatures):
    clf = svm.SVR()
    clf.fit(X, Y)
    return clf.predict(testFeatures)
