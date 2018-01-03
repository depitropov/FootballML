#! /usr/bin/python3
from sklearn import model_selection
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

import psycopg2
import sqlite3 as sq
import pandas as pd


def get_data_db(name, table, class_column, categorical_columns, drop_empty=False, scale=False, normalize=False, std_scale=False):
    """
    Gets data from a database
    :param database: Name of the DB existing in ../Data/
    :param table: The Table containing the data
    :param class_column: The column containing the classes for our model
    :param categorical_columns: List of strings for Columns containing categories in order to transform
    :param drop_empty: Drops empty columns and rows. Possible values (False, all/True, row, column)
    :param scale: Scales the data or not
    :param normalize: Normalizes the data or not
    :param std_scale: Standard scales the data or not
    :return: Dictionary of X_train, Y_train, X_test, Y_test
    """
    conn = sq.connect('../Data/%s') % name
    dataset = pd.read_sql_query('SELECT * FROM %s', conn) % table

    # Fix Data
    classes = (dataset['%s'] % class_column).values
    inputs = (dataset.drop('%s', axis=1) % class_column).values

    # TODO: Check for bugs
    for column in categorical_columns:
        encoder = OneHotEncoder()
        label_encoder = LabelEncoder()
        data_label_encoded = label_encoder.fit_transform(inputs[column])
        inputs[column] = data_label_encoded
        inputs[column] = encoder.fit_transform(inputs[[column]].as_matrix())

    X_train, X_test, Y_train, Y_test = \
        model_selection.train_test_split(inputs, classes, test_size=0.2)
    if scale:
        X_train = preprocessing.scale(X_train)
        X_test = preprocessing.scale(X_test)
    if normalize:
        X_train = preprocessing.normalize(X_train)
        X_test = preprocessing.normalize(X_test)
    if std_scale:
        X_train = preprocessing.StandardScaler(X_train)
        X_test = preprocessing.StandardScaler(X_test)

    return {'X_train': X_train, 'X_test': X_test, 'Y_train': Y_train, 'Y_test': Y_test}


def get_data_csv(name, class_column, drop_empty=False, scale=False, normalize=False, std_scale=False):
    """
    Gets data from a CSV file
    :param database: Name of the DB existing in ../Data/
    :param class_column: The column containing the classes for our model
    :param drop_empty: Drops empty columns and rows. Possible values (False, all/True, row, column)
    :param scale: Scales the data or not
    :param normalize: Normalizes the data or not
    :param std_scale: Standard scales the data or not
    :return: Dictionary of X_train, Y_train, X_test, Y_test
    """
    dataset = pd.read_csv('../Data/%s') %  name

    if drop_empty:
        dataset.dropna(how='all', inplace=True)  # Remove empty rows
        dataset.dropna(axis=1, how='all', inplace=True)  # Remove empty columns

    # Fix Data
    classes = (dataset['%s'] % class_column).values
    inputs = (dataset.drop('%s', axis=1) % class_column).values

    X_train, X_test, Y_train, Y_test = \
        model_selection.train_test_split(inputs, classes, test_size=0.2)
    if scale:
        X_train = preprocessing.scale(X_train)
        X_test = preprocessing.scale(X_test)
    if normalize:
        X_train = preprocessing.normalize(X_train)
        X_test = preprocessing.normalize(X_test)
    if std_scale:
        X_train = preprocessing.StandardScaler(X_train)
        X_test = preprocessing.StandardScaler(X_test)

    return {'X_train': X_train, 'X_test': X_test, 'Y_train': Y_train, 'Y_test': Y_test}


def get_data(data_info):
    """
    Primary function for reading data. Called with a single parameter data_info - a dictionary of parameters for getting 
    the appropriate data in the appropriate format.
    :param data_info: Dictionary with parameters for getting data. data_info['type'] is either csv or db and determines 
    the rest of the parameters. Mandatory are name and class_column and for db also table. The source of the data should 
    reside in ~/Data. Additional Params: scale, normalize, std normalize, drop_empty (False, row, column, all) 
    :return: Dictionary of X_train, Y_train, X_test, Y_test
    """
    # TODO: Error handling
    if data_info['type'] is 'csv':
        return get_data_csv(data_info['path'], data_info['class_column'],
                            drop_empty=data_info.get('drop_empty') or False,
                            scale=data_info.get('scale') or False,
                            normalize=data_info.get('normalize') or False,
                            std_scale=data_info.get('std_sclale') or False)
    if data_info['type'] is 'db':
        return get_data_db(data_info['path'], data_info['table'],
                           data_info['class_column'],
                           drop_empty=data_info.get('drop_empty') or False,
                           scale=data_info.get('scale') or False,
                           normalize=data_info.get('normalize') or False,
                           std_scale=data_info.get('std_sclale') or False)