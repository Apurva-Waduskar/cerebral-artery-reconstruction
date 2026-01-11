import nibabel as nib
import numpy as np
from skimage.morphology import remove_small_objects
from pathlib import Path

input_vessel = "02_vesselness/vesselness.nii.gz"
output_dir = Path("03_masks")
output_dir.mkdir(exist_ok=True)

img = nib.load(input_vessel)
data = img.get_fdata()

print("Vesselness range:", data.min(), data.max())

# Threshold tuned to TOF vesselness scale
mask = data > 1e-05   # IMPORTANT

# Gentle cleanup
mask = remove_small_objects(mask, min_size=100)

out_img = nib.Nifti1Image(mask.astype(np.uint8), img.affine)
nib.save(out_img, output_dir / "arteries_mask.nii.gz")

print("Clean artery mask saved")
