import boto3
from get_s3_data import *
from caches import sample_id_cache

@cached(cache=sample_id_cache)
def get_sample_ids():
    sample_ids = []

    for folder in s3_client.list_objects(Bucket='zb4171', Prefix='kazoo/results/', Delimiter='/').get('CommonPrefixes'):
        sample_id = folder['Prefix'].split('kazoo/results/')[1].split('/')[0]
        if sample_id in ['failed_runs', 'archive', 'K2', 'testindex', 'testrun']:
            continue
        sample_ids.append(sample_id)
    
    return sample_ids