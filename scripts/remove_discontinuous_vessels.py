import nibabel as nib
import numpy as np
from scipy.ndimage import label
from pathlib import Path

# Paths
input_mask = "03_masks/arteries_mask.nii.gz"
output_dir = Path("03_masks")
output_dir.mkdir(exist_ok=True)

img = nib.load(input_mask)
data = img.get_fdata().astype(bool)

# Label connected components
labeled, num = label(data)
print("Total connected components:", num)

# Count sizes
sizes = np.bincount(labeled.ravel())
sizes[0] = 0  # background

# Keep components larger than threshold
MIN_SIZE = 2000   # adjust if needed
keep = sizes >= MIN_SIZE

clean_mask = keep[labeled]

out_img = nib.Nifti1Image(clean_mask.astype(np.uint8), img.affine)
nib.save(out_img, output_dir / "arteries_clean_continuous.nii.gz")

print("Saved cleaned continuous artery mask")
