#Library for testing on different models
from numpy import *
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.lda import LDA
from sklearn.qda import QDA
from sklearn import svm
from sklearn import neighbors

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
    clf = svm.SVC()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@continuousResponse
def predictWithSVR(config, X, Y, testFeatures):
    clf = svm.SVR()
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse    
def predictWithSCVsigmoid(config, X, Y, testFeatures):
    clf = svm.SVC(C=1.0, kernel='sigmoid', degree=2, gamma=3.0, coef0=0.0, shrinking=True, probability=False, tol=0.0001, cache_size=200, class_weight=None, verbose=False)
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse
def predictWithKNN(config, X, Y, testFeatures):
    clf=neighbors.KNeighborsClassifier(4)
    clf.fit(X,Y)
    return clf.predict(testFeatures)