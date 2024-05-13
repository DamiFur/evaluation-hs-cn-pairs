from glob import glob
import os

for file in glob("data/data_raw/human_annotated/*"):
    comparison_file = open(file, 'r')
    comparison_data = comparison_file.read()
    if len([line for line in comparison_data.split("\n") if line != ""]) <= 1:
        os.remove(file)
        print(f"Removed {file}")