import boto3
import pandas as pd
import json
from cachetools import cached, TTLCache
from caches import multiqc_cache
from get_s3_data import *

@cached(cache=multiqc_cache)
def get_multiqc_data():

    sample_data = {}

    # Retrieve multiqc data
    pages = list_objects('kazoo/results/')
    for page in pages:
        for obj in page['Contents']:
            obj_key = obj['Key']
            if 'multiqc' in obj_key and obj_key.endswith('.json'):
                sample_id = obj_key.split('results/')[1].split('/multiqc')[0]
                try:
                    int(sample_id)
                except:
                    continue

                sample_data[sample_id] = {}
                sample_data[sample_id]['Sample ID'] = sample_id

                # Retrieve multiqc json file
                multiqc_json = s3_client.get_object(Bucket='zb4171', Key=obj_key)['Body']
                multiqc_data = json.load(multiqc_json)
                for d in multiqc_data['report_general_stats_data']:
                    for d2 in d.values():
                        for k, v in d2.items():
                            sample_data[sample_id][k] = [v]

    # Convert dictionary data to pandas dataframe
    return pd.concat(list(map(lambda x: pd.DataFrame.from_dict(x), sample_data.values())), axis=0, ignore_index=True).sort_values(by='Sample ID')
