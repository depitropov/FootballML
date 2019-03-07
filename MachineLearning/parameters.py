from scipy.stats import randint, uniform
import numpy as np

svc_grid_params = {
                'C': [1, 20, 40, 60, 80, 100],
                'kernel': ['linear', 'rbf'],  # precomputed,'poly', 'sigmoid'
                'degree': [0, 20, 40, 60, 80, 100],
                'gamma': [1, 2, 4, 6, 8, 10],
                'coef0': [1, 2, 4, 6, 8, 10],
                'tol': [0.001, 0.05, 0.010, 0.015, 0.01]
            }

tuned_parameters = {'kernel': ['rbf', 'linear'],
                    'gamma': [1e-2, 1e-3, 1e-4, 1e-5],
                    'C': [0.001, 0.10, 0.1, 10, 25, 50, 100, 1000],
                    'degree': [0, 20, 40, 60, 80, 100]
                    }


svc_random_params = {
                'C': np.arange(1, 100 + 1, 1).tolist(),
                'kernel': ['linear', 'rbf'],  # precomputed,'poly', 'sigmoid'
                'degree': np.arange(0, 100 + 0, 1).tolist(),
                'gamma': np.arange(0.0, 10.0 + 0.0, 0.1).tolist(),
                'coef0': np.arange(0.0, 10.0 + 0.0, 0.1).tolist(),
                'shrinking': [True],
                'probability': [False],
                'tol': np.arange(0.001, 0.01 + 0.001, 0.001).tolist(),
                'cache_size': [2000],
                'class_weight': [None],
                'verbose': [False],
                'max_iter': [-1],
                'random_state': [None],
}


sgd_grid = {
                "loss": ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron', 'squared_epsilon_insensitive'],
                "n_iter": [1, 3, 5, 7, 9, 10, 13, 15, 17, 20],
                "alpha": [0.0001, 0.0003, 0.0004, 0.0005, 0.001, 0.01, 0.1, 1, 10, 100],
                "l1_ratio": [0.00, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00],
                "fit_intercept": [True, False],
                # "learning_rate": ['constant', 'optimal', 'invscaling'],
                "class_weight": [{0: 0.94, 1: 0.06}],
                "warm_start": [True, False],
                "penalty": ['none', 'l2', 'l1', 'elasticnet']
            }

sgd_dist = {
                "n_iter": randint(1, 11),
                "alpha": uniform(scale=0.01),
                "penalty": ["none", "l1", "l2"]
            }


random_forest_dist = {"max_depth": [3, None],
              "max_features": randint(1, 11),
              "min_samples_split": randint(2, 11),
              "bootstrap": [True, False],
              "criterion": ["gini", "entropy"]
                      }

knn_params = {'n_neighbors':[5,6,7,8,9,10],
          'leaf_size':[1,2,3,5],
          'weights':['uniform', 'distance'],
          'algorithm':['auto', 'ball_tree','kd_tree','brute'],
          'n_jobs':[-1]}


gb_grid_params = {
    "loss": ["deviance"],
    "learning_rate": [0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2],
    "min_samples_split": np.linspace(0.1, 0.5, 12),
    "min_samples_leaf": np.linspace(0.1, 0.5, 12),
    "max_depth": [3, 5, 8],
    "max_features": ["log2", "sqrt"],
    "criterion": ["friedman_mse",  "mae"],
    "subsample": [0.5, 0.618, 0.8, 0.85, 0.9, 0.95, 1.0],
    "n_estimators": [10]
    }

logistic_reg_grid_params = {
    "C": np.logspace(-3, 3, 7),
    "penalty": ["l2"],
    'class_weight': ['balanced'],
    'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']
    }
