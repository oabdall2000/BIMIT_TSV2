import subprocess
import sys
import os
import warnings
import torch

# -----------------------
# Dependency Installation
# -----------------------
def install_dependencies():
    """Install required dependencies."""
    required_packages = [
        "torch",
        "totalsegmentator",
        "fury",
        "pyradiomics",
        "dicom2nifti",
        "tqdm",
        "pandas"
    ]

    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
        except subprocess.CalledProcessError:
            print(f"Failed to install package: {package}")
            sys.exit(1)


# -----------------------
# GPU Check and Enforcement
# -----------------------
def select_device():
    """Ensure GPU is used if available; fallback to CPU otherwise."""
    if torch.cuda.is_available():
        print("✅ GPU detected! Using GPU for segmentation.")
        return "gpu"
    else:
        print("❌ No GPU detected. Falling back to CPU. This might be slower.")
        return "cpu"


# -----------------------
# User Inputs
# -----------------------
def get_valid_path(prompt):
    """Prompt user for a valid file or folder path."""
    while True:
        path = input(prompt)
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
        else:
            return path


def get_user_input(prompt, valid_options):
    """Prompt user for valid input."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_options:
            return choice
        print(f"Invalid input. Please choose from: {', '.join(valid_options)}")


# -----------------------
# Main Script Logic
# -----------------------
if __name__ == "__main__":
    # Step 1: Install dependencies
    install_dependencies()

    warnings.filterwarnings(
        "ignore",
        message="You are using `torch.load` with `weights_only=False`",
        category=FutureWarning
    )

    print("------------------------------------------------------------")
    print("All dependencies (torch and totalsegmentator) are installed!")
    print("------------------------------------------------------------")

    try:
        import pandas as pd
        from tqdm import tqdm
        from totalsegmentator.python_api import totalsegmentator

        # Step 2: Get User Inputs
        folder_path = get_valid_path("Copy the path to the folder or file to segment: ")
        output_path = get_valid_path("Copy the path to the folder you want the outputs in: ")

        # Force GPU usage if available
        device = select_device()

        image_mod = get_user_input("Is the input file MR or CT? (MR/CT): ", ["mr", "ct"])
        task = "total_mr" if image_mod == "mr" else "total"

        special_task = get_user_input("Are you performing a special task? (Y/N): ", ["y", "n"])
        roi_subset = None
        if special_task == 'y':
            print("Available tasks:\nlung_vessels, body, cerebral_bleed, hip_implant, coronary_arteries")
            print("pleural_pericard_effusion, head_glands_cavities, head_muscles")
            task = input("Enter the name of the special task: ").strip()
        else:
            subset_choice = get_user_input("Are you performing segmentation for all classes? (Y/N): ", ["y", "n"])
            if subset_choice == 'n':
                roi_subset = []
                while True:
                    class_subset = input("What class(es) would you like to segment: ").strip()
                    roi_subset.append(class_subset)
                    more_classes = get_user_input("Any other classes? (Y/N): ", ["y", "n"])
                    if more_classes == 'n':
                        break

        adv_logic = get_user_input("Would you like to add advanced settings? (Y/N): ", ["y", "n"])
        ml = radiomics = statistics = 0
        if adv_logic == 'y':
            ml = 0
            radiomics = 1
            statistics = 1

        quiet = get_user_input("Would you like the segmentation process to be quiet? (Y/N): ", ["y", "n"])
        quiet = 1 if quiet == 'y' else 0

        fast = get_user_input("Would you like the segmentation process to be in fast mode? (Y/N): ", ["y", "n"])
        fast = 1 if fast == 'y' else 0

        # Step 3: Process Files
        if folder_path.endswith(".nii.gz"):
            valid_files = [folder_path]
            folder_logic = True
        else:
            valid_files = [
                os.path.join(folder_path, f) for f in os.listdir(folder_path)
                if f.endswith(".nii.gz") and not f.startswith(".")
            ]
            folder_logic = False

        if not valid_files:
            print("No valid files found to process.")
            sys.exit(1)

        print("--------------------------------------------------------------")

        with tqdm(total=len(valid_files), desc="Processing Files", unit="file", leave=True) as pbar:
            for file_path in valid_files:
                filename = os.path.basename(file_path)
                output_path_batch = os.path.join(output_path, filename)

                tqdm.write(f"Processing file: {file_path}")

                try:
                    totalsegmentator(
                        file_path,
                        output_path_batch,
                        quiet=quiet,
                        device=device,
                        roi_subset=roi_subset,
                        fast=fast,
                        task=task,
                        ml=ml,
                        statistics=statistics,
                        radiomics=radiomics,
                        preview=0
                    )
                except Exception as e:
                    tqdm.write(f"Error processing {file_path}: {e}")

                pbar.update(1)

        print("--------------------------------------------------------------")
        print("✅ Segmentation process completed successfully!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
