#! /usr/bin/python3

from Tools.getdata import get_data


from sklearn import model_selection
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def evaluate_models(data, models=False):
    # TODO: Error catching

    # Spot Check Algorithms
    if not models:
        models = [('LR', LogisticRegression()),
                  ('LDA', LinearDiscriminantAnalysis()),
                  ('KNN', KNeighborsClassifier()),
                  ('CART', DecisionTreeClassifier()),
                  ('NB', GaussianNB()),
                  ('SVM', SVC()),
                  #('SGD', SGDClassifier(warm_start= True, n_iter= 8, loss= 'squared_hinge', l1_ratio= 0.5,
                                        #fit_intercept= True, penalty= 'l1', alpha= 0.0003, class_weight= {0: 0.94, 1: 0.06}))
                  ]
    seed = 7
    results = []
    names = []
    for name, model in models:
        kfold = model_selection.KFold(n_splits=6, random_state=seed)
        cv_results = model_selection.cross_val_score(model, data['X_train'], data['Y_train'], cv=kfold, scoring='precision')
        results.append(cv_results)
        names.append(name)
        print(cv_results)
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)