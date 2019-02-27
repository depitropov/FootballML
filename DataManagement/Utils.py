#! /usr/bin/python3
from datetime import datetime
import pandas as pd
import logging
import itertools
from multiprocessing import Pool


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
                               filter_continuous_col=None, filter_categorical_col=None, log=False):
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

        database_data = pd.read_sql(args, engine)

        if len(database_data.index) > 0:
            df = pd.merge(df, pd.read_sql(args, engine), how='left', on=dup_cols, indicator=True)
        else:
            return df

        if log:
            df_with_error_records = df[df['_merge'] == 'both'][dup_cols]
            if df_with_error_records.size > 0:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                logging.warning("The following records already have duplicates in table {0} on columns {1}: \n {2}".
                                format(table_name, dup_cols, df[df['_merge'] == 'both'][dup_cols].to_string))
                pd.reset_option('display.max_rows')
                pd.reset_option('display.max_columns')

        df = df[df['_merge'] == 'left_only']
        df.drop(['_merge'], axis=1, inplace=True)
        return df


class FeatureUtils:

    def __init__(self, config, matches, side):
        self.config = config
        self.matches = matches
        self.side = side
        self.algorithms = (self.first_half_goals, self.second_half_goals, self.half_wins, self.half_draws, self.half_lose, self.full_wins,
                      self.full_draws, self.full_lose, self.win_odds, self.draw_odds, self.lose_odds, self.home_draw, self.away_draw)
        self.p = Pool(self.config['processors'])


    def get_features(self):

        matches_np = self.matches[
            ['HTFTR', 'HomeTeam', 'AwayTeam', 'league_id', 'country_id', 'Date', 'B365H', 'B365A', 'B365D',
             'last_home_ids_10', 'last_away_ids_10',
             'last_home_ids_5', 'last_away_ids_5']].dropna()

        for algorithm in self.algorithms:
            matches_np['{0}_{1}'.format(side, algorithm.func_name)] \
            = self.p.map(algorithm, self.p.map(read_last, matches_np['last_{0}_ids_{1}'.format(side, num_matches)]),
                    itertools.repeat(side, len(matches_np)))
            for side in [get_all_last_home, get_all_last_away]:
                if side == get_all_last_home:
                    side_name = 'home'
                    side_col = 'HomeTeam'
                elif side == get_all_last_away:
                    side_name = 'away'
                    side_col = 'AwayTeam'
                matches_np['{0}_{1}_all'.format(side_name, algorithm.func_name)] = \
                    p.map(algorithm,
                          p.map(side, matches_np['Date'], matches_np[side_col]),
                          itertools.repeat(side_name, len(matches_np)))


    def first_half_goals(self, matches, side):
        if side == 'home':
            return matches.HTHG.sum() - matches.HTAG.sum()
        elif side == 'away':
            return matches.HTAG.sum() - matches.HTHG.sum()

    def second_half_goals(matches, side):
        if side == 'home':
            return (matches.FTHG.sum() - matches.HTHG.sum()) - (matches.FTAG.sum() - matches.HTAG.sum())
        elif side == 'away':
            return (matches.FTAG.sum() - matches.HTAG.sum()) - (matches.FTHG.sum() - matches.HTHG.sum())

    def half_wins(matches, side):
        if side == 'home':
            return matches[matches.HTR == 1].index.size
        elif side == 'away':
            return matches[matches.HTR == 2].index.size

    def half_draws(matches, side):
        if side == 'home':
            return matches[matches.HTR == 3].index.size
        elif side == 'away':
            return matches[matches.HTR == 3].index.size

    def half_lose(matches, side):
        if side == 'home':
            return matches[matches.HTR == 2].index.size
        elif side == 'away':
            return matches[matches.HTR == 1].index.size

    def full_wins(matches, side):
        if side == 'home':
            return matches[matches.FTR == 1].index.size
        elif side == 'away':
            return matches[matches.FTR == 2].index.size

    def full_draws(matches, side):
        if side == 'home':
            return matches[matches.FTR == 3].index.size
        elif side == 'away':
            return matches[matches.FTR == 3].index.size

    def full_lose(matches, side):
        if side == 'home':
            return matches[matches.FTR == 2].index.size
        elif side == 'away':
            return matches[matches.FTR == 1].index.size

    def win_odds(matches, side):
        if side == 'home':
            return matches.B365H.mean()
        if side == 'away':
            return matches.B365A.mean()

    def draw_odds(matches, side):
        if side == 'home':
            return matches.B365D.mean()
        if side == 'away':
            return matches.B365D.mean()

    def lose_odds(matches, side):
        if side == 'home':
            return matches.B365A.mean()
        if side == 'away':
            return matches.B365H.mean()

    def home_draw(matches, side):
        if side == 'home':
            return matches[matches.HTFTR == 13].index.size
        if side == 'away':
            return matches[matches.HTFTR == 13].index.size

    def away_draw(matches, side):
        if side == 'home':
            return matches[matches.HTFTR == 23].index.size
        if side == 'away':
            return matches[matches.HTFTR == 23].index.size
