import boto3
from cachetools import cached, TTLCache
from caches import s3_cache
from s3_client import s3_client

@cached(cache=s3_cache)
def list_objects(path):
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket='zb4171', Prefix=path)
    return pages
