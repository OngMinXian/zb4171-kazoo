import sys

# To replace the placeholder in the config file with the actual sample ID
def generate_config_file(template_path, sample_id):
    with open(template_path, 'r') as f:
        template = f.read()
    
    config_content = template.replace("SAMPLEID", sample_id)

    with open(f"{sample_id}.config", "w") as f:
        f.write(config_content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python makeconfig.py TEMPLATE_PATH SAMPLEID")
        sys.exit(1)

    template_path = sys.argv[1]
    sample_id = sys.argv[2]
    
    print(f"Generating config file for {sample_id}!")
    generate_config_file(template_path, sample_id)
    print(f"config file for {sample_id} has been generated!")
