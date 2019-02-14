#! /usr/bin/python3

from Config import init_config
from DataManagement import DbInitiator, FileImporter

configuration = init_config()
db_initiator = DbInitiator(configuration)
db_initiator.init_db()
file_importer = FileImporter(configuration)
file_importer.import_files()


