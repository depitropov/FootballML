#! /usr/bin/python3

import pandas as pd


class FeatureCalculator:

    def calculate_features(self, df, side, team_id):
        d = {
            '{0}_half_time_wins'.format(side): self.get_half_time_wins(df, team_id),
            '{0}_full_time_wins'.format(side): self.get_half_time_wins(df, team_id),
            '{0}_half_time_draws'.format(side): self.get_half_time_wins(df, team_id),
            '{0}_full_time_draws'.format(side): self.get_half_time_wins(df, team_id),
            '{0}_returns_percentage'.format(side): self.get_half_time_wins(df, team_id),
            '{0}_average_odds'.format(side): self.get_half_time_wins(df, team_id),
        }
        return pd.Series(d)

    def get_half_time_wins(self, df, team_id):
        return len(df.loc[(df.home_team_id == team_id) & (df.htr == 1)].index) + len(
            df.loc[(df.away_team_id == team_id) & (df.htr == 2)].index)

    def get_full_time_wins(self, df, team_id):
        return len(df.loc[df.home_team_id == team_id & df.ftr == 1].index) + len(
            df.loc[df.away_team_id == team_id & df.ftr == 2].index)

    def get_half_time_draws(self, df):
        return len(df.loc[df.htr == 3].index)

    def get_full_time_draws(self, df):
        return len(df.loc[df.ftr == 3].index)

    def get_returns_percentage(self, df, team_id):
        return (len(df.loc[df.home_team_id == team_id & df.htr == 2 & (df.ftr == 3 | df.ftr == 1)].index) + len(
            df.loc[df.away_team_id == team_id & df.htr == 1 & (df.ftr == 3 | df.ftr == 2)].index)) / (len(
            df.loc[df.home_team_id == team_id & df.htr == 2].index) + len(
            df.loc[df.away_team_id == team_id & df.htr == 1].index))

    def get_average_odds(self, df, team_id):
        return (df.loc[df.home_team_id == team_id].b365h.mean() + df.loc[df.awat_team_id == team_id].b365a.mean()) / 2

