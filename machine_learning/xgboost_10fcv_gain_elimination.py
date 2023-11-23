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
df_y= pd.read_csv('./train_set_2k_metadata.csv')


gene_lst = []
with open ('xgbfeaimp_gain_full_lst.txt', 'r') as file:
    for line in file:
        gene_lst.append(line.strip())

print(len(gene_lst))
average_acc_score = []
average_f1_score = []
for i in range(len(gene_lst)):
    if i ==0:
        genes_to_keep = gene_lst
    else:
        genes_to_keep = gene_lst[:-i]
    print(i,len(genes_to_keep))
    df_to_use = df[df.index.isin(genes_to_keep)]

    # transpose the df
    df_to_use = df_to_use.T
    
    # add label
    df_to_use['label'] = list(df_y['label'])

    x = df_to_use.drop(columns='label')
    y = df_to_use['label']
    list_f1_score = []
    list_acc_score = []

    # 10 fold CV
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

        clf = XGBClassifier(n_jobs=8,random_state=42)
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
    pathout = f'./cv_score_gain/cv_scoredf_xgb_gain_geneCount_{len(gene_lst)-i}.csv'
    scoredf.to_csv(pathout)
    average_acc_score.append(sum(list_acc_score))
    average_f1_score.append(sum(list_f1_score))

finaldf = pd.DataFrame(zip(average_acc_score,average_f1_score),columns=['ave_accuracy','ave_f1score'])
finaldf.to_csv('10fcv_gain_selection.csv')
print("Time taken :", timeit.default_timer() - starting_time)