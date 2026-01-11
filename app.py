import streamlit as st
import zipfile
import tempfile
from pathlib import Path
import numpy as np
import trimesh
import plotly.graph_objects as go

from pipeline import run_pipeline


# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(
    page_title="3D Cerebral Artery Reconstruction",
    layout="wide"
)

st.title("3D Cerebral Artery Reconstruction from TOF-MRA")


# -----------------------------
# Helper: Plotly STL viewer
# -----------------------------
def plot_stl_plotly(stl_path: Path):
    mesh = trimesh.load_mesh(stl_path)

    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)

    fig = go.Figure(
        data=[
            go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=faces[:, 0],
                j=faces[:, 1],
                k=faces[:, 2],
                color="lightgray",
                opacity=1.0
            )
        ]
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Upload ZIP
# -----------------------------
uploaded_zip = st.file_uploader(
    "Upload ZIP file containing TOF-MRA DICOM (.dcm) files",
    type=["zip"]
)


# -----------------------------
# Run pipeline
# -----------------------------
if uploaded_zip is not None:

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        raw_dir = tmp / "00_raw_dicom"
        raw_dir.mkdir(parents=True, exist_ok=True)

        # Extract ZIP
        with zipfile.ZipFile(uploaded_zip, "r") as z:
            z.extractall(raw_dir)

        st.success("DICOM files extracted")

        # Run reconstruction
        with st.spinner("Running artery reconstruction pipeline..."):
            try:
                stl_path = run_pipeline(tmp)
            except Exception as e:
                st.error("Pipeline failed")
                st.exception(e)
                st.stop()

        st.success("3D artery reconstruction complete")

        # -----------------------------
        # Plot STL (Cloud-safe)
        # -----------------------------
        plot_stl_plotly(stl_path)

        # -----------------------------
        # Download STL
        # -----------------------------
        with open(stl_path, "rb") as f:
            st.download_button(
                "Download 3D Artery STL",
                f,
                file_name="cerebral_arteries.stl",
                mime="application/octet-stream"
            )
