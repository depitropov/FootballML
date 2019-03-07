#! /usr/bin/python3

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


def testestimator(data):
    # grid-test
    # K-fold!!!!!!

    # Make predictions on validation dataset
    svc = SVC(class_weight={1: 0.94, 0: 0.06})
    svc.fit(data['X_train'], data['Y_train'])
    predictions = svc.predict(data['X_test'])
    print(accuracy_score(data['Y_test'], predictions))
    print(confusion_matrix(data['Y_test'], predictions, [1, 0]))
    print(classification_report(data['Y_test'], predictions))
