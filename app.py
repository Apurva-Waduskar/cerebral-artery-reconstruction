import nest_asyncio
nest_asyncio.apply()

import streamlit as st
import zipfile
import tempfile
from pathlib import Path
import pyvista as pv

from pipeline import run_pipeline


# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(
    page_title="3D Cerebral Artery Reconstruction",
    layout="wide"
)

st.title("3D Cerebral Artery Reconstruction from TOF-MRA")


# -----------------------------
# Helper: Render PyVista in Streamlit
# -----------------------------
def show_pyvista(plotter: pv.Plotter, html_path: Path):
    """
    Export PyVista scene to HTML and embed in Streamlit
    """
    plotter.export_html(str(html_path))

    with open(html_path, "r", encoding="utf-8") as f:
        st.components.v1.html(
            f.read(),
            height=650,
            scrolling=True
        )


# -----------------------------
# File uploader
# -----------------------------
uploaded_zip = st.file_uploader(
    "Upload ZIP file containing TOF-MRA DICOM (.dcm) files",
    type=["zip"]
)


# -----------------------------
# Main pipeline execution
# -----------------------------
if uploaded_zip is not None:

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        # Where ZIP will be extracted
        raw_dicom_dir = tmp / "00_raw_dicom"
        raw_dicom_dir.mkdir(parents=True, exist_ok=True)

        # Extract ZIP
        try:
            with zipfile.ZipFile(uploaded_zip, "r") as z:
                z.extractall(raw_dicom_dir)
            st.success("DICOM files extracted")
        except Exception as e:
            st.error("Failed to extract ZIP file")
            st.exception(e)
            st.stop()

        # Run pipeline
        with st.spinner("Running full artery reconstruction pipeline..."):
            try:
                stl_path = run_pipeline(tmp)
            except Exception as e:
                st.error("Pipeline execution failed")
                st.exception(e)
                st.stop()

        st.success("3D artery reconstruction complete")

        # -----------------------------
        # Load and visualize STL
        # -----------------------------
        try:
            mesh = pv.read(str(stl_path))
        except Exception as e:
            st.error("Failed to load generated STL file")
            st.exception(e)
            st.stop()

        plotter = pv.Plotter(off_screen=True)
        plotter.set_background("black")
        plotter.add_mesh(
            mesh,
            color="white",
            smooth_shading=True
        )
        plotter.add_axes()

        html_file = tmp / "arteries.html"
        show_pyvista(plotter, html_file)

        # -----------------------------
        # Download STL
        # -----------------------------
        with open(stl_path, "rb") as f:
            st.download_button(
                label="Download 3D Artery STL",
                data=f,
                file_name="cerebral_arteries.stl",
                mime="application/octet-stream"
            )
