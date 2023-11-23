import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, f1_score, precision_score , classification_report,recall_score
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import pickle
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
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42, stratify=y)

scaler = MinMaxScaler()
x_train = pd.DataFrame(scaler.fit_transform(x_train), columns=x_train.columns)

scaler = MinMaxScaler()
x_test = pd.DataFrame(scaler.fit_transform(x_test), columns=x_test.columns)

#########################################################################

xgbclf = XGBClassifier(n_jobs=-1)
eval_set = [(x_train, y_train), (x_test, y_test)]
xgbclf.fit(x_train, y_train, eval_metric=["error", "logloss", "auc"], eval_set=eval_set, verbose=True)
y_pred = xgbclf.predict(x_test)

# evaluate predictions
f1score = f1_score(y_test, y_pred)
matrix = confusion_matrix(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
print('F1_score :', f1score)
print('Precision :', precision)
print('Recall :', recall)
print('Confusion matrix: \n', matrix)

# model result
result = xgbclf.evals_result()
epochs = len(result['validation_0']['error'])
x_axis = range(0, epochs)

# plot log loss
fig, ax = plt.subplots()
ax.plot(x_axis, result['validation_0']['logloss'], label='Train')
ax.plot(x_axis, result['validation_1']['logloss'], label='Test')
ax.legend()
plt.ylabel('Logloss')
plt.xlabel('epoch')
plt.title('XGBoost Logloss')
filename = f'fullDataset10k_eval_logloss_V2.png'
plt.savefig(filename, dpi=300,bbox_inches='tight')

# plot classification error
fig, ax = plt.subplots()
ax.plot(x_axis, result['validation_0']['error'], label='Train')
ax.plot(x_axis, result['validation_1']['error'], label='Test')
ax.legend()
plt.ylabel('Classification Error')
plt.xlabel('epoch')
plt.title('XGBoost Classification Error')
filename = f'fullDataset10k_eval_error_V2.png'
plt.savefig(filename, dpi=300,bbox_inches='tight')

# plot AUC
fig, ax = plt.subplots()
ax.plot(x_axis, result['validation_0']['auc'], label='Train')
ax.plot(x_axis, result['validation_1']['auc'], label='Test')
ax.legend()
plt.ylabel('AUC')
plt.xlabel('epoch')
plt.title('XGBoost AUC')
filename = f'fullDataset10k_eval_auc_V2.png'
plt.savefig(filename, dpi=300,bbox_inches='tight')

filename = f'fullDataset10k_eval_V2.joblib'
pickle.dump(xgbclf, open(filename, 'wb'))

print("Time taken :", timeit.default_timer() - starting_time)