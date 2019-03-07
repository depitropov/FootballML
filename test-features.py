
from Config import init_config
from DataManagement.database import Dao
from MachineLearning.getdata import split_data
from MachineLearning.ParameterTuning import ParameterTuning
from MachineLearning.parameters import *
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression


configuration = init_config()
dao = Dao(configuration)

data = dao.get_features('last_10_matches_side')
splited_data = split_data(data, drop_na=True, downsample=True)
search = ParameterTuning(LogisticRegression(), splited_data, logistic_reg_grid_params)
search.perform_random_search(10)
