#Library for testing on different models
from numpy import *
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

def predictWithGaussianNaiveBayes(config, X, Y, testFeatures):
    clf = GaussianNB()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

def predictWithLogisticRegression(config, X, Y, testFeatures):
    clf = LogisticRegression()
    clf.fit(X, Y)
    return clf.predict(testFeatures)
