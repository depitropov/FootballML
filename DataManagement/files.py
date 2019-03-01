#! /usr/bin/python3

import pandas as pd
import numpy as np
from os import listdir
from DataManagement.Utils import Converters
from multiprocessing import Pool


class FileImporter:

    def __init__(self, config, db_initiator, dao):
        self.config = config
        self.p = Pool(self.config['processors'])
        self.db_initiator = db_initiator
        self.dao = dao

    def update_countries(self, matches):
        countries_unique = self.dao.get_countries_unique(matches)

        self.dao.write_countries(countries_unique)

        countries_updated = self.dao.get_countries()

        matches = matches.reset_index().merge(countries_updated.reset_index().rename(columns={'index': 'country_id'}),
                                              left_on='country_name',
                                              right_on='country_name').set_index('index')
        matches = matches.drop('country_name', axis=1)
        return matches

    def update_leagues(self, matches):
        leagues_unique = self.dao.get_leagues_unique(matches)

        self.dao.write_leagues(leagues_unique)

        leagues_updated = self.dao.get_leagues()

        matches = matches.reset_index().merge(leagues_updated.reset_index().rename(columns={'index': 'league_id'}),
                                              left_on='league_name',
                                              right_on='league_name').set_index('index')
        matches = matches.drop('league_name', axis=1)

        return matches

    def update_teams(self, matches):
        teams = (matches[['home_team_name']].rename(columns={'home_team_name': 'team_name'}).append(
            matches[['away_team_name']].rename(columns={'away_team_name': 'team_name'}), ignore_index=True)) \
            .drop_duplicates()

        teams_unique = self.dao.get_teams_unique(teams)

        self.dao.write_teams(teams_unique)

        teams_updated = self.dao.get_teams()

        matches = matches.reset_index().merge(teams_updated.reset_index().rename(columns={'team_id': 'home_team_id'}),
                                              left_on='home_team_name',
                                              right_on='team_name').drop('team_name', axis=1)

        matches = matches.merge(teams_updated.reset_index().rename(columns={'team_id': 'away_team_id'}),
                                left_on='away_team_name',
                                right_on='team_name').drop('team_name', axis=1).set_index('index')

        matches = matches.drop((['home_team_name', 'away_team_name']), axis=1)

        return matches

    def import_files(self):
        self.db_initiator.init_db()
        csv_files = listdir(self.config['source_directory'])

        converters = Converters()

        matches_list_frames = []

        for csv_file in csv_files:
            print(csv_file)
            temp_frame = pd.read_csv(('%s/{0}' % self.config['source_directory']).format(csv_file))
            temp_frame.dropna(how='all', inplace=True)  # Remove empty rows
            temp_frame.dropna(axis=1, how='all', inplace=True)  # Remove empty columns
            temp_frame.dropna(subset=['HTR', 'FTR'],
                              inplace=True)  # Remove matches without half time or full time results
            temp_frame['league'] = temp_frame['Div']  # Create new column for league name
            temp_frame['country'] = temp_frame['Div']  # Create new column for country name
            temp_frame.Date = pd.to_datetime(temp_frame.Date, infer_datetime_format=True).astype(pd.Timestamp)
            temp_frame.country = self.p.map(converters.country, temp_frame.country)
            temp_frame.league = self.p.map(converters.league, temp_frame.league)
            temp_frame.HTR = self.p.map(converters.h_d_a, temp_frame.HTR)
            temp_frame.FTR = self.p.map(converters.h_d_a, temp_frame.FTR)
            temp_frame['HTFTR'] = self.p.map(int, temp_frame['HTR'].map(str) + temp_frame['FTR'].map(str))
            temp_frame.drop(
                ['HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR', 'Div', 'BWH', 'BWD',
                 'BWA', 'IWH', 'IWD', 'IWA', 'LBH', 'LBD', 'LBA', 'PSH', 'PSD', 'PSA', 'WHH', 'WHD', 'WHA', 'VCH',
                 'VCD', 'VCA', 'Bb1X2', 'BbMxH', 'BbAvH', 'BbMxD', 'BbAvD', 'BbMxA', 'BbAvA', 'BbOU', 'BbMx>2.5',
                 'BbAv>2.5', 'BbMx<2.5', 'BbAv<2.5', 'BbAH', 'BbAHh', 'BbMxAHH', 'BbAvAHH', 'BbMxAHA', 'BbAvAHA',
                 'PSCH', 'PSCD', 'PSCA', 'BSH', 'BSD', 'BSA', 'Referee', 'GBH', 'GBA', 'GBD', 'SBH', 'SBD', 'SBA',
                 'SJH', 'SJD', 'SJA', 'HFKC', 'AFKC'], axis=1, inplace=True, errors='ignore')
            temp_frame.replace("", np.nan)
            temp_frame.columns = ['date', 'home_team_name', 'away_team_name', 'fthg', 'ftag', 'ftr', 'hthg', 'htag',
                                  'htr',
                                  'b365h', 'b365d', 'b365a', 'league_name', 'country_name', 'htftr']

            matches_list_frames.append(temp_frame)

        matches = pd.concat(matches_list_frames, axis=0, ignore_index=True)

        matches = self.update_countries(matches)
        matches = self.update_leagues(matches)
        matches = self.update_teams(matches)

        matches_unique = self.dao.get_matches_unique(matches)

        self.dao.write_matches(matches_unique)
