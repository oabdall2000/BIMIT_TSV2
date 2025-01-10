import os
import shutil
import uuid
import nibabel as nib
import SimpleITK as sitk
import dicom2nifti


def reorient_to_standard(input_path, output_path, orientation="RAI"):
    """Reorient a NIfTI file to a standard orientation."""
    try:
        image = sitk.ReadImage(input_path)
        reoriented_image = sitk.DICOMOrient(image, orientation)
        sitk.WriteImage(reoriented_image, output_path)
        print(f"Reoriented to {orientation}: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Error during reorientation of {input_path}: {e}")


def process_dicom_folder(input_folder, output_folder, unique_prefix):
    """Convert a DICOM folder to NIfTI and save the output into a single directory."""
    temp_output_dir = os.path.join(output_folder, f"temp_{unique_prefix}")
    os.makedirs(temp_output_dir, exist_ok=True)

    try:
        # Step 1: Convert DICOM to NIfTI
        dicom2nifti.convert_directory(input_folder, temp_output_dir)
        print(f"Converted DICOM from {input_folder} to NIfTI.")

        # Find the output NIfTI file
        nifti_file = next(
            (f for f in os.listdir(temp_output_dir) if f.endswith(".nii.gz")), None
        )
        if nifti_file is None:
            raise ValueError(f"No NIfTI file found in the temporary output directory: {temp_output_dir}")

        nifti_path = os.path.join(temp_output_dir, nifti_file)

        # Final output path
        final_output_name = f"{unique_prefix}.nii.gz"
        final_output_path = os.path.join(output_folder, final_output_name)

        # Step 2: Reorient to standard directly into the final output
        reorient_to_standard(nifti_path, final_output_path)

        print(f"Final NIfTI file saved at: {final_output_path}")
    except Exception as e:
        raise RuntimeError(f"Error processing folder {input_folder}: {e}")
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir)
            print(f"Cleaned up temporary directory: {temp_output_dir}")


def process_all_dicom_folders(input_path, output_path):
    """Recursively process all DICOM folders."""
    for root, dirs, _ in os.walk(input_path):
        for folder in dirs:
            input_folder = os.path.join(root, folder)
            unique_prefix = f"{folder.replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            print(f"Processing folder: {input_folder}")
            try:
                process_dicom_folder(input_folder, output_path, unique_prefix)
            except Exception as e:
                print(f"Error processing folder {input_folder}: {e}")


if __name__ == "__main__":
    # Get input and output paths
    input_path = input("Copy path for the input (file or parent folder): ")
    output_path = input("Copy path for the output folder for consolidated .nii.gz files: ")

    # Ensure the output folder exists
    os.makedirs(output_path, exist_ok=True)

    if os.path.isdir(input_path):
        print("Processing input directory.")
        process_all_dicom_folders(input_path, output_path)
    else:
        print("Invalid input path. Please provide a valid folder containing DICOM files.")

    print("Conversion process completed.")
