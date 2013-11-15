#Library for testing on different models
import numpy as np
from sklearn.naive_bayes import GaussianNB

def predictWithGaussianNaiveBayes(config, X, Y, testFeatures):
    clf = GaussianNB()
    clf.fit(X, Y)
    return clf.predict(testFeatures)
