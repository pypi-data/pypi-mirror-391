import os
import glob


def get_dataset_txt(dataset_path, dataset_file):
    file_data = glob.glob(os.path.join(dataset_path, "*.jpg"))
    with open(dataset_file, "w") as f:
        for file in file_data:
            f.writelines(f"{file}\n")

