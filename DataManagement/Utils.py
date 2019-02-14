#! /usr/bin/python3
from datetime import datetime


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

