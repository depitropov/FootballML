#!/usr/bin/python3
from psycopg2 import sql
import pandas as pd
import numpy as np
import time
from profilehooks import profile


def set_last_matches(matches, conn, count=5):
    """
    Get last &count matches of both teams.
    :param matches: pd dataframe with all matches
    :param conn: DataBase connection object
    :param count: Number of last matches to index
    :return: True; Writes matches to a bridge table matches_&count_previous
    """
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS matches_{0}_previous;'.format(count))
    cur.execute("""
                CREATE TABLE matches_{0}_previous (
                  match_id    int REFERENCES matches (match_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                  previous_id int REFERENCES matches (match_id) ON UPDATE CASCADE, 
                  side text, 
                  CONSTRAINT match_side_previous_pkey PRIMARY KEY (match_id, previous_id, side)
                );""".format(count)
                )
    conn.commit()
    side_col = {'home_team': 1,
                'away_team': 2}
    t0 = time.perf_counter()
    for i, match in matches.iterrows():
        for side in ('home_team', 'away_team'):
            last_matches = pd.read_sql_query("SELECT match_id FROM matches WHERE {0} = '{1}' AND date < '{2}' ORDER BY date DESC LIMIT {3}"
                                             .format(side, match[side_col[side]], match[0], count),
                                             conn,
                                             index_col='match_id',
                                             )
            if len(last_matches.index) == count:
                for previous_id in last_matches:
                    print(previous_id)
                    cur.execute('INSERT INTO matches_{0}_previous (match_id, previous_id, side) VALUES (%s, %s, %s)'
                                .format(count), (i, previous_id, side))
                    conn.commit()
    cur.execute('CREATE INDEX match_side_index ON matches_%s_previous (match_id, side);', (count,))
    conn.commit()
    t1 = time.perf_counter()
    print(t1-t0)
    return True



def set_last_matches_sql(matches, conn, count=5):
    """
    Get last &count matches of both teams.
    :param matches: pd dataframe with all matches
    :param conn: DataBase connection object
    :param count: Number of last matches to index
    :return: True; Writes matches to a bridge table matches_&count_previous
    """
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS matches_{0}_previous;'.format(count))
    cur.execute("""
                CREATE TABLE matches_{0}_previous (
                  match_id    int REFERENCES matches (match_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                  previous_id int REFERENCES matches (match_id) ON UPDATE CASCADE, 
                  side text, 
                  CONSTRAINT match_side_previous_pkey PRIMARY KEY (match_id, previous_id, side)
                );""".format(count)
                )
    conn.commit()
    side_col = {'home_team': 1,
                'away_team': 2}
    t0 = time.perf_counter()
    for i, match in matches.iterrows():
        for side in ('home_team', 'away_team'):
            cur.execute(sql.SQL("SELECT match_id FROM matches WHERE {} = %s AND date < %s ORDER BY date DESC LIMIT %s")
                        .format(sql.Identifier(side)),(match[side_col[side]], match[0], count))
            last_matches = cur.fetchall()
            if len(last_matches) == count:
                for previous_id in last_matches:
                    print(previous_id)
                    cur.execute('INSERT INTO matches_{0}_previous (match_id, previous_id, side) VALUES (%s, %s, %s)'
                               .format(count), (i, previous_id[0], side))
                    conn.commit()
    cur.execute('CREATE INDEX match_side_index ON matches_%s_previous (match_id, side);', (count,))
    conn.commit()
    t1 = time.perf_counter()
    print(t1-t0)
    return True


def set_stats():
    pass


def first_half_goals(matches, side):
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


algorithms = (first_half_goals, second_half_goals, half_wins, half_draws, half_lose, full_wins,
              full_draws, full_lose, win_odds, draw_odds, lose_odds, home_draw, away_draw)