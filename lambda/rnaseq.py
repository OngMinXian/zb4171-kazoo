import json
import pandas as pd
import boto3

def lambda_handler(event, context):
    
    # Define pipeline to run
    pipeline = 'rnaseq-analysis'
    
    # Reads sample sheet into pandas df
    samplesheet_filename = event['Records'][0]['s3']['object']['key']
    print(f'Filename: {samplesheet_filename}')
    
    s3 = boto3.client('s3')
    samplesheet = s3.get_object(Bucket='zb4171', Key=samplesheet_filename)['Body']
    df = pd.read_csv(samplesheet)
    print('Samplesheet loaded')
    
    # Get email from samplesheet
    try:
        email = df['Email'].values[0]
        if type(email) != str:
            email = 'e0540516@u.nus.edu'
    except:
        email = 'e0540516@u.nus.edu'
    print(f'Sending notification email to {email}')
    
    # Create batch job for each sample
    batch_cilent = boto3.client('batch')
    for sample_id in df['Sample'].values:
        print('Creating batch job for', sample_id)
        batch_cilent.submit_job(
            jobName=(f'zb4171_kazoo_rnaseq_{sample_id}').replace(" ", "").replace(".", ""),
            jobQueue='arn:aws:batch:ap-southeast-1:130113215616:job-queue/zb4171-kazoo-queue-500ebs',
            jobDefinition='arn:aws:batch:ap-southeast-1:130113215616:job-definition/zb4171-kazoo-launch-nextflow:10',
            containerOverrides = {
                'command': ["bash", "script.sh", str(sample_id), pipeline, email]
            },
            tags={
                'zb4171': 'kazoo'
            },
        )
        print(f'Batch job for {sample_id} created')
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successful execution')
    }