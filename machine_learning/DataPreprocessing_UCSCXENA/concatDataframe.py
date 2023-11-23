import pandas as pd
import gc

mapping = {'normal':0, 'cancer':1}

# Concat all the train_set
dfnormal_train = pd.read_csv('normal_train_data.csv')
dfcancer_train = pd.read_csv('cancer_train_data.csv')

dfnormal_train.set_index('gene_id',inplace=True,drop=True)
dfcancer_train.set_index('gene_id',inplace=True,drop=True)

dftrain = pd.concat([dfnormal_train,dfcancer_train],axis=1)
dftrain.to_csv('train_set.csv')

# create metadata 
lst_col_name = list(dftrain.columns)
lst_label = (["normal"] * 3000) + (["cancer"] * 3000) 
dftrain_metadata = pd.DataFrame(zip(lst_col_name,lst_label),columns=['sample_id','condition'])
dftrain_metadata['label'] = dftrain_metadata['condition'].map(mapping)
dftrain_metadata.to_csv('train_set_metadata.csv',index=False)

# Concat all the test_set
dfnormal_test = pd.read_csv('normal_test_data.csv')
dfcancer_test = pd.read_csv('cancer_test_data.csv')

dfnormal_test.set_index('gene_id',inplace=True,drop=True)
dfcancer_test.set_index('gene_id',inplace=True,drop=True)

dftest = pd.concat([dfnormal_test,dfcancer_test],axis=1)
dftest.to_csv('test_set.csv')

# create metadata
lst_col_name = list(dftest.columns)
lst_label = (["normal"] * 2000) + (["cancer"] * 2000) 
dftest_metadata = pd.DataFrame(zip(lst_col_name,lst_label),columns=['sample_id','condition'])
dftest_metadata['label'] = dftest_metadata['condition'].map(mapping)
dftest_metadata.to_csv('test_set_metadata.csv',index=False)

# concat all the dataframe to get the final dataset 
dfFull = pd.concat([dftrain,dftest],axis=1)
dfFullMeta = pd.concat([dftrain_metadata,dftest_metadata],axis=0)
del dftrain
del dftest
del dfnormal_train
del dfcancer_train
del dfnormal_test
del dfcancer_test
gc.collect()

dfFull.to_csv('fullDataset10k.csv')
dfFullMeta.to_csv('fullDataset10k_metadata.csv',index=False)
dfFull.to_parquet('fullDataset10k.parquet',engine='fastparquet')