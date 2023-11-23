import csv
import boto3

# Input CSV file
csv_file_path = 'rnasequence.csv'

# Input TXT file with sample IDs
sample_ids_txt_path = 'sampleids.txt'

# Output bash script
bash_script_path = 'wgetRNA.sh'

# Initialize a boto3 S3 client
s3 = boto3.client('s3')

# Function to check if the sample ID exists in the S3 bucket
def is_sample_in_s3(sampleid, s3_client):
    try:
        # This is a generator, and will make a single API call per iteration
        for obj in s3_client.list_objects_v2(Bucket='zb4171', Prefix=f'kazoo/data/{sampleid}/').get('Contents', []):
            return True
    except s3_client.exceptions.NoSuchBucket:
        print(f"Bucket does not exist")
    return False

# Read the sample IDs from the TXT file
with open(sample_ids_txt_path, 'r') as sample_ids_file:
    sample_ids = sample_ids_file.read().splitlines()

# Create the bash script
with open(csv_file_path, 'r') as csv_file, open(bash_script_path, 'w') as bash_script:
    reader = csv.reader(csv_file)
    header = next(reader)

    # Write a shebang line to the bash script
    bash_script.write("#!/bin/bash\n\n")

    # Process each sample ID
    for sampleid in sample_ids:
        # Check if sample ID is in the S3 bucket
        if not is_sample_in_s3(sampleid, s3):
            # Find the corresponding row in the CSV file
            csv_file.seek(0)  # Go back to the beginning of the CSV file
            next(reader)  # Skip the header
            for row in reader:
                if row[header.index('Patient ID')] == sampleid:
                    fastqR1 = row[header.index('Read1FASTQ')]
                    fastqR2 = row[header.index('Read2FASTQ')]

                    # Create the URLs
                    url_fastqR1 = f"https://pdmdb.cancer.gov{fastqR1}"
                    url_fastqR2 = f"https://pdmdb.cancer.gov{fastqR2}"

                    # Get file names from the paths and correct the extensions
                    filename_fastqR1 = fastqR1.split('/')[-1].lower()
                    filename_fastqR2 = fastqR2.split('/')[-1].lower()

                    # Write wget commands to the bash script
                    bash_script.write(f"wget {url_fastqR1} -O {filename_fastqR1}\n")
                    bash_script.write(f"wget {url_fastqR2} -O {filename_fastqR2}\n")

                    # Write aws s3 mv commands to move the files to S3 with the new extension
                    bash_script.write(f"aws s3 mv {filename_fastqR1} s3://zb4171/kazoo/data/{sampleid}/{filename_fastqR1}\n")
                    bash_script.write(f"aws s3 mv {filename_fastqR2} s3://zb4171/kazoo/data/{sampleid}/{filename_fastqR2}\n\n")
                    break

print(f"Bash script written to: {bash_script_path}")
