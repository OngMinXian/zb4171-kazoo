import boto3
import pandas as pd

# AWS cilents
s3_client = boto3.client('s3')

# Find filename of all cancer tsv files for input into DESeq
print('Getting df of cancer counts')
cancer_data = []
for obj in s3_client.list_objects(Bucket='zb4171', Prefix='kazoo/data_deseq/')['Contents']:
    obj_key = obj['Key']
    if obj_key.endswith('gene_counts.tsv') and 'failed_runs' not in obj_key:
        sample_id = obj_key.split('data_deseq/')[1].split('/star_rsem/')[0]
        tsv_file = s3_client.get_object(Bucket='zb4171', Key=obj_key)['Body']
        df = pd.read_csv(tsv_file, sep='\t')
        df = df[['gene_id', 'expected_count']].rename(columns={'expected_count': sample_id})
        cancer_data.append(df)

# Find filename of all normal tsv files for input into DESeq
print('Getting df of normal counts')
normal_data = []
for obj in s3_client.list_objects(Bucket='zb4171', Prefix='kazoo/data_deseq_normal/')['Contents']:
        obj_key = obj['Key']
        if obj_key.endswith('.tsv') and 'pancancer' in obj_key:
            tsv_file = s3_client.get_object(Bucket='zb4171', Key=obj_key)['Body']
            df = pd.read_csv(tsv_file, sep='\t').rename(columns={'SYMBOL': 'gene_id'}).dropna(axis=0).drop_duplicates(subset=['gene_id'])
            normal_data.append(df)

# Make samplesheet.csv
print('Make samplesheet')
sample_lst = []
condition_lst = []
replicate_lst = []

cancer_counts = 1
for df in cancer_data:
    for sample_id in df.drop(columns='gene_id').columns:
        sample_lst.append(sample_id)
        condition_lst.append(f'cancer')
        replicate_lst.append(cancer_counts)
        cancer_counts += 1

normal_counts = 1
for df in normal_data:
    for sample_id in df.drop(columns='gene_id').columns:
        if sample_id == 'Unnamed: 0':
            continue
        sample_lst.append(sample_id)
        condition_lst.append(f'normal')
        replicate_lst.append(normal_counts)
        normal_counts += 1

df_samplesheet = pd.DataFrame({
    'sample': sample_lst,
    'condition': condition_lst,
    'replicate': replicate_lst,
})

# Make contrast.csv
print('Make contrast')
id_lst = ['condition_cancer_vs_normal']
variable_lst = ['condition']
reference_lst = ['normal']
target_lst = ['cancer']

df_contrast = pd.DataFrame({
    'id': id_lst,
    'variable': variable_lst,
    'reference': reference_lst,
    'target': target_lst,
})

# Make count matrix
print('Make count matrix')
df_counts = pd.DataFrame()
for df in cancer_data:
    if df_counts.empty:
        df_counts = df
    else:
        df_counts = df_counts.merge(df, on='gene_id', how='inner')

for df in normal_data:
    df_counts = df_counts.merge(df, on='gene_id', how='inner')

# Fill na with 0 and remove rows with all 0
df_counts = df_counts.fillna(0)
df_counts = df_counts.loc[~(df_counts==0).all(axis=1)]

# Check for _x and _y
df_counts

# Save as CSV
df_samplesheet.to_csv('samplesheet.csv', index=False)
df_contrast.to_csv('contrast.csv', index=False)
df_counts.to_csv('cancer_counts.tsv', sep='\t')
