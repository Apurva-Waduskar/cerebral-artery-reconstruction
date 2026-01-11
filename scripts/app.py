import nest_asyncio
nest_asyncio.apply()

import streamlit as st
import zipfile
import tempfile
from pathlib import Path
import pyvista as pv

from pipeline import run_pipeline

st.set_page_config(layout="wide")
st.title("3D Cerebral Artery Reconstruction from TOF-MRA")


def show_pyvista(plotter, html_path):
    plotter.export_html(str(html_path))
    with open(html_path, "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=650, scrolling=True)


uploaded_zip = st.file_uploader(
    "Upload ZIP file containing TOF-MRA DICOM (.dcm) files",
    type=["zip"]
)

if uploaded_zip:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        raw = tmp / "00_raw_dicom"
        raw.mkdir()

        with zipfile.ZipFile(uploaded_zip, "r") as z:
            z.extractall(raw)

        st.success("DICOM files extracted")

        with st.spinner("Running full artery reconstruction pipeline..."):
            stl_path = run_pipeline(tmp)

        st.success("3D artery reconstruction complete")

        mesh = pv.read(str(stl_path))

        plotter = pv.Plotter(off_screen=True)
        plotter.set_background("black")
        plotter.add_mesh(mesh, color="white", smooth_shading=True)
        plotter.add_axes()

        html_file = tmp / "arteries.html"
        show_pyvista(plotter, html_file)

        with open(stl_path, "rb") as f:
            st.download_button(
                "Download STL",
                f,
                file_name="cerebral_arteries.stl"
            )
