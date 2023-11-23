import pandas as pd

# extract 1k normal and 1k cancer for model training and feature selection 
dfnormal_train = pd.read_csv('normal_train_data.csv')
dfcancer_train = pd.read_csv('cancer_train_data.csv')
dfnormal_train.set_index('gene_id',inplace=True,drop=True)
dfcancer_train.set_index('gene_id',inplace=True,drop=True)

# sample 1k normal
dfnormal_train_sample = dfnormal_train.T.sample(n=1000,random_state=42)
# sample 1k cancer
dfcancer_train_sample = dfcancer_train.T.sample(n=1000,random_state=42)


# concat the 1k normal and 1k cancer
df = pd.concat([dfnormal_train_sample.T,dfcancer_train_sample.T],axis=1)
df.to_csv('train_set_2k.csv')

# create metadata 
lst_col_name = list(df.columns)
lst_label = (["normal"] * 1000) + (["cancer"] * 1000)
metadata = pd.DataFrame(zip(lst_col_name,lst_label),columns=['sample_id','condition'])
mapping = {'normal':0, 'cancer':1}
metadata['label'] = metadata['condition'].map(mapping)
metadata.to_csv('train_set_2k_metadata.csv',index=False)