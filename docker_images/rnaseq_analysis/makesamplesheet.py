import boto3
import csv
import sys

def list_files_in_s3_bucket(prefix):
    s3_client = boto3.client('s3')
    objects = s3_client.list_objects_v2(Bucket="zb4171", Prefix=prefix)
    file_paths = []
    
    if ('Contents' in objects):
        for obj in objects['Contents']:
            if obj['Size'] != 0:
                print(obj['Key'],obj['Size'])
                file_paths.append("s3://zb4171/{}".format(obj['Key']))
    else:
        sys.exit(1)
    
    return file_paths

def extract_files_with_keywords(file_paths):
    file1, file2 = None, None

    for file_path in file_paths:
        if "r1.fastq.gz" in file_path.lower():
            file1 = file_path
        elif "r2.fastq.gz" in file_path.lower():
            file2 = file_path
    
    return file1, file2

def create_csv(sample, file1, file2):
    with open("samplesheet.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["sample", "fastq_1", "fastq_2", "strandedness"])
        writer.writerow([sample, file1, file2, "auto"])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <sampleID>")
        sys.exit(1)

    sampleID = sys.argv[1]
    
    prefix = "kazoo/data/{}/".format(sampleID)

    file_paths = list_files_in_s3_bucket(prefix)
    
    file1, file2 = extract_files_with_keywords(file_paths)
    
    if not file1 or not file2:
        print("Could not find files with R1 and R2 keywords in given directory.")
        sys.exit(1)

    create_csv(sampleID, file1, file2)
