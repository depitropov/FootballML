#! /usr/bin/env python
from __future__ import print_function

from Tools.getdata import get_data_db, get_data_csv

import numpy as np

from time import time
from operator import itemgetter

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.feature_selection import SelectKBest
from sklearn.ensemble import ExtraTreesClassifier
from scipy.stats import randint, uniform

from Parameters.Classification import CLParameters


def ExtraTrees(data, result):
    # Feature Importance with Extra Trees Classifier
    model = ExtraTreesClassifier()
    model.fit(data['X_train'], data['Y_train'])
    print(model.feature_importances_)


def KBest(data, result):
    model = SelectKBest(score_func='f_classif', k=all)
    scores = model.fit(data['X_train'], data['Y_train'])


# Report for parameter tuner
def report(cv_results, n_top=10):
    """Report top n_top parameters settings, default n_top=10.

    Args
    ----
    cv_results -- output from grid or random search
    n_top -- how many to report, of top models

    Returns
    -------
    top_params -- [dict] top parameter settings found in
                  search
    """
    print (cv_results)
    res = zip(cv_results['params'], cv_results['mean_test_score'], cv_results['std_test_score'])
    top_scores = sorted(res, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print(("Precision: "
               "{0:.3f} (std: {1:.3f})").format(
               score[1],
               score[2]))
        print("Parameters: {0}".format(score[0]))
        print("")

    return top_scores[0][0]


def run_grid_search(data, clf, cv=5, param_grid=False):
    """Run a grid search for best Decision Tree parameters.

    Args
    ----
    X -- features
    y -- targets (classes)
    param_grid -- [dict] parameter settings to test
    clf - classifier to be used
    cv -- fold of cross-validation, default 5

    Returns
    -------
    top_params -- [dict] from report()
    """
    if not param_grid:
        param_grid=getattr(CLParameters, str(clf) + '_grid')

    # TODO: Error handling if param_grid is not correct or maybe error handling at .fit method

    grid_search = GridSearchCV(clf,
                               param_grid=param_grid,
                               cv=cv, scoring='precision', n_jobs=7)
    start = time()
    grid_search.fit(data['X_train'], data['Y_train'])

    print(("\nGridSearchCV took {:.2f} "
           "seconds for {:d} candidate "
           "parameter settings.").format(time() - start,
                len(grid_search.cv_results_['params'])))

    top_params = report(grid_search.cv_results_, 10)
    return top_params


def run_random_search(data, clf, param_dist, cv=5, n_iter_search=20):
    """Run a random search for best Decision Tree parameters.

    Args
    ----
    X -- features
    y -- targets (classes)
    cf -- scikit-learn Decision Tree
    param_dist -- [dict] list, distributions of parameters
                  to sample
    cv -- fold of cross-validation, default 5
    n_iter_search -- number of random parameter sets to try,
                     default 20.

    Returns
    -------
    top_params -- [dict] from report()
    """
    random_search = RandomizedSearchCV(clf,
                        param_distributions=param_dist,
                        n_iter=n_iter_search, scoring='precision', n_jobs=7)

    start = time()
    random_search.fit(data['X_train'], data['Y_train'])
    print(("\nRandomizedSearchCV took {:.2f} seconds "
           "for {:d} candidates parameter "
           "settings.").format((time() - start),
                               n_iter_search))

    top_params = report(random_search.cv_results_, 10)
    return top_params


def test_params(clf, data):
    """
    Tests the performance of the Clasificator
    :param clf: 
    :param data: 
    :return: 
    """
    clf.fit(data['X_train'], data['Y_train'])
    pred = clf.predict(data['X_test'])
    print(confusion_matrix(data['Y_test'], pred))
    print(classification_report(data['Y_test'], pred))

if __name__ == '__main__':
   pass


