#! /usr/bin/python3
from sklearn import model_selection
from sklearn import preprocessing
from imblearn.over_sampling import SMOTE
from sklearn.utils import resample
import pandas as pd


def split_data(data, scale=True, normalize=False, std_scale=False, drop_na=True, smote=False, downsample=False):

    if drop_na:
        data = data.dropna()

    classes = data['htftr'].values
    inputs = data.drop('htftr', axis=1).values

    data['htftr'].replace(13, 1, inplace=True)
    data.loc[data['htftr'] != 1, 'htftr'] = 0
    assert len(data['htftr'].unique()) == 2

    if downsample:
        df_minority = data[data.htftr == 1]
        df_majority = data[data.htftr == 0]

        df_minority_upsampled = resample(df_minority,
                                         replace=False,  # sample with replacement
                                         n_samples=1482,  # to match majority class
                                         random_state=123)  # reproducible results
        data = pd.concat([df_majority, df_minority_upsampled])

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
    if smote:
        smt = SMOTE()
        X_train, Y_train = smt.fit_sample(X_train, Y_train)

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