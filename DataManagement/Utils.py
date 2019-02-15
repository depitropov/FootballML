#! /usr/bin/python3
from datetime import datetime
import pandas as pd


class Converters:

    leagues_dict = {'E0': 'eng_premier',
                    'E1': 'eng_championship',
                    'E2': 'eng_league1',
                    'E3': 'eng_league2',
                    'EC': 'eng_conf',
                    'D1': 'ger_1',
                    'D2': 'ger_2',
                    'F1': 'fra_1',
                    'F2': 'fra_2',
                    'I1': 'ita_1',
                    'I2': 'ita_2',
                    'SP1': 'spa_1',
                    'SP2': 'spa_2',
                    'N1': 'ned_1'
                    }

    countries_dict = {'E': 'England', 'S': 'Spain', 'D': 'Germany', 'F': 'France', 'I': 'Italy'}

    h_d_a_dict = {'H': 1, 'D': 3, 'A': 2}

    def convert_date(self, date):
        converted_date = datetime.strptime(date, '%d/%m/%y')
        return converted_date

    def league(self, div):
        return self.leagues_dict[div]

    def country(self, div):
        return self.countries_dict[div[0:1]]

    def h_d_a(self, result):
        return self.h_d_a_dict[result]


class DbUtils:

    @staticmethod
    def clean_df_db_duplicates(df, table_name, engine, dup_cols=[],
                               filter_continuous_col=None, filter_categorical_col=None):
        """
        Remove rows from a dataframe that already exist in a database
        Required:
            df : dataframe to remove duplicate rows from
            engine: SQLAlchemy engine object
            tablename: tablename to check duplicates in
            dup_cols: list or tuple of column names to check for duplicate row values
        Optional:
            filter_continuous_col: the name of the continuous data column for BETWEEEN min/max filter
                                   can be either a datetime, int, or float data type
                                   useful for restricting the database table size to check
            filter_categorical_col : the name of the categorical data column for Where = value check
                                     Creates an "IN ()" check on the unique values in this column
        Returns
            Unique list of values from dataframe compared to database table
        """
        args = 'SELECT %s FROM %s' % (', '.join(['"{0}"'.format(col) for col in dup_cols]), table_name)
        args_contain_filter, args_cat_filter = None, None
        if filter_continuous_col is not None:
            if df[filter_continuous_col].dtype == 'datetime64[ns]':
                args_contain_filter = """ "%s" BETWEEN Convert(datetime, '%s')
                                              AND Convert(datetime, '%s')""" % (filter_continuous_col,
                                                                                df[filter_continuous_col].min(),
                                                                                df[filter_continuous_col].max())

        if filter_categorical_col is not None:
            args_cat_filter = ' "%s" in(%s)' % (filter_categorical_col,
                                                ', '.join(["'{0}'".format(value) for value in
                                                           df[filter_categorical_col].unique()]))

        if args_contain_filter and args_cat_filter:
            args += ' Where ' + args_contain_filter + ' AND' + args_cat_filter
        elif args_contain_filter:
            args += ' Where ' + args_contain_filter
        elif args_cat_filter:
            args += ' Where ' + args_cat_filter

        df.drop_duplicates(dup_cols, keep='last', inplace=True)
        df = pd.merge(df, pd.read_sql(args, engine), how='left', on=dup_cols, indicator=True)
        df = df[df['_merge'] == 'left_only']
        df.drop(['_merge'], axis=1, inplace=True)
        return df
