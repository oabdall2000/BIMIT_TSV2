

import subprocess
import sys
import warnings
from totalsegmentator.python_api import totalsegmentator
import os
import pandas as pd
from tqdm import tqdm

def install_dependencies():
    required_packages = [
        "torch",
        "totalsegmentator",
        # Add more packages as needed
    ]

    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
        except subprocess.CalledProcessError:
            print(f"Failed to install package: {package}")
            sys.exit(1)

if __name__ == "__main__":
    # Step 1: Download dependencies for TotalsegmentatorV2
    install_dependencies()
    warnings.filterwarnings(
    "ignore",
    message="You are using `torch.load` with `weights_only=False`",
    category=FutureWarning
    )
    print("------------------------------------------------------------")
    print("All dependencies (torch and totalsegmentator) are installed!")
    print("------------------------------------------------------------")

    csv_path = "totalsegmentator/resources/totalsegmentator_snomed_mapping.csv"
    data = pd.read_csv(csv_path)
    valid_classes = data['Structure'].dropna().unique().tolist()
    
    #Step 2: Set paths
    logic = 1
    while logic:
        folder_path = input("Copy the path to the folder of file(s) to segment: ")
        if not os.path.exists(folder_path):
            print(f"Folder does not exist: {folder_path}")
            print("Please try again")
        else:
            logic = 0
    logic = 1
    while logic:
        mutliple_logic = input("Do you want to run on all the '.nii.gz' files: (Y/N) ")
        if mutliple_logic not in ('Y', 'y', 'N', 'n'):
             print("Invalid input. Please enter Y/y or N/n.")
        else:
            logic = 0
    if mutliple_logic in ('N', 'n'):
        logic = 1
        while logic:
            input_file = input("What is the name of the file? ");
            temp = folder_path + '/' + input_file
            if not os.path.exists(temp):
                print(f"file does not exist: {temp}")
                print("Please try again")
            else:
                logic = 0
    logic = 1
    while logic:
        output_path = input("Copy the path to the folder you want the outputs in: ")
        if not os.path.exists(output_path):
            print(f"Folder does not exist: {folder_path}")
            print("Please try again")
        else:
            logic = 0

    #Step 3: Set GPU usage
    logic = 1
    while logic:
       
        device = input("What device are you using? (cpu/gpu): ")
        if device not in ('cpu', 'gpu'):
            print("Make sure your the answer to the following question is lowercase!!!")
            print("Invalid input. Please enter cpu or gpu.")
        else:
            logic = 0
        #Step 5: MR vs CT
        logic = 1
        while logic:
            image_mod= input("Is the input file MR or CT? (MR/CT) ")
            if image_mod not in ('MR', 'CT'):
                 print("Invalid input. Please enter 'CT'or 'MR'")
            else:
                logic = 0
        if image_mod == 'MR':
            task = "total_mr"
        else:
            task = "total"
        #Step 6: Determine class
        logic = 1
        while logic:
            class_logic = input("Are you perfoming segmentation for all classes (Y/N): ")
            if class_logic not in ('Y', 'y', 'N', 'n'):
                 print("Invalid input. Please enter Y/y or N/n.")
            else:
                logic = 0
        if class_logic in ('Y','y'):
            roi_subset = None
        else:
            logic = 1
            roi_subset =[]
            while logic:
                class_validation = 1
                while class_validation:
                    class_subset = input("What class(es) would you like to segmenent: ")
                    if class_subset not in valid_classes:
                        print(f"Invalid class '{class_subset}'. Please choose from the valid classes.")
                    else:
                        roi_subset.append(class_subset)
                        class_validation = 0
                logic_1 = 1
                while logic_1:
                    class_logic = input("Any other classes (Y/N): ")
                    if class_logic not in ('Y', 'y', 'N', 'n'):
                        print("Invalid input. Please enter Y/y or N/n.")
                    else:
                        logic_1 = 0
                if class_logic in ('N', 'n'):
                    logic = 0
            
    #Step 7: Extra stuff
    logic = 1
    while logic:
        quiet= input("Would you like the segmentation proccess to be quiet: (Y/N) ")
        if quiet not in ('Y', 'y', 'N', 'n'):
             print("Invalid input. Please enter Y/y or N/n.")
        else:
            logic = 0
    if quiet in ('Y','y'):
        quiet = 1
    else:
        quiet = 0
    logic = 1
    while logic:
        fast = input("Would you like the segmentation proccess to be in fast mode: (Y/N) ")
        if fast not in ('Y', 'y', 'N', 'n'):
             print("Invalid input. Please enter Y/y or N/n.")
        else:
            logic = 0
    if fast in ('Y','y'):
        fast = 1
    else:
        fast = 0
    #Step 8: run the inference
    # Get the list of valid files to process
    valid_files = [
        filename for filename in os.listdir(folder_path)
        if not filename.startswith(".") and filename.endswith(".nii.gz")
    ]

    # If processing a single file, filter the list
    if mutliple_logic in ('N', 'n'):
        valid_files = [filename for filename in valid_files if filename == input_file]

    if not valid_files:
        print("No valid files found to process.")
        sys.exit(1)

    print("--------------------------------------------------------------")

    
    # Iterate over files with a single progress bar
    with tqdm(total=len(valid_files), desc="Processing Files", unit="file", leave=True) as pbar:
        for filename in valid_files:
            # Construct the full file path
            file_path = os.path.join(folder_path, filename)

            # Check if it's a file
            if os.path.isfile(file_path):
                input_path = str(file_path)
                output_path_batch = os.path.join(output_path, filename)

                # Use tqdm.write to indicate which file is being processed
                tqdm.write(f"Processing file: {file_path}")

                try:
                    # Call totalsegmentator
                    totalsegmentator(
                        input_path,
                        output_path_batch,
                        quiet=quiet,
                        device=str(device),
                        roi_subset=roi_subset,
                        fast=fast,
                        task = task
                    )
                except Exception as e:
                    # Log errors without interfering with the progress bar
                    tqdm.write(f"Error processing {file_path}: {e}")
            # Update the progress bar
            pbar.update(1)

    print("--------------------------------------------------------------")
