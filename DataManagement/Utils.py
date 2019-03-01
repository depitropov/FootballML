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
