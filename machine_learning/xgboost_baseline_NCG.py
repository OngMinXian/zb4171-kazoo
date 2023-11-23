import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score , classification_report
import pickle
import timeit


starting_time = timeit.default_timer()

df = pd.read_csv('./train_set_2k_norm_pt.csv')
df.set_index('gene_id',drop=True, inplace=True)

genes_to_keep = []
with open ('NCG_gene_lst.txt', 'r') as file:
    for line in file:
        genes_to_keep.append(line.strip())

df = df[df.index.isin(genes_to_keep)]

# transpose the df
df = df.T

df_y= pd.read_csv('./train_set_2k_metadata.csv')
df['label'] = list(df_y['label'])


x = df.drop(columns='label')
y = df['label']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

scaler = MinMaxScaler()
x_train = pd.DataFrame(scaler.fit_transform(x_train), columns=x_train.columns)

scaler = MinMaxScaler()
x_test = pd.DataFrame(scaler.fit_transform(x_test), columns=x_test.columns)


clf = XGBClassifier(n_jobs=-1,random_state=42)
clf.fit(x_train, y_train)
y_pred = clf.predict(x_test)

print(f"Printing Results")
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


filename = f'./trainset-norm-pt-2k-xgboost-NCG-gene.joblib'
pickle.dump(clf, open(filename, 'wb'))


print("Time taken :", timeit.default_timer() - starting_time)