import os
import dicom2nifti

# Get input and output paths
input_path = input("Copy path for the input (file or parent folder): ")
output_path = input("Copy path for the output (file or parent folder): ")

# Check if the input path is a directory
if os.path.isdir(input_path):
    # Check if it's a parent folder with multiple subdirectories
    if any(os.path.isdir(os.path.join(input_path, folder)) for folder in os.listdir(input_path)):
        print("Detected a parent folder containing multiple DICOM folders.")
        # Handle multiple subdirectories
        for folder in os.listdir(input_path):
            input_folder = os.path.join(input_path, folder)
            
            if os.path.isdir(input_folder):  # Ensure it is a directory
                print(f"Processing folder: {input_folder}")
                
                # Create corresponding output folder
                output_folder = os.path.join(output_path, folder)
                os.makedirs(output_folder, exist_ok=True)
                
                try:
                    # Convert the DICOM folder to NIfTI
                    dicom2nifti.convert_directory(input_folder, output_folder)
                    print(f"Successfully converted: {input_folder}")
                except Exception as e:
                    print(f"Error converting {input_folder}: {e}")
    else:
        print("Detected a single DICOM folder.")
        # Handle a single folder
        os.makedirs(output_path, exist_ok=True)
        try:
            dicom2nifti.convert_directory(input_path, output_path)
            print(f"Successfully converted: {input_path}")
        except Exception as e:
            print(f"Error converting {input_path}: {e}")
else:
    print("Invalid input path. Please provide a valid folder containing DICOM files.")

print("Conversion process completed.")
