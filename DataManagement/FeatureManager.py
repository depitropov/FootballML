#! /usr/bin/python3

import pandas as pd


def calculate_features(df, side, match_id):
    d = {
        '{0}_first_half_wins'.format(side): FeatureCalculator.get_half_time_wins(df, match_id)
    }
    return pd.Series(d, index=['{0}_first_half_wins'.format(side)])


def get_half_time_wins(df, match_id):
    df.loc[df.home_team_id == match_id].hthg.sum() + df.loc[
        df.away_team_id == match_id].hthg.sum() / len(df.index)


class FeatureCalculator:

    @staticmethod
    def calculate_features(df, side, match_id):
        d = {
            '{0}_first_half_wins'.format(side): FeatureCalculator.get_half_time_wins(df, match_id)
        }
        return pd.Series(d, index=['{0}_first_half_wins'.format(side)])

    @staticmethod
    def get_half_time_wins(df, match_id):
        return df.loc[df.home_team_id == match_id].hthg.sum() + df.loc[
            df.away_team_id == match_id].hthg.sum() / len(df.index)
