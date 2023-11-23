import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import StratifiedKFold 
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score , classification_report

import timeit

starting_time = timeit.default_timer()

df = pd.read_csv('./train_set_2k_norm_pt.csv')
df.set_index('gene_id',drop=True, inplace=True)


file_lst = ['top100deg.txt', 'NCG_gene_lst.txt', 'xgbfeaimp_weight_full_lst.txt', 'xgbfeaimp_weight_top20.txt', 'xgbfeaimp_gain_full_lst.txt', 'xgbfeaimp_gain_top156.txt']

for file in file_lst:
    genes_to_keep = []
    with open (file, 'r') as f:
        for line in f:
            genes_to_keep.append(line.strip())

    df_train = df[df.index.isin(genes_to_keep)]

    # transpose the df
    df_train = df_train.T

    df_y= pd.read_csv('./train_set_2k_metadata.csv')
    df_train['label'] = list(df_y['label'])

    x = df_train.drop(columns='label')
    y = df_train['label']

    list_f1_score = []
    list_acc_score = []

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

    scoredf = pd.DataFrame(zip(list_acc_score,list_f1_score),columns=['accuracy','f1score'])
    filename = 'cv_scoredf_xgb_' + str(file.split('.')[0]) + '.csv'
    scoredf.to_csv(filename)

print("Time taken :", timeit.default_timer() - starting_time)