#! /usr/bin/python3

from Config import init_config
from DataManagement.files import FileImporter
from DataManagement.database import Dao, DbInitiator
from DataManagement.features import FeatureManager, FeatureCalculator

configuration = init_config()
dao = Dao(configuration)
db_initiator = DbInitiator(configuration)
file_importer = FileImporter(configuration, db_initiator, dao)
#file_importer.import_files()

feature_calculator = FeatureCalculator()
feature_manager = FeatureManager(dao, feature_calculator, "last_10_matches_third", 10)
feature_manager.generate_features()



