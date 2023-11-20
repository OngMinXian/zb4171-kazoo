import json
import pandas as pd
import boto3

def lambda_handler(event, context):
    
    print('Triggering DESeq2 analysis')
    
    # Logic for checking for every 20 samples before running DESeq2
    sample_count = 0
    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket='zb4171', Prefix='kazoo/results/')
    for page in pages:
        for obj in page['Contents']:
            obj_key = obj['Key']
            if obj_key.endswith('/star_rsem/rsem.merged.gene_counts.tsv') and 'failed_runs' not in obj_key and 'archive' not in obj_key and 'K2' not in obj_key:
                sample_count += 1
    print('Total samples analyzed:', sample_count)
    
    # Check whether sample count is multiple of 10 before analyzing
    if sample_count % 10 != 0:
        return {
            'statusCode': 200,
            'body': json.dumps('Sample count not multiple of 10')
        } 
    
    # Create batch job
    batch_cilent = boto3.client('batch')
    batch_cilent.submit_job(
        jobName=f'zb4171-kazoo-deseq-combined',
        jobQueue='arn:aws:batch:ap-southeast-1:130113215616:job-queue/zb4171-kazoo-queue',
        jobDefinition='arn:aws:batch:ap-southeast-1:130113215616:job-definition/zb4171-kazoo-deseq:2',
        containerOverrides={
            'command': ["bash", "script.sh"]
        },
        tags={
            'zb4171': 'kazoo'
        },
    )
    print(f'Batch job created')
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('DESeq2 batch job sent')
    }