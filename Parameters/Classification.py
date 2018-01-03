#! /usr/bin/env python
import numpy as np
from scipy.stats import randint, uniform


class CLParameters(object):
    
    def __init__(self):
        self.parameters = {
            'svc_dist': {
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
            },
            'svc_grid': {
                'C': [1, 20, 40, 60, 80, 100],
                'kernel': ['linear', 'rbf'],  # precomputed,'poly', 'sigmoid'
                'degree': [0, 20, 40, 60, 80, 100],
                'gamma': [1, 2, 4, 6, 8, 10],
                'coef0': [1, 2, 4, 6, 8, 10],
                'tol': [0.001, 0.05, 0.010, 0.015, 0.01]
            },
            'sgd_grid': {
                "loss": ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron', 'squared_epsilon_insensitive'],
                "n_iter": [1, 3, 5, 7, 9, 10, 13, 15, 17, 20],
                "alpha": [0.0001, 0.0003, 0.0004, 0.0005, 0.001, 0.01, 0.1, 1, 10, 100],
                "l1_ratio": [0.00, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00],
                "fit_intercept": [True, False],
                # "learning_rate": ['constant', 'optimal', 'invscaling'],
                "class_weight": [{0: 0.94, 1: 0.06}],
                "warm_start": [True, False],
                "penalty": ['none', 'l2', 'l1', 'elasticnet']
            },
            'sgd_dist': {
                "n_iter": randint(1, 11),
                "alpha": uniform(scale=0.01),
                "penalty": ["none", "l1", "l2"]
            },
            'dt_grid': {
                "loss": ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron', 'squared_epsilon_insensitive'],
                "n_iter": [1, 3, 5, 7, 9, 10, 13, 15, 17, 20],
                "alpha": [0.0001, 0.0003, 0.0004, 0.0005, 0.001, 0.01, 0.1, 1, 10, 100],
                "l1_ratio": [0.00, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00],
                "fit_intercept": [True, False],
                # "learning_rate": ['constant', 'optimal', 'invscaling'],
                "class_weight": [{0: 0.94, 1: 0.06}],
                "warm_start": [True, False],
                "penalty": ['none', 'l2', 'l1', 'elasticnet']
            },
            'dt_dist': {
                "max_depth": [3, None],
                "max_features": randint(1, 9),
                "min_samples_leaf": randint(1, 9),
                "criterion": ["gini", "entropy"]
            }
        }
