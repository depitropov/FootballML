#! /usr/bin/python3

from Config import init_config
from DataManagement import FileImporter
from dao import DbGetters

configuration = init_config()
db_getters = DbGetters(configuration)
file_importer = FileImporter(configuration, db_getters)
file_importer.import_files()


