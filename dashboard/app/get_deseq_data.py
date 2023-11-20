import boto3
import pandas as pd
from cachetools import cached, TTLCache
from caches import deseq_result_cache
from get_s3_data import *

def get_combined_deseq_result():
    # Get result
    deseq_result = s3_client.get_object(
        Bucket='zb4171',
        Key='kazoo/results_deseq_combined/tables/differential/condition_cancer_vs_normal.deseq2.results.tsv'
    )['Body']
    df = pd.read_csv(deseq_result, sep='\t')
    df = df.rename(columns={'gene_id': 'HGNC symbol'}).drop(columns=['lfcSE', 'pvalue'])
    return df

@cached(cache=deseq_result_cache)
def get_deseq_result(organ):
    if organ == 'combined':
        return get_combined_deseq_result()

    # Get result based on organ
    pages = list_objects('kazoo/results_deseq/tables/differential/')
    for page in pages:
        for obj in page['Contents']:
            obj_key = obj['Key']
            if organ in obj_key and obj_key.endswith('.results.tsv'):
                deseq_result = s3_client.get_object(Bucket='zb4171', Key=obj_key)['Body']
                df = pd.read_csv(deseq_result, sep='\t')
                df = df.rename(columns={'gene_id': 'HGNC symbol'}).drop(columns=['lfcSE', 'pvalue'])
                return df
