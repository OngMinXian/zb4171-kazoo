echo "DEseq pipeline"

# Copy required files from S3 bucket
echo "Copying files from S3"
aws s3 cp "s3://zb4171/kazoo/pipelines/differentialabundance/template.config" ./template.config
aws s3 cp "s3://zb4171/kazoo/pipelines/differentialabundance/params.json" ./params.json
aws s3 cp "s3://zb4171/kazoo/pipelines/differentialabundance/sample_metadata.csv" ./sample_metadata.csv
aws s3 cp "s3://zb4171/kazoo/pipelines/differentialabundance/differentialabundance.nf" ./differentialabundance.nf
aws s3 cp "s3://zb4171/kazoo/pipelines/differentialabundance/cancer_types.txt" ./cancer_types.txt

# Run python/R scripts
echo "Running python scripts"
python3 make_csv.py

# Run nextflow script
echo "Running nextflow script"
nextflow run nf-core/differentialabundance -c template.config -params-file params.json -profile docker

# Output results back into S3
echo "Copying files to S3"
aws s3 sync ./results s3://zb4171/kazoo/results_deseq/

# Log command line outputs
echo "Batch job completed"
