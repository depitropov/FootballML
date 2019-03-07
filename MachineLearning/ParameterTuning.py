from sklearn import model_selection
from sklearn.metrics import classification_report

class ParameterTuning:

    def __init__(self, estimator, data, params):
        self.estimator = estimator
        self.data = data
        self.params = params

    def report(self, results, n_top=3):
        for i in range(1, n_top + 1):
            candidates = np.flatnonzero(results['rank_test_score'] == i)
            for candidate in candidates:
                print("Model with rank: {0}".format(i))
                print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                    results['mean_test_score'][candidate],
                    results['std_test_score'][candidate]))
                print("Parameters: {0}".format(results['params'][candidate]))
                print("")

    def perform_grid_search(self):

        kfold = model_selection.KFold(n_splits=6, random_state=6)
        clf = model_selection.GridSearchCV(self.estimator, self.params, cv=kfold, scoring='precision')
        clf.fit(self.data['X_train'], self.data['Y_train'])

        print("Best parameters set found on development set:")
        print()
        print(clf.best_params_)
        print()
        print("Grid scores on development set:")
        print()
        means = clf.cv_results_['mean_test_score']
        stds = clf.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, clf.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r"
                  % (mean, std * 2, params))
        print()

        print("Detailed classification report:")
        print()
        print("The model is trained on the full development set.")
        print("The scores are computed on the full evaluation set.")
        print()
        y_true, y_pred = self.data['Y_test'], clf.predict(self.data['X_test'])
        print(classification_report(y_true, y_pred))
        print()

    def perform_random_search(self, iterations):
        k = model_selection.StratifiedKFold(n_splits=9)
        randsearch = model_selection.RandomizedSearchCV(self.estimator, param_distributions=self.params,
                                                        scoring='precision', cv=k, n_jobs=4, verbose=1,
                                                        n_iter=iterations)

        randsearch.fit(self.data['X_train'], self.data['Y_train'])

        print("Best parameters set found on development set:")
        print()
        print(randsearch.best_params_)
        print()
        print("Grid scores on development set:")
        print()
        means = randsearch.cv_results_['mean_test_score']
        stds = randsearch.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, randsearch.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r"
                  % (mean, std * 2, params))
        print()

        print("Detailed classification report:")
        print()
        print("The model is trained on the full development set.")
        print("The scores are computed on the full evaluation set.")
        print()
        y_true, y_pred = self.data['Y_test'], randsearch.predict(self.data['X_test'])
        print(classification_report(y_true, y_pred))
        print()

