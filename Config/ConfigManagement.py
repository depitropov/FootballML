#!/usr/bin/python3

import configparser


def init_config():
    config = configparser.ConfigParser()
    config.read("/opt/footballML/default.cnf")

    return {
        "host": config.get('database', 'host'),
        "url": config.get('database', 'url'),
        "user": config.get('database', 'username'),
        "database": config.get('database', 'database'),
        "source_directory": config.get('directories', 'source'),
        "destination_directory": config.get('directories', 'destination'),
        "processors": config.getint('system', 'processors')
    }
