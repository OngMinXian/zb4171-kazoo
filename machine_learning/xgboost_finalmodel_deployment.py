import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.preprocessing import MinMaxScaler
import pickle
import timeit



starting_time = timeit.default_timer()

df = pd.read_csv('./fullDataset10_norm_pt.csv')
df.set_index('gene_id',drop=True, inplace=True)

# remove genes based on pc1 correlated genes 
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


scaler = MinMaxScaler()
x = pd.DataFrame(scaler.fit_transform(x), columns=x.columns)

clf = XGBClassifier(n_jobs=-1)
clf.fit(x, y)
filename = f'./fullDataset10k_weight20_wo_test.joblib'
pickle.dump(clf, open(filename, 'wb'))


print("Time taken :", timeit.default_timer() - starting_time)
