import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer


def powertransform (dataframe, method='yeo-johnson'):
    df = dataframe.T
    pt = PowerTransformer(method=method)
    df = pd.DataFrame(pt.fit_transform(df), columns=df.columns,index=df.index)
    df = df.astype('float32')
    return df.T

df = pd.read_csv('train_set_2k_norm.csv')
df.set_index('gene_id',drop=True, inplace=True)
df = powertransform(df)
df.to_csv('train_set_2k_norm_pt.csv')