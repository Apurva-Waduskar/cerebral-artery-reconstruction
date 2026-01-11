import nibabel as nib
import numpy as np
from skimage.measure import marching_cubes
import trimesh
from pathlib import Path

mask_path = "03_masks/arteries_clean_continuous.nii.gz"
output_dir = Path("04_mesh")
output_dir.mkdir(exist_ok=True)

img = nib.load(mask_path)
mask = img.get_fdata()

if mask.max() == 0:
    raise RuntimeError("Mask is empty")

# Marching cubes
verts, faces, normals, _ = marching_cubes(mask, level=0.5)

# Convert to mesh
mesh = trimesh.Trimesh(vertices=verts, faces=faces, vertex_normals=normals)

# Save
mesh.export(output_dir / "cerebral_arteries.stl")

print("3D artery mesh saved")
