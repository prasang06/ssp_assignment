"""Combined entry point for both assignment interfaces.

Local:  streamlit run streamlit_app.py
Deploy: set this file as the main module on Streamlit Community Cloud.
"""

import streamlit as st

st.set_page_config(page_title="Solid State Physics — Assignment 1",
                   page_icon="atom", layout="wide")

HOME = "home.py"

pages = [
    st.Page(HOME, title="Overview", icon=":material/home:", default=True),
    # url_path is required: both scripts are named app.py, so the pathname
    # Streamlit infers from the filename would collide
    st.Page("question_3/app.py", title="Q3 · Phonon dispersion",
            icon=":material/graphic_eq:", url_path="phonons"),
    st.Page("question_5/app.py", title="Q5 · Fermi–Dirac statistics",
            icon=":material/show_chart:", url_path="fermi-dirac"),
]

st.navigation(pages).run()
