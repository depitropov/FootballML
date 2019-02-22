#! /usr/bin/python3

import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine
from multiprocessing import Pool


class FeatureGenerator:

    def __init__(self, config):
        self.config = config
        self.p = Pool(self.config['processors'])
        self.con = psycopg2.connect(database=self.config['database'], user=self.config['user'],
                                    host=self.config['host'])
        self.cur = self.con.cursor()
        self.con_sql_alchemy = create_engine(self.config['url'])

    def __enter__(self):
        return self

    def __exit__(self):
        self.con_sql_alchemy.close()
        self.con.close()

    def generate_features(self):
        """Get Pandas dataframe with raw matches.
        Get statistics and write only needed columns to numpy.db for ML algorithms"""
        matches = pd.read_sql_query('SELECT * FROM matches', self.con_sql_alchemy, index_col='match_id')
        matches_np = matches[
            ['HTFTR', 'HomeTeam', 'AwayTeam', 'league_id', 'country_id', 'Date', 'B365H', 'B365A', 'B365D',
             'last_home_ids_10', 'last_away_ids_10',
             'last_home_ids_5', 'last_away_ids_5']].dropna()

        for side in ['home', 'away']:
            for algorithm in algorithms:
                matches_np['{0}_{1}'.format(side, algorithm.func_name)] \
                    = p.map(algorithm, p.map(read_last, matches_np['last_{0}_ids_{1}'.format(side, num_matches)]),
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
            fin_matches = matches_np.drop(['Date', 'HomeTeam', 'AwayTeam', 'last_home_ids_10', 'last_away_ids_10',
                                           'last_home_ids_5', 'last_away_ids_5'], axis=1)
            cur.execute('DROP TABLE IF EXISTS numpy_{0}'.format(num_matches))
            conn.commit()
            fin_matches.to_sql('numpy_{0}'.format(num_matches), conn, if_exists='replace')
        cur.close()
        conn.close()

    def init_feature_db(self, name):
        self.cur.execute("""
                        CREATE TABLE IF NOT EXISTS {0} (
                          match_id    int REFERENCES matches (match_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                          previous_id int REFERENCES matches (match_id) ON UPDATE CASCADE, 
                          side text, 
                          CONSTRAINT match_side_previous_{0}_pkey PRIMARY KEY (match_id, previous_id, side)
                        );""".format(count))
        self.cur.execute('CREATE INDEX IF NOT EXISTS match_side_{0}_index ON matches_{0}_previous (match_id, side);'.
                         format(count))
        self.con.commit()
