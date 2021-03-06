#! /usr/bin/python3

from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


def testestimator(data):
    # grid-test
    # K-fold!!!!!!

    # Make predictions on validation dataset
    nb = SGDClassifier()
    nb.fit(data['X_train'], data['Y_train'])
    predictions = nb.predict(data['X_test'])
    print(accuracy_score(data['Y_test'], predictions))
    print(confusion_matrix(data['Y_test'], predictions))
    print(classification_report(data['Y_test'], predictions))
