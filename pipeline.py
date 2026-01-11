from pathlib import Path
import subprocess
import sys


def find_tof_folder(root_dir: Path) -> Path:
    candidates = []

    for p in root_dir.rglob("*"):
        if p.is_dir():
            name = p.name.lower()
            if "tof_fl3d_tra_p2_multi-slab" in name and "mip" not in name:
                if list(p.glob("*.dcm")):
                    candidates.append(p)

    if not candidates:
        raise FileNotFoundError(
            "No 'tof_fl3d_tra_p2_multi-slab' folder with DICOMs found"
        )

    candidates.sort(
        key=lambda x: len(list(x.glob("*.dcm"))),
        reverse=True
    )
    return candidates[0]


def run_pipeline(tmpdir: Path) -> Path:
    raw_root = tmpdir / "00_raw_dicom"
    nifti_dir = tmpdir / "01_nifti"
    vessel_dir = tmpdir / "02_vesselness"
    mask_dir = tmpdir / "03_masks"
    mesh_dir = tmpdir / "04_mesh"

    for d in [nifti_dir, vessel_dir, mask_dir, mesh_dir]:
        d.mkdir(exist_ok=True)

    tof_dicom_dir = find_tof_folder(raw_root)

    PY = sys.executable  # 🔑 THIS IS THE FIX

    def run(cmd):
        subprocess.run(
            cmd,
            check=True,
            cwd=tmpdir
        )

    run([
        PY, "scripts/dicom_to_nifti.py",
        "-i", str(tof_dicom_dir),
        "-o", str(nifti_dir / "brain_TOF.nii.gz")
    ])

    run([PY, "scripts/vesselness.py"])
    run([PY, "scripts/threshold_and_clean.py"])
    run([PY, "scripts/remove_discontinuous_vessels.py"])
    run([PY, "scripts/mesh_from_mask.py"])

    stl_path = mesh_dir / "cerebral_arteries.stl"
    if not stl_path.exists():
        raise FileNotFoundError("STL file not generated")

    return stl_path
