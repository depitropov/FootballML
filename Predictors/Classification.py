#! /usr/bin/python3
import numpy as np
import pandas as pd
import sqlite3 as sq
from time import time

from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC

from sklearn import model_selection
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.externals import joblib
from scipy.stats import randint, uniform


def create_estimator(data, clf, name):
    # grid-test
    # K-fold!!!!!!

    # Make predictions on validation dataset
    clf.fit(data['X_train'], data['Y_train'])
    joblib.dump(clf, '../estimators/%s.pkl' % name)
    predictions = clf.predict(data['X_validation'])
    print(accuracy_score(data['Y_validation'], predictions))
    print(confusion_matrix(data['Y_validation'], predictions))
    print(classification_report(data['Y_validation'], predictions))


def estimate(data, name):
    clf = joblib.load('../estimators/%s.pkl' % name)
    dataset = data.values
    prediction = clf.predict(dataset)
    print(dataset)
    print(prediction)
