import pandas as pd
import gc

df = pd.read_csv('TcgaTargetGtex_gene_expected_count', delimiter='\t')
mapperdf = pd.read_csv('Ensl2Symbol.csv')
mapperdict = {}

# Mapper of Ensembl id to Gene symbol - only keep those with unqiue name and does not start with ENSG
for i , row in mapperdf.iterrows():
    if not row[1].startswith('ENSG'):    
        if row[2] not in mapperdict:
            mapperdict[row[2]] = row[1]


## Set1
cancertrainmeta = pd.read_csv('cancer_train_metadata.csv')
lst_cancer_train = cancertrainmeta['samples'].tolist()

# extract samples based on the metadata
df_cancer_train = df[lst_cancer_train]
df_cancer_train['gene_ids'] = df['sample']

# convert gene id to gene symbol
df_cancer_train['gene_ids'] = df_cancer_train['gene_ids'].apply(lambda x: x.split('.')[0])
df_cancer_train['gene_id'] = df_cancer_train['gene_ids'].map(mapperdict)
df_cancer_train.dropna(inplace=True)
df_cancer_train.drop(columns='gene_ids',inplace=True)

# groupby gene name and sum the genes counts (share genes name, likely isoform)
df_cancer_train = df_cancer_train.groupby('gene_id').sum()
df_cancer_train.to_csv('cancer_train_data.csv')
del df_cancer_train
####

## Set2
cancertestmeta = pd.read_csv('cancer_test_metadata.csv')
lst_cancer_test = cancertestmeta['samples'].tolist()
df_cancer_test = df[lst_cancer_test]
df_cancer_test['gene_ids'] = df['sample']

df_cancer_test['gene_ids'] = df_cancer_test['gene_ids'].apply(lambda x: x.split('.')[0])
df_cancer_test['gene_id'] = df_cancer_test['gene_ids'].map(mapperdict)
df_cancer_test.dropna(inplace=True)
df_cancer_test.drop(columns='gene_ids',inplace=True)

df_cancer_test = df_cancer_test.groupby('gene_id').sum()
df_cancer_test.to_csv('cancer_test_data.csv')
del df_cancer_test
###


### Set3
normaltrainmeta = pd.read_csv('normal_train_metadata.csv')
lst_normal_train = normaltrainmeta['samples'].tolist()
df_normal_train = df[lst_normal_train]
df_normal_train['gene_ids'] = df['sample']

df_normal_train['gene_ids'] = df_normal_train['gene_ids'].apply(lambda x: x.split('.')[0])
df_normal_train['gene_id'] = df_normal_train['gene_ids'].map(mapperdict)
df_normal_train.dropna(inplace=True)
df_normal_train.drop(columns='gene_ids',inplace=True)

df_normal_train = df_normal_train.groupby('gene_id').sum()
df_normal_train.to_csv('normal_train_data.csv')
del df_normal_train
###

### Set4
normaltestmeta = pd.read_csv('normal_test_metadata.csv')
lst_normal_test = normaltestmeta['samples'].tolist()
df_normal_test = df[lst_normal_test]
df_normal_test['gene_ids'] = df['sample']

df_normal_test['gene_ids'] = df_normal_test['gene_ids'].apply(lambda x: x.split('.')[0])
df_normal_test['gene_id'] = df_normal_test['gene_ids'].map(mapperdict)
df_normal_test.dropna(inplace=True)
df_normal_test.drop(columns='gene_ids',inplace=True)

df_normal_test = df_normal_test.groupby('gene_id').sum()
df_normal_test.to_csv('normal_test_data.csv')
del df_normal_test
###

