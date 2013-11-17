#Library for testing on different models
from numpy import *
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.lda import LDA
from sklearn.qda import QDA
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
def predictWithRandomForest(config, X, Y, testFeatures):
    clf = RandomForestClassifier()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse
def predictWithLDA(config, X, Y, testFeatures):
    clf = LDA()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse
def predictWithQDA(config, X, Y, testFeatures):
    clf = QDA()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse
def predictWithSVC(config, X, Y, testFeatures):
    svcConfig = config.getConfig('model/svc')
    kernel = svcConfig.get('kernel', 'rbf')
    if kernel == 'sigmoid':
        clf = svm.SVC(C=1.0, kernel='sigmoid', degree=2, gamma=1.0, coef0=0.0, shrinking=True, probability=False, tol=0.0001, cache_size=200, class_weight=None, verbose=False)
    else:
        clf = svm.SVC(kernel=kernel)
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@continuousResponse
def predictWithSVR(config, X, Y, testFeatures):
    clf = svm.SVR()
    clf.fit(X, Y)
    return clf.predict(testFeatures)
