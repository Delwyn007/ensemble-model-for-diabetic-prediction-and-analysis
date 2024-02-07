# -*- coding: utf-8 -*-
"""Diabetes_predict.final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14ALJ9loC1WtPkjIr8tWV60vqeYA4e2Sw
"""

from google.colab import files
files.upload()

!pip install chart_studio

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split,RepeatedKFold, cross_val_score,KFold, RepeatedStratifiedKFold
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio.plotly as py
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier,export_graphviz
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, BaggingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score, KFold
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, BaggingClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, roc_curve, confusion_matrix
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, f1_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import precision_score, recall_score, confusion_matrix,  roc_curve, precision_recall_curve, accuracy_score, roc_auc_score
import lightgbm as lgbm
from sklearn.ensemble import VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_curve,auc
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_predict
from yellowbrick.classifier import DiscriminationThreshold

from imblearn.over_sampling import SMOTE

from xgboost import XGBClassifier
import lightgbm as lgb

# %matplotlib inline
import matplotlib.pyplot as plt
import seaborn as sns
import graphviz

import warnings
warnings.filterwarnings('ignore')


from yellowbrick import ROCAUC
from yellowbrick.classifier import ClassificationReport

print("Imported all libraries successfully")

CV_N_REPEATS=20
BINS=10

import warnings
warnings.filterwarnings('ignore')

"""Read Data"""

data = pd.read_csv('diabetes.csv')

data.head(5)

"""## 1. Data analysis"""

data.info()

data.describe()

plt.figure(figsize=(20,12), dpi= 60)
plt.title('Distribution of Outcome variable')
plt.pie(data['Outcome'].value_counts(), labels = ['healthy','diabetic'], colors = ['gold', 'lightcoral'], autopct='%1.1f%%', shadow=True, startangle=140)
plt.show()

for i in data.columns:
    print(i, data[i][data[i] == 0].count())

plt.figure(figsize = (12, 8))
ax = sns.boxplot(data = data, orient = 'h', palette = 'Set2')
plt.title('Boxplot overview dataset')
plt.xlabel('values')
plt.xlim(-3, 300)
plt.show()

"""#Data cleaning"""

#plot the correlation map of the dataset
plt.figure(figsize=(10,10))
corr = data.corr()
corr.index = data.columns
sns.heatmap(corr, annot = True, cmap='RdYlGn', vmin=-1, vmax=1)
plt.title("Correlation Heatmap", fontsize=16)
plt.show()

data.corr()

"""## 2. Data cleaning and feature Selection"""

def median_feature(feature):
    temp = data[data[feature] > 0]
    med_cat = temp.groupby('Outcome')[feature].median().reset_index()
    return med_cat

def preparing_feature(feature, median_data):
    data.loc[(data['Outcome'] == 0) & (data[feature] == 0), feature] = median_data[median_data['Outcome'] == 0][feature].median()
    data.loc[(data['Outcome'] == 1) & (data[feature] == 0), feature] = median_data[median_data['Outcome'] == 1][feature].median()

def kdeplot(feature, xlabel, title):
    plt.figure(figsize = (12, 8))
    ax = sns.kdeplot(data[feature][(data['Outcome'] == 0) &
                             (data[feature].notnull())], color = 'darkturquoise', shade = True)
    ax = sns.kdeplot(data[feature][(data['Outcome'] == 1) &
                             (data[feature].notnull())], color = 'lightcoral', shade= True)
    plt.xlabel(xlabel)
    plt.ylabel('frequency')
    plt.title(title)
    ax.grid()
    ax.legend(['healthy','diabetic'])
kdeplot('Glucose', 'concentration', 'Glucose')

median_feature_glucose = median_feature('Glucose')
median_feature_glucose

preparing_feature('Glucose', median_feature_glucose)

kdeplot('Insulin', 'mu U/ml', 'Insulin')

median_feature_insulin = median_feature('Insulin')
median_feature_insulin

data['Insulin'] = data['Insulin'].astype('float')
preparing_feature('Insulin', median_feature_insulin)

kdeplot('BloodPressure', 'mm Hg', 'BloodPressure')

median_feature_bpressure = median_feature('BloodPressure')
median_feature_bpressure

data['BloodPressure'] = data['BloodPressure'].astype('float')
preparing_feature('BloodPressure', median_feature_bpressure)

kdeplot('SkinThickness', 'mm', 'SkinThickness')

median_feature_skinthickness = median_feature('SkinThickness')
median_feature_skinthickness

preparing_feature('SkinThickness', median_feature_skinthickness)

kdeplot('BMI', 'weight in kg/(height in m)^2', 'BMI')

median_feature_bmi = median_feature('BMI')
median_feature_bmi

preparing_feature('BMI', median_feature_bmi)

for i in data.columns:
    print(i, data[i][data[i] == 0].count())

kdeplot('Age', 'years', 'Age')

kdeplot('DiabetesPedigreeFunction', 'diabetes pedigree function', 'DiabetesPedigreeFunction')

kdeplot('Pregnancies', 'number of times pregnant', 'Pregnancies')

data.head(5)

plt.figure()
sns.pairplot(data=data,hue='Outcome',diag_kind='kde', palette='deep');

"""#Priniciple Component Analysis"""

# Separating the features and the target (Y)
X = data.iloc[:,0:8]
Y = data.iloc[:,8]

#Standardizing the features
X= StandardScaler().fit_transform(X)
# Fit PCA and transform X.
pca=PCA(n_components=.90)
pca.fit(X)
print('Variance explained by the principal components(in decreasing order): ',pca.explained_variance_ratio_)
#print('PCA singular values: ',pca.singular_values_)
X1=pca.transform(X)
print('Shape of transformed X: ',X1.shape)

"""Notice that we need 7 principal components to explain 90% of the variance in the data. Plotting the first two principal components below, which together explain approximately 47% of the total variance, we observe that the two classes have been differentiated to some extent but not enough.  """

plt.figure()
sns.scatterplot(X1[:,0],X1[:,1], hue=Y, palette='deep')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('Scatter Plot of First two Principal Component')
plt.show()

"""How about plotting the first 3 principal components in a 3D plot and check how well our data is classified. These 3 components together explain 61% of the variance in the data."""

from mpl_toolkits.mplot3d import Axes3D
plt.style.use('classic')
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X1[:,0],X1[:,1], X1[:,2], c=data.Outcome, s=30)
ax.view_init(10, 100)
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_zlabel('PC3')
plt.tight_layout()
plt.show()

"""#Model buliding"""

X = data.iloc[:,0:8]
Y = data.iloc[:,8]
seed = 7
test_size = 0.20
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)
print("Shape of X_train:", X_train.shape)
print("Shape of X_test:", X_test.shape)

"""## K-Nearest Neighbors"""

knn=KNeighborsClassifier(n_neighbors=10)
knn.fit(X_train,y_train)

#compute accuracy
scores = cross_val_score(knn, X, Y, cv=RepeatedStratifiedKFold(n_repeats=CV_N_REPEATS))
print(f"Accuracy mean={scores.mean():0.2f} +/- {scores.std():0.2f} (1 s.d.)")

KNN = KNeighborsClassifier(11)
KNN.fit(X_train,y_train)
y_test_knn = KNN.predict(X_test)
print(classification_report(y_test, y_test_knn))

y_pred=knn.predict(X_test)

from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
p = sns.heatmap(pd.DataFrame(cnf_matrix), annot=True, cmap="YlGnBu" ,fmt='g')
plt.title('Confusion matrix', y=1.1)
plt.ylabel('Actual label')
plt.xlabel('Predicted label')

error_rate = []
for i in range(1,50):

  KNN = KNeighborsClassifier(n_neighbors=i)
  KNN.fit(X_train,y_train)
  pred_i =KNN.predict(X_test)
  error_rate.append(np.mean(pred_i != y_test))

plt.figure(figsize=(10,6))
plt.plot(range(1,50),error_rate,color='blue',linestyle='dashed',marker='o',
         markerfacecolor='red', markersize=10)
plt.title('error Rate vs K Value')
plt.xlabel('k')
plt.ylabel('error rate')

from sklearn.model_selection import GridSearchCV
#In case of classifier like knn the parameter to be tuned is n_neighbors
param_grid = {'n_neighbors':np.arange(1,50)}
knn = KNeighborsClassifier()
knn_cv= GridSearchCV(knn,param_grid,cv=5)
knn_cv.fit(X,Y)

print("Best Score:" + str(knn_cv.best_score_))
print("Best Parameters: " + str(knn_cv.best_params_))

import pickle

knn=KNeighborsClassifier(n_neighbors=14)
knn.fit(X_train,y_train)

#compute accuracy
scores = cross_val_score(knn, X, Y, cv=RepeatedStratifiedKFold(n_repeats=CV_N_REPEATS))
print(f"Accuracy mean={scores.mean():0.2f} +/- {scores.std():0.2f} (1 s.d.)")

KNN = KNeighborsClassifier(14)
KNN.fit(X,Y)
y_test_knn = KNN.predict(X_test)
print(classification_report(y_test, y_test_knn))

pkl_filename = "KNN.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(KNN, file)

y_pred=knn.predict(X_test)

from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
p = sns.heatmap(pd.DataFrame(cnf_matrix), annot=True, cmap="YlGnBu" ,fmt='g')
plt.title('Confusion matrix', y=1.1)
plt.ylabel('Actual label')
plt.xlabel('Predicted label')





visualizer = DiscriminationThreshold(knn_cv)

visualizer.fit(X, Y)
visualizer.poof()

Importance = pd.DataFrame({'Importance':GradientBoostingClassifier().fit(X, Y).feature_importances_*100},
                          index = X.columns)

Importance.sort_values(by = 'Importance',
                       axis = 0,
                       ascending = True).plot(kind = 'barh',
                                              color = 'r', figsize=(8,6))

plt.xlabel('Variable Importance')
plt.gca().legend_ = None

"""# LightGBM - Discrimination Threshold


"""

y=Y

random_state=42

#number of combinations
n_iter = 300

#intialize lgbm and lunch the search
lgbm_clf = lgbm.LGBMClassifier(random_state=random_state, silent=True, metric='None', n_jobs=4)

models = []
models.append(("LightGBM", lgbm_clf))

# evaluate each model in turn
results = []
names = []

for name, model in models:

        kfold = KFold(n_splits = 10, random_state = 123456)
        cv_results = cross_val_score(model, X, Y, cv = 10, scoring= "accuracy")
        results.append(cv_results)
        names.append(name)
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)

lgbm_clf.fit(X_train,y_train)

#compute accuracy
scores = cross_val_score(lgbm_clf, X, Y, cv=RepeatedStratifiedKFold(n_repeats=CV_N_REPEATS))
print(f"Accuracy mean={scores.mean():0.2f} +/- {scores.std():0.2f} (1 s.d.)")

y_test_lgbm = lgbm_clf.predict(X_test)
print(classification_report(y_test, y_test_lgbm))

pkl_filename = "LGBM.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(lgbm_clf, file)

from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_test_lgbm)
p = sns.heatmap(pd.DataFrame(cnf_matrix), annot=True, cmap="YlGnBu" ,fmt='g')
plt.title('Confusion matrix', y=1.1)
plt.ylabel('Actual label')
plt.xlabel('Predicted label')

visualizer = DiscriminationThreshold(lgbm_clf)

visualizer.fit(X, y)
visualizer.poof()

"""#***KNN+LGBM***"""

knn_clf = KNeighborsClassifier()

voting_clf = VotingClassifier(estimators=[
    ('lgbm_clf', lgbm.LGBMClassifier()),
    ('knn', KNeighborsClassifier())], voting='soft', weights = [1,1])

params = {
      'knn__n_neighbors': np.arange(30)
      }

grid = GridSearchCV(estimator=voting_clf, param_grid=params, cv=10)

grid.fit(X,Y)

print("Best Score:" + str(grid.best_score_))
print("Best Parameters: " + str(grid.best_params_))

y_test_grid = grid.predict(X_test)
print(classification_report(y_test, y_test_lgbm))

pkl_filename = "Final.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(grid, file)

from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_test_grid)
p = sns.heatmap(pd.DataFrame(cnf_matrix), annot=True, cmap="YlGnBu" ,fmt='g')
plt.title('Confusion matrix', y=1.1)
plt.ylabel('Actual label')
plt.xlabel('Predicted label')

visualizer = DiscriminationThreshold(voting_clf)

visualizer.fit(X, y)
visualizer.poof()

X_test.columns

def p(a):
  y_test_grid = grid.predict([a])
  if y_test_grid[0] == 1:
    print("The patient is Diabetic")
  else:
    print("The patient is Healthy")

a = [6,93,50,30,64,28.7,0.356,23]
p(a)

a = [13,152,90,33,29,26,0.731,43]
p(a)

"""# Thank You For Attending My Final Review"""

