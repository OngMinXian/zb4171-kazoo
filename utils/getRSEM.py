import csv
import boto3

# Input CSV file
csv_file_path = 'rnasequence.csv'

# Output bash script
bash_script_path = 'wgetRSEM.sh'

# Initialize a boto3 S3 client
s3 = boto3.client('s3')

# Function to check if the patient ID exists in the S3 bucket
def is_patient_in_s3(patient_id, s3_client):
    return s3_client.list_objects_v2(Bucket='zb4171', Prefix=f'kazoo/data_deseq/{patient_id}').get('Contents', []) != []

# Create the bash script
with open(csv_file_path, 'r') as csv_file, open(bash_script_path, 'w') as bash_script:
    reader = csv.reader(csv_file)
    header = next(reader)

    # Write a shebang line to the bash script
    bash_script.write("#!/bin/bash\n\n")

    # Process each row in the CSV file
    for row in reader:
        patient_id = row[header.index('Patient ID')]
        # Check if patient ID is in the S3 bucket
        if not is_patient_in_s3(patient_id, s3):
            rsem_genes_url = row[header.index('RSEM(genes)')]

            # Append the necessary prefix to the URL
            full_rsem_genes_url = f"https://pdmdb.cancer.gov{rsem_genes_url}"

            # Get the file name from the URL
            filename = rsem_genes_url.split('/')[-1].lower()

            # Write wget command to the bash script
            bash_script.write(f"wget {full_rsem_genes_url} -O {filename}\n")

            # Write aws s3 mv command to move the file to S3 within the correct directory structure
            bash_script.write(f"aws s3 mv {filename} s3://zb4171/kazoo/data_deseq/{patient_id}/star_rsem/rsem.merged.gene_counts.tsv\n\n")

print(f"Bash script written to: {bash_script_path}")
