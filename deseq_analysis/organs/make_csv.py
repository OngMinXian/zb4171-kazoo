import boto3
import pandas as pd

sample_data = {}

# AWS cilents
s3_client = boto3.client('s3')

# Read cancer types
cancer_types = []
with open('cancer_types.txt') as f:
    for line in f.readlines():
        cancer_types.append(line.strip())

# Import sample ID to cancer type mapping
sample_id_to_cancer = pd.read_csv('sample_metadata.csv', encoding='unicode_escape')[['Patient ID', 'Sample ID', 'CTEP SDCDescription']]
sample_id_to_cancer = sample_id_to_cancer[sample_id_to_cancer['Sample ID'] == 'ORIGINATOR']
cancer_rename = {
    'colon': 'colon',
    'pancreas': 'pancreas',
    'sarcoma': 'sarcoma',
    'melanoma': 'skin',
    'endometrioid': 'female reproductive',
    'lung': 'lung',
    'breast': 'breast',
    'bladder': 'bladder',
    'histiocytoma': 'sarcoma',
    'fibrosarcoma ': 'sarcoma',
    'oral': 'oral',
    'ovarian': 'female reproductive',
    'uterus': 'female reproductive',
    'squamous': 'skin',
    'rcc': 'rectum',
    'rectum': 'rectum',
    'liposarcoma': 'sarcoma',
    'cholangiocar': 'liver',
    'ovarian': 'female reproductive',
    'colorectal': 'colon',
    'female reprod': 'female reproductive',
    'vaginal ': 'female reproductive',
    'cervical': 'female reproductive',
    'soft tissue': 'sarcoma',
    'skin': 'skin',
    'uterine': 'female reproductive',
    'rhabdomyosarcoma': 'sarcoma',
    'endometrial': 'female reproductive',
    'skin': 'skin',
    'uterus': 'female reproductive',
    'vulvar': 'female reproductive',
}
def helper(x):
    for k, v in cancer_rename.items():
        if k in x.lower():
            return v
    return x
sample_id_to_cancer['CTEP SDCDescription'] = sample_id_to_cancer['CTEP SDCDescription'].apply(helper)

# Find filename of all cancer tsv files for input into DESeq
print('Getting filenames of cancer counts')
for obj in s3_client.list_objects(Bucket='zb4171', Prefix='kazoo/data_deseq/')['Contents']:
    obj_key = obj['Key']
    if obj_key.endswith('gene_counts.tsv') and 'failed_runs' not in obj_key:
        sample_id = obj_key.split('kazoo/data_deseq/')[1].split('/')[0]
        cancer_type = sample_id_to_cancer[sample_id_to_cancer['Patient ID'] == sample_id]['CTEP SDCDescription'].values[0]
        if cancer_type not in cancer_types:
            continue
        cancer_type_dict = sample_data.get(cancer_type, {})
        cancer_type_dict[sample_id] = obj_key
        sample_data[cancer_type] = cancer_type_dict

# Find filename of all normal tsv files for input into DESeq
print('Getting filenames of normal counts')
normal_data = {}
for obj in s3_client.list_objects(Bucket='zb4171', Prefix='kazoo/data_deseq_normal/')['Contents']:
    for cancer in cancer_types:
        obj_key = obj['Key']
        if obj_key.endswith('.tsv') and cancer in obj_key:
            normal_data[cancer] = normal_data.get(cancer, []) + [obj_key]

# Make samplesheet.csv
print('Make samplesheet')
sample_lst = []
condition_lst = []
replicate_lst = []

cancer_counts = {}
for cancer_type, data in sample_data.items():
    for sample_id, filename in data.items():
        sample_lst.append(sample_id)
        condition_lst.append(f'cancer {cancer_type}')
        count = cancer_counts.get(cancer_type, 0)
        count += 1
        cancer_counts[cancer_type] = count
        replicate_lst.append(count)

normal_counts = {}
for cancer_type, data in normal_data.items():
    for filename in data:
        tsv_file = s3_client.get_object(Bucket='zb4171', Key=filename)['Body']
        df = pd.read_csv(tsv_file, sep='\t').rename(columns={'SYMBOL': 'gene_id'}).drop(columns='gene_id')
        for sample_name in df.columns:
            sample_lst.append(sample_name)
            condition_lst.append(f'normal {cancer_type}')
            count = normal_counts.get(cancer_type, 0)
            count += 1
            normal_counts[cancer_type] = count
            replicate_lst.append(count)

df_samplesheet = pd.DataFrame({
    'sample': sample_lst,
    'condition': condition_lst,
    'replicate': replicate_lst,
})
df_samplesheet.to_csv('samplesheet.csv', index=False)

# Make contrast.csv
print('Make contrast')
id_lst = []
variable_lst = []
reference_lst = []
target_lst = []
for i in range(len(cancer_types)):
    id_lst.append(f'condition_{cancer_types[i]}_cancer')
    variable_lst.append('condition')
    reference_lst.append(f'normal {cancer_types[i]}')
    target_lst.append(f'cancer {cancer_types[i]}')

df_contrast = pd.DataFrame({
    'id': id_lst,
    'variable': variable_lst,
    'reference': reference_lst,
    'target': target_lst,
})
df_contrast.to_csv('contrast.csv', index=False)

# Make count matrix
print('Make count matrix')
df_counts = 0

for cancer_type, data in sample_data.items():
    for sample_id, filename in data.items():
        tsv_file = s3_client.get_object(Bucket='zb4171', Key=filename)['Body']
        df = pd.read_csv(tsv_file, sep='\t')
        df = df[['gene_id', 'expected_count']].rename(columns={'expected_count': sample_id})
        if type(df_counts) == int:
            df_counts = df
        else:
            df_counts = df_counts.merge(df, on='gene_id')
df_counts = df_counts.drop_duplicates(subset=['gene_id'])

for cancer_type, data in normal_data.items():
    for filename in data:
        tsv_file = s3_client.get_object(Bucket='zb4171', Key=filename)['Body']
        df = pd.read_csv(tsv_file, sep='\t').rename(columns={'SYMBOL': 'gene_id'}).dropna(axis=0).drop_duplicates(subset=['gene_id'])
        df_counts = df_counts.merge(df, on='gene_id', how='inner')

# Fill na with 0 and remove rows with all 0
df_counts = df_counts.fillna(0)
df_counts = df_counts.loc[~(df_counts==0).all(axis=1)]
df_counts.to_csv('cancer_counts.tsv', sep='\t')
