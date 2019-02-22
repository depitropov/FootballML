#!/usr/bin/python3
from psycopg2 import sql
import pandas as pd
import time




def set_last_matches_sql(matches, conn, count=5):
    """
    Get last &count matches of both teams.
    :param matches: pd dataframe with all matches
    :param conn: DataManagement connection object
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



