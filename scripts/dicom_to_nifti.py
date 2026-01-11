from pathlib import Path
import numpy as np
import nibabel as nib
import pydicom

def dicom_to_nifti(dicom_root, output_nifti):
    dicom_root = Path(dicom_root)

    # Recursively find all DICOM files
    dicom_files = list(dicom_root.rglob("*.dcm"))

    if len(dicom_files) == 0:
        raise RuntimeError("No DICOM files found in uploaded folder")

    slices = []
    for f in dicom_files:
        try:
            ds = pydicom.dcmread(f, stop_before_pixels=False)
            if hasattr(ds, "PixelData"):
                slices.append(ds)
        except Exception:
            continue

    if len(slices) == 0:
        raise RuntimeError("No readable DICOM slices with pixel data")

    # Reference shape
    ref_shape = slices[0].pixel_array.shape
    valid_slices = [s for s in slices if s.pixel_array.shape == ref_shape]

    if len(valid_slices) < 10:
        raise RuntimeError("Too few valid DICOM slices")

    print(f"Total DICOMs found: {len(dicom_files)}")
    print(f"Valid image slices used: {len(valid_slices)}")
    print(f"Image shape: {ref_shape}")

    # Sort by Z position
    def zpos(ds):
        return float(ds.ImagePositionPatient[2])

    valid_slices.sort(key=zpos)

    volume = np.stack([s.pixel_array for s in valid_slices], axis=-1)

    px_spacing = float(valid_slices[0].PixelSpacing[0])
    slice_spacing = abs(zpos(valid_slices[1]) - zpos(valid_slices[0]))

    affine = np.diag([px_spacing, px_spacing, slice_spacing, 1.0])

    nifti = nib.Nifti1Image(volume.astype(np.float32), affine)
    nib.save(nifti, output_nifti)

    print(f"Saved NIfTI: {output_nifti}")
    print(f"Final volume shape: {volume.shape}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    dicom_to_nifti(args.input, args.output)
