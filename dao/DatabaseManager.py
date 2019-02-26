import psycopg2
from psycopg2 import sql
import pandas as pd
from multiprocessing import Pool
from DataManagement import DbUtils
from sqlalchemy import create_engine


class DbInitiator:

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

    def init_db(self):
        """Initiates the database. Transform and populate data from all CVS located in input folder"""
        self.cur.execute("""CREATE TABLE IF NOT EXISTS public.teams(
                    team_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    team_name text,
                    CONSTRAINT team_name_uniq UNIQUE (team_name)
                    )
                    WITH (OIDS = FALSE);
                    ALTER TABLE public.teams OWNER TO footdata;
                    """
                         )

        self.cur.execute("""CREATE TABLE IF NOT EXISTS public.countries(
                    country_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    country_name text,
                    CONSTRAINT country_name_uniq UNIQUE (country_name)
                    )
                    WITH (OIDS = FALSE);
                    ALTER TABLE public.countries OWNER TO footdata;
                    """
                         )

        self.cur.execute("""CREATE TABLE IF NOT EXISTS public.leagues(
                    league_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    league_name text,
                    CONSTRAINT league_name_uniq UNIQUE (league_name)
                    )
                    WITH (OIDS = FALSE);
                    ALTER TABLE public.leagues OWNER TO footdata;
                    """
                         )

        self.cur.execute("""CREATE TABLE IF NOT EXISTS public.matches(
                    match_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    date timestamp without time zone,
                    home_team_id int REFERENCES teams (team_id),
                    away_team_id int REFERENCES teams (team_id),
                    fthg int,
                    ftag int,
                    ftr int,
                    hthg int,
                    htag int,
                    htr int,
                    b365h double precision,
                    b365d double precision,
                    b365a double precision,
                    league_id int REFERENCES leagues (league_id),
                    country_id int REFERENCES countries (country_id),
                    htftr int,
                    CONSTRAINT date_home_uniq UNIQUE (date, home_team_id)
                    )
                    WITH (OIDS = FALSE);
                    ALTER TABLE public.matches OWNER TO footdata;
                    """
                         )

        self.cur.execute(""" CREATE INDEX IF NOT EXISTS match_id ON matches (match_id);
                            CREATE INDEX IF NOT EXISTS home_team_id ON matches (home_team_id);
                            CREATE INDEX IF NOT EXISTS away_team_id ON matches (away_team_id);
                            CREATE INDEX IF NOT EXISTS date ON matches (date);""")
        self.con.commit()

    def init_feature_db(self, count):
        """
        :param count: number of last matches to generate features on
        :return: N/A
        """
        self.cur.execute("""
                        CREATE TABLE IF NOT EXISTS features{0}_matches (
                          match_id    int REFERENCES matches (match_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                          CONSTRAINT match_side_previous_{0}_pkey PRIMARY KEY (match_id, previous_id, side)
                        );""".format(count))
        self.cur.execute('CREATE INDEX IF NOT EXISTS match_side_{0}_index ON matches_{0}_previous (match_id, side);'.
                         format(count))
        self.con.commit()


class DbGetters:
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

    def get_countries(self):
        return pd.read_sql_query('SELECT * FROM countries;', self.con, index_col='country_id')

    def get_countries_unique(self, matches):
        return DbUtils.clean_df_db_duplicates(matches[['country_name']].drop_duplicates(), "countries",
                                              self.con_sql_alchemy, dup_cols=["country_name"])

    def write_countries(self, countries):
        countries.to_sql('countries', self.con_sql_alchemy, index_label='country_id', if_exists='append')

    def get_leagues(self):
        return pd.read_sql_query('SELECT * FROM leagues;', self.con, index_col='league_id')

    def get_leagues_unique(self, matches):
        return DbUtils.clean_df_db_duplicates(matches[['league_name']].drop_duplicates(), "leagues",
                                       self.con_sql_alchemy, dup_cols=["league_name"])

    def write_leagues(self, leagues):
        leagues.to_sql('leagues', self.con_sql_alchemy, index_label='league_id', if_exists='append')

    def get_teams(self):
        return pd.read_sql_query('SELECT * FROM teams;', self.con, index_col='team_id')

    def get_teams_unique(self, teams):
        return DbUtils.clean_df_db_duplicates(teams, "teams",
                                       self.con_sql_alchemy, dup_cols=["team_name"])

    def write_teams(self, teams):
        teams.to_sql('teams', self.con_sql_alchemy, index_label='team_id', if_exists='append')

    def get_matches(self):
        return pd.read_sql_query('SELECT * FROM matches;', self.con, index_col='match_id')

    def get_matches_unique(self, matches):
        return DbUtils.clean_df_db_duplicates(matches,
                                              "matches",
                                              self.con_sql_alchemy, dup_cols=["date", "home_team_id"],
                                              log=True)

    def write_matches(self, matches):
        matches.to_sql('matches', self.con_sql_alchemy, index_label='match_id', if_exists='append')

    def get_matches_without_features(self, table_name):

        query = sql.SQL("""SELECT matches.match_id, matches.date, matches.home_team_id, matches.away_team_id, 
        matches.htftr, matches.b365h, matches.b365d, matches.b365a
        FROM matches 
        LEFT JOIN {} features ON features.match_id = matches.match_id 
        WHERE features.match_id IS NULL;""").format(sql.Identifier(table_name)).as_string(self.con)

        return pd.read_sql_query(query, self.con_sql_alchemy,
                                 index_col='match_id')

    def get_previous_matches(self, team_id, date, count):
        """
        Get last &count matches of both teams.
        """

        query = """SELECT * FROM matches 
        WHERE (home_team_id = %(team_id)s OR away_team_id = %(team_id)s) AND %(date)s < matches.date
        ORDER BY date DESC 
        LIMIT %(count)s;"""

        params = {'team_id': team_id, 'date': date, 'count': count}

        previous_matches_df = pd.read_sql_query(query, self.con, index_col='match_id', params=params)
        return previous_matches_df


