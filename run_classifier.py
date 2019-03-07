from Config import init_config
from DataManagement.database import Dao
from MachineLearning.getdata import split_data
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_curve, auc
from sklearn.model_selection import cross_validate
import numpy as np

from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

configuration = init_config()
dao = Dao(configuration)

threshold = 0.6


def predict(x):
    return 1.0 if x >= threshold else 0.0

vecotired_predict = np.vectorize(predict)

data = dao.get_features('last_10_matches_side')
splited_data = split_data(data, scale=True, smote=False, downsample=True, drop_na=True)
# Make predictions on validation dataset
svc = GaussianNB()
svc.fit(splited_data['X_train'], splited_data['Y_train'])
prob = svc.predict_proba(splited_data['X_test'])[:, 1]
print(prob)
predictions = np.apply_along_axis(vecotired_predict, 0, prob)
#predictions = svc.predict(splited_data['X_test'])



#predictions = svc.predict(splited_data['X_test'])

scoring = {'accuracy': 'accuracy',
           'recall': 'recall',
           'precision': 'precision',
           'roc_auc': 'roc_auc'}

cross_val_scores = cross_validate(svc, splited_data['X_train'], splited_data['Y_train'], cv=9, scoring='precision')
print(cross_val_scores)

print(accuracy_score(splited_data['Y_test'], predictions))
print(confusion_matrix(splited_data['Y_test'], predictions, [1, 0]))
print(classification_report(splited_data['Y_test'], predictions))
