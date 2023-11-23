import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold 

import matplotlib.pyplot as plt
import timeit
import modeldata as md


starting_time = timeit.default_timer()

df = pd.read_csv('./train_set_2k_norm_pt.csv')
df.set_index('gene_id',drop=True, inplace=True)

genes_to_keep = []
with open ('xgbfeaimp_weight_top20.txt', 'r') as file:
    for line in file:
        genes_to_keep.append(line.strip())

df = df[df.index.isin(genes_to_keep)]

# transpose the df
df = df.T

df_y= pd.read_csv('./train_set_2k_metadata.csv')
df['label'] = list(df_y['label'])


x = df.drop(columns='label')
y = df['label']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42, stratify=y)

scaler = MinMaxScaler()
x_train = pd.DataFrame(scaler.fit_transform(x_train), columns=x_train.columns)

scaler = MinMaxScaler()
x_test = pd.DataFrame(scaler.fit_transform(x_test), columns=x_test.columns)

# 10fold cv    
cv = StratifiedKFold(n_splits=10, random_state=42, shuffle=True)
list_score = []
list_testsetscore = []
    
testset_y = pd.DataFrame(y_test).reset_index(drop=True)
testset= pd.concat([x_test, testset_y],axis=1)

# Run 10fold cv on each model
modelchoie = ['randomforest','xgboost','lgbm', 'svc']
for model in modelchoie:
    print("Currently running this model: ",model)
    for train_idx, valid_idx in cv.split(x_train, y_train):
        trainset = x_train.iloc[list(train_idx)]
        validset = x_train.iloc[list(valid_idx)]
        
        trainset_y = y_train.iloc[list(train_idx)]
        validset_y = y_train.iloc[list(valid_idx)]
        
        trainset.loc[:, 'label'] = list(trainset_y)
        validset.loc[:, 'label'] = list(validset_y)
        
        validscore = md.callmodel(trainset, model, separatetestset=True, testsetdf=validset, all=True)
        list_score.append(validscore)
        
        testsetscore = md.callmodel(trainset, model, separatetestset=True, testsetdf=testset, all=True)
        list_testsetscore.append(testsetscore)
        
outputdf = pd.DataFrame({'list_score': list_score, 'list_testsetscore': list_testsetscore })
outputdf.to_csv('modelselectionresult_2k_norm_pt_weight_gene_top20.csv', index=False)


print("Time taken :", timeit.default_timer() - starting_time)
