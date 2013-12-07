#Library for testing on different models
from numpy import *
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.lda import LDA
from sklearn.qda import QDA
from sklearn import svm
from sklearn import neighbors
from sklearn import linear_model
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier

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
    clf = LDA(priors=[.5,.5])
    clf.fit(X, Y)
    return clf.predict(testFeatures)

@discreteResponse
def predictWithQDA(config, X, Y, testFeatures):
    clf = QDA(priors=[.5,.5])
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

@discreteResponse
def predictWithKNN(config, X, Y, testFeatures):
    clf=neighbors.KNeighborsClassifier(3)
    clf.fit(X,Y)
    return clf.predict(testFeatures)
    
@discreteResponse
def predictWithPerceptron(config, X, Y, testFeatures):
    clf = linear_model.Perceptron()
    clf.fit(X,Y)
    return clf.predict(testFeatures)


@discreteResponse
def predictWithAdaBoost(config, X, Y, testFeatures):
    clf = AdaBoostClassifier(n_estimators=100)
    clf.fit(X,Y)
    return clf.predict(testFeatures)
   
@continuousResponse
def predictWithLasso(config, X, Y,testFeatures):
    #lasso = linear_model.LassoCV(eps=0.01, n_alphas=500, alphas=None, fit_intercept=True, normalize=False, precompute='auto', max_iter=10000, tol=0.0001, copy_X=True, cv=None, verbose=False)
    #lasso.fit(X, Y)
    #print lasso.alpha_
    #bestalpha=lasso.alpha_
    clf = linear_model.Lasso(alpha = 1.5)
    clf.fit(X,Y)
    return clf.predict(testFeatures)
    
@discreteResponse
def predictWithGradientBoosting(config, X, Y, testFeatures):
    clf = GradientBoostingClassifier()
    clf.fit(X,Y)
    return clf.predict(testFeatures)
    