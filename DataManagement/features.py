#! /usr/bin/python3

import pandas as pd
import numpy as np
import time


class FeatureManager:

    def __init__(self, dao, feature_calculator, table_name, count):
        self.dao = dao
        self.feature_calculator = feature_calculator
        self.count = count
        self.table_name = table_name

    def get_previous_matches(self, matches, team_id, date):
        return matches.loc[(matches['date'] < date) & (
                (matches['home_team_id'] == team_id) | (
                matches['away_team_id'] == team_id))].nlargest(self.count, 'date')

    def calculate_features_per_row(self, matches, index):

        match_date = matches.at[index, 'date']
        home_team_id = int(matches.at[index, 'home_team_id'])
        away_team_id = int(matches.at[index, 'away_team_id'])

        last_matches_home = self.get_previous_matches(matches, home_team_id, match_date)
        last_matches_away = self.get_previous_matches(matches, away_team_id, match_date)

        if len(last_matches_away.index) < self.count or len(last_matches_home.index) < self.count:
            return pd.Series()

        features_home = self.feature_calculator.calculate_features(last_matches_home, 'home', home_team_id)
        features_away = self.feature_calculator.calculate_features(last_matches_away, 'away', away_team_id)

        return matches.loc[index][
            ['home_team_id', 'away_team_id', 'htftr', 'b365h', 'b365a', 'b365d']].set_value('match_id', index).append(
            features_home).append(features_away)

    def calculate_features(self, matches):
        result = pd.DataFrame()

        for index in matches.index:
            feature_row = self.calculate_features_per_row(matches, index)
            if not feature_row.empty:
                result = result.append(feature_row, ignore_index=True)

        return result.set_index('match_id')

    def generate_features(self):
        start = time.time()
        matches_without_features = self.dao.get_matches_without_features(self.table_name)
        result = self.calculate_features(matches_without_features)
        result = self.dao.write_features(result, self.table_name)
        end = time.time()
        print(end - start)
        return result


class FeatureCalculator:

    def calculate_features(self, df, side, team_id):
        d = {
            '{0}_half_time_wins'.format(side): self.get_half_time_wins(df, team_id),
            '{0}_full_time_wins'.format(side): self.get_full_time_wins(df, team_id),
            '{0}_half_time_draws'.format(side): self.get_half_time_draws(df),
            '{0}_full_time_draws'.format(side): self.get_full_time_draws(df),
            '{0}_scored_first_half'.format(side): self.get_scored_first_half(df, team_id),
            '{0}_scored_second_half'.format(side): self.get_scored_second_half(df, team_id),
            '{0}_recovery_percentage'.format(side): self.get_recovery_percentage(df, team_id),
            '{0}_turn_around_percentage'.format(side): self.get_turn_around_percentage(df, team_id),
            '{0}_average_odds'.format(side): self.get_average_odds(df, team_id),
            '{0}_lose_draws'.format(side): self.get_lose_draws(df, team_id),
            '{0}_win_draws'.format(side): self.get_win_draws(df, team_id),
            '{0}_side_half_time_wins'.format(side): self.get_side_half_time_wins(df, side, team_id),
            '{0}_side_full_time_wins'.format(side): self.get_side_full_time_wins(df, side, team_id),
            '{0}_side_half_time_draws'.format(side): self.get_side_half_time_draws(df, side, team_id),
            '{0}_side_full_time_draws'.format(side): self.get_side_full_time_draws(df, side, team_id),
            '{0}_side_scored_first_half'.format(side): self.get_side_scored_first_half(df, side, team_id),
            '{0}_side_scored_second_half'.format(side): self.get_side_scored_second_half(df, side, team_id),
            '{0}_side_recovery_percentage'.format(side): self.get_side_recovery_percentage(df, side, team_id),
            '{0}_side_turn_around_percentage'.format(side): self.get_side_turn_around_percentage(df, side, team_id),
            '{0}_side_average_odds'.format(side): self.get_side_average_odds(df, side, team_id),
            '{0}_side_lose_draws'.format(side): self.get_side_lose_draws(df, side, team_id),
            '{0}_side_win_draws'.format(side): self.get_side_win_draws(df, side, team_id)
        }
        return pd.Series(d)

    side_dict = {
        'home': 'home_team_id',
        'away': 'away_team_id'
    }

    def get_half_time_wins(self, df, team_id):
        return len(df.loc[(df.home_team_id == team_id) & (df.htr == 1)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.htr == 2)].index)

    def get_full_time_wins(self, df, team_id):
        return len(df.loc[(df.home_team_id == team_id) & (df.ftr == 1)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.ftr == 2)].index)

    def get_half_time_draws(self, df):
        return len(df.loc[df.htr == 3].index)

    def get_full_time_draws(self, df):
        return len(df.loc[df.ftr == 3].index)

    def get_scored_first_half(self, df, team_id):
        return len(df.loc[(df.home_team_id == team_id) & (df.hthg > 0)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.htag > 0)].index)

    def get_scored_second_half(self, df, team_id):
        return len(df.loc[(df.home_team_id == team_id) & (df.fthg - df.hthg > 0)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.ftag - df.htag > 0)].index)

    def get_recovery_percentage(self, df, team_id):

        possibles = (len(
            df.loc[(df.home_team_id == team_id) & (df.htr == 2)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.htr == 1)].index))

        if possibles == 0:
            return np.nan
        else:
            return (len(
                df.loc[(df.home_team_id == team_id) & (df.htr == 2) & ((df.ftr == 3) | (df.ftr == 1))].index) + len(
                df.loc[
                    (df.away_team_id == team_id) & (df.htr == 1) & ((df.ftr == 3) | (df.ftr == 2))].index)) / possibles

    def get_turn_around_percentage(self, df, team_id):
        possibles = (len(
            df.loc[(df.home_team_id == team_id) & (df.htr == 2)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.htr == 1)].index))

        if possibles == 0:
            return np.nan
        else:
            return (len(
                df.loc[(df.home_team_id == team_id) & (df.htr == 1) & ((df.ftr == 3) | (df.ftr == 2))].index) + len(
                df.loc[
                    (df.away_team_id == team_id) & (df.htr == 2) & ((df.ftr == 3) | (df.ftr == 1))].index)) / possibles

    def get_average_odds(self, df, team_id):
        return (df.loc[df.home_team_id == team_id].b365h.mean() + df.loc[df.away_team_id == team_id].b365a.mean()) / 2

    def get_lose_draws(self, df, team_id):
        return len(df.loc[(df.home_team_id == team_id) & (df.htr == 2) & (df.ftr == 3)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.htr == 1) & (df.ftr == 3)].index)

    def get_win_draws(self, df, team_id):
        return len(df.loc[(df.home_team_id == team_id) & (df.htr == 1) & (df.ftr == 3)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.htr == 2) & (df.ftr == 3)].index)

    def get_side_half_time_wins(self, df, side, team_id):
        if side == 'home':
            return len(df.loc[(df.home_team_id == team_id) & (df.htr == 1)].index)
        else:
            return len(df.loc[(df.away_team_id == team_id) & (df.htr == 2)].index)

    def get_side_full_time_wins(self, df, side, team_id):
        if side == 'home':
            return len(df.loc[(df.home_team_id == team_id) & (df.ftr == 1)].index)
        else:
            return len(df.loc[(df.away_team_id == team_id) & (df.ftr == 2)].index)

    def get_side_half_time_draws(self, df, side, team_id):
        return len(df.loc[(df[self.side_dict[side]] == team_id) & (df.htr == 3)].index)

    def get_side_full_time_draws(self, df, side, team_id):
        return len(df.loc[(df[self.side_dict[side]] == team_id) & (df.ftr == 3)].index)

    def get_side_scored_first_half(self, df, side, team_id):
        if side == 'home':
            return len(df.loc[(df.home_team_id == team_id) & (df.hthg > 0)].index)
        else:
            return len(df.loc[(df.away_team_id == team_id) & (df.htag > 0)].index)

    def get_side_scored_second_half(self, df, side, team_id):
        if side == 'home':
            return len(df.loc[(df.home_team_id == team_id) & (df.fthg - df.hthg > 0)].index)
        else:
            return len(df.loc[(df.away_team_id == team_id) & (df.ftag - df.htag > 0)].index)

    def get_side_recovery_percentage(self, df, side, team_id):

        if side == 'home':
            possibles = len(
                df.loc[(df.home_team_id == team_id) & (df.htr == 2)].index)

            if possibles == 0:
                return np.nan
            else:
                return len(
                    df.loc[(df.home_team_id == team_id) & (df.htr == 2) & (
                                (df.ftr == 3) | (df.ftr == 1))].index) / possibles
        else:
            possibles = len(df.loc[(df.away_team_id == team_id) & (df.htr == 1)].index)

            if possibles == 0:
                return np.nan
            else:
                return len(df.loc[
                               (df.away_team_id == team_id) & (df.htr == 1) & (
                                       (df.ftr == 3) | (df.ftr == 2))].index) / possibles

    def get_side_turn_around_percentage(self, df, side, team_id):

        if side == 'home':

            possibles = len(df.loc[(df.home_team_id == team_id) & (df.htr == 1)].index)

            if possibles == 0:
                return np.nan
            else:
                return len(
                    df.loc[(df.home_team_id == team_id) & (df.htr == 1) & (
                                (df.ftr == 3) | (df.ftr == 2))].index) / possibles
        else:
            possibles = len(df.loc[(df.away_team_id == team_id) & (df.htr == 2)].index)

            if possibles == 0:
                return np.nan
            else:
                return len(
                    df.loc[
                        (df.away_team_id == team_id) & (df.htr == 2) & (
                                    (df.ftr == 3) | (df.ftr == 1))].index) / possibles

    def get_side_average_odds(self, df, side, team_id):
        if side == 'home':
            return df.loc[df.home_team_id == team_id].b365h.mean()
        else:
            return df.loc[df.away_team_id == team_id].b365a.mean()

    def get_side_lose_draws(self, df, side, team_id):
        if side == 'home':
            return len(df.loc[(df.home_team_id == team_id) & (df.htr == 2) & (df.ftr == 3)].index)
        else:
            return len(df.loc[(df.away_team_id == team_id) & (df.htr == 1) & (df.ftr == 3)].index)

    def get_side_win_draws(self, df, side, team_id):
        if side == 'home':
            return len(df.loc[(df.away_team_id == team_id) & (df.htr == 2) & (df.ftr == 3)].index)
        else:
            return len(df.loc[(df.away_team_id == team_id) & (df.htr == 2) & (df.ftr == 3)].index)
