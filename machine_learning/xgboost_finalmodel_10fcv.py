import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import StratifiedKFold 
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score , classification_report

import timeit

starting_time = timeit.default_timer()

df = pd.read_csv('./fullDataset10_norm_pt.csv')
df.set_index('gene_id',drop=True, inplace=True)

genes_to_keep = []
with open ('xgbfeaimp_weight_top20.txt', 'r') as file:
    for line in file:
        genes_to_keep.append(line.strip())


df = df[df.index.isin(genes_to_keep)]

# transpose the df
df = df.T

df_y= pd.read_csv('./fullDataset10k_metadata.csv')
df['label'] = list(df_y['label'])

x = df.drop(columns='label')
y = df['label']

list_f1_score = []
list_acc_score = []
list_cm = []

cv = StratifiedKFold(n_splits=10, random_state=42, shuffle=True)
for train_idx, valid_idx in cv.split(x, y):
    trainset = x.iloc[list(train_idx)]
    validset = x.iloc[list(valid_idx)]

    trainset_y = y.iloc[list(train_idx)]
    validset_y = y.iloc[list(valid_idx)]

    trainset.loc[:, 'label'] = list(trainset_y)
    validset.loc[:, 'label'] = list(validset_y)

    x_train = trainset.drop(columns=['label'])
    y_train = trainset['label']
    x_test = validset.drop(columns=['label'])
    y_test = validset["label"]

    scaler = MinMaxScaler()
    x_train = pd.DataFrame(scaler.fit_transform(x_train), columns=x_train.columns)

    scaler = MinMaxScaler()
    x_test = pd.DataFrame(scaler.fit_transform(x_test), columns=x_test.columns)

    clf = XGBClassifier(n_jobs=-1,random_state=42)
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)

    print(f"Printing Results this iteration!")
    f1score = f1_score(y_test, y_pred)*100
    accscore = accuracy_score(y_test, y_pred)*100
    matrix = confusion_matrix(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    print('Accuracy :', accscore)
    print('F1_score :', f1score)
    print('Precision :', precision)
    print('Confusion matrix: \n', matrix)
    print('Classification Report:')
    print(classification_report(y_test, y_pred))
    list_f1_score.append(f1score)
    list_acc_score.append(accscore)
    list_cm.append(list(matrix.flatten()))
    
scoredf = pd.DataFrame(zip(list_acc_score,list_f1_score,list_cm),columns=['accuracy','f1score','cm'])
scoredf.to_csv('cv_scoredf_xgb_fullDataset_weight_top20.csv')

print("Time taken :", timeit.default_timer() - starting_time)