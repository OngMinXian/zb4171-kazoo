import boto3
import pandas as pd
import numpy as np
from cachetools import cached, TTLCache
from caches import sample_metadata_cache
from get_sample_ids import *

@cached(cache=sample_metadata_cache)
def get_sample_metadata(filter=False):

    # Retrieve patient metadata
    df_metadata = pd.read_csv('patientinformation.csv', encoding='windows-1254')

    # Filter for only samples analyzed
    if filter:
        sample_ids = get_sample_ids()
        df_metadata = df_metadata[df_metadata['Patient ID'].isin(sample_ids)]

    # Clean and process data
    def age_helper(age):
        try:
            return int(age)
        except:
            try:
                if '-' in age:
                    bot, top = age.split(' - ')
                    return (int(top) + int(bot)) / 2
                elif 'or older' in age:
                    return 90
            except:
                return np.NaN
    df_metadata['Age atDiagnosis'] = df_metadata['Age atDiagnosis'].apply(age_helper)

    return df_metadata.sort_values(by='Patient ID')
