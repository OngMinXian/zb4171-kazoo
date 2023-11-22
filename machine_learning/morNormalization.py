import pandas as pd
import numpy as np

def mor_normalization(data):
    # log data
    log_data = np.log(data)
    
    # find a pseudo-reference
    log_data['pseudo_ref'] = log_data.apply(np.mean, axis=1)
    
    # remove any rows with np.inf
    log_data = log_data[log_data['pseudo_ref']!=-np.inf]
    
    # finding the ratio of the value against the pseudo-reference 
    ratio_data = log_data.sub(log_data['pseudo_ref'],axis=0)
    
    # drop pseudo-reference column
    ratio_data.drop(columns='pseudo_ref',inplace=True)
    
    # find column median in the ratios
    column_median = np.median(ratio_data,axis=0)
    
    # Exponentiate the medians to get the scaling factors
    scaling_factor = np.exp(column_median)
    
    # Divide original value by the scaling factor to normalize the value
    normalizedDf = data.div(scaling_factor,axis=1)
    normalizedDf = normalizedDf.astype('float32')
    return normalizedDf


df = pd.read_csv('/home/ec2-user/train_set_2k.csv')
df.set_index('gene_id',inplace=True,drop=True)
df = mor_normalization(df)
df.to_csv('train_set_2k_norm.csv')