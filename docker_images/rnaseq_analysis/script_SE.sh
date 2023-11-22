echo "Running $2 on sample ID $1"

# Copy required files from S3 bucket
echo "Copying files from S3"

aws s3 cp "s3://zb4171/kazoo/pipelines/$2/template.config" ./template.config
aws s3 cp "s3://zb4171/kazoo/pipelines/$2/params.json" ./params.json
aws s3 cp "s3://zb4171/kazoo/pipelines/$2/samplesheet.csv" ./samplesheet.csv

# Run python scripts
echo "Running python scripts"
python3 makeconfig.py template.config $1

# Run nextflow script
echo "Running nextflow script"
# nextflow pull nf-core/rnaseq
nextflow run nf-core/rnaseq -profile docker -c "$1.config" -params-file params.json

# Output results back into S3
echo "Copying files to S3"
aws s3 sync ./results s3://zb4171/kazoo/results/$1/

# Log command line outputs
echo "Batch job completed"
