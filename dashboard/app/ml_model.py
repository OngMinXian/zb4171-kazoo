import boto3
import pandas as pd
from get_s3_data import *
from cachetools import cached, TTLCache
from caches import ml_model_cache
import s3fs

import joblib
from xgboost import XGBClassifier

@cached(cache=ml_model_cache)
def get_model():
    fs = s3fs.S3FileSystem()
    filename = 's3://zb4171/kazoo/ml_model/fullDataSet-xgboost-pc1-corr-gene.joblib'
    with fs.open(filename, encoding='utf8') as fh:
        model = joblib.load(fh)
    return model

def predict_cancer(x_test):
    # Retrieve model from s3
    xgbclf = get_model()

    # Get features of model
    features = xgbclf.get_booster().feature_names
    df_features = pd.DataFrame({'gene_id': features})

    # Ensures data to be predicted matches features
    ensl_mapping = pd.read_csv('Ensl2Symbol.csv')
    if 'ENS' in x_test['gene_id'].values[0]:
        x_test = x_test.merge(ensl_mapping, on='gene_id', how='left')
        x_test['gene_id'] = x_test['gene_name']
        x_test = x_test.drop(columns='gene_name')
    x_test = x_test.merge(df_features, on='gene_id', how='right')
    x_test = x_test.pivot_table(columns='gene_id', values=x_test.columns[1], aggfunc='sum')

    y_pred = xgbclf.predict(x_test)[0]
    if y_pred:
        return True
    else:
        return False

# test = pd.read_csv('rsem.merged.gene_counts.tsv', sep='\t')
# test = test[['gene_id', '174125']]
# print(predict_cancer(test))
