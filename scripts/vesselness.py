import nibabel as nib
import numpy as np
from skimage.filters import frangi
from pathlib import Path

# Paths
input_nifti = "01_nifti/brain_TOF.nii.gz"
output_dir = Path("02_vesselness")
output_dir.mkdir(exist_ok=True)

# Load TOF
img = nib.load(input_nifti)
data = img.get_fdata()

# Normalize
data = (data - data.min()) / (data.max() - data.min())

# Frangi vesselness
vesselness = frangi(
    data,
    sigmas=[0.5, 1, 1.5, 2, 3],
    alpha=0.3,
    beta=0.3,
    gamma=5,
    black_ridges=False
)


# Save
out_img = nib.Nifti1Image(vesselness.astype(np.float32), img.affine)
nib.save(out_img, output_dir / "vesselness.nii.gz")

print("Vesselness saved:", out_img.shape)
