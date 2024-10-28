import streamlit as st
from app_config import DATA_DIR
from metadata.MetaDataAPI import force_reset_metadata
import os

####################### Display Data Directories
def show_dirs():
    # Function to list directories
    def list_dirs(path='.'):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    st.sidebar.subheader("Data Sets")

    # Dropdown to select a directory
    base_path = DATA_DIR
    directories = list_dirs(base_path)
    selected_dir = st.sidebar.selectbox("Select a directory", directories)
    #st.write(f"You selected: {os.path.join(base_path, selected_dir)}")
    if selected_dir:
        selected_path = os.path.join(base_path, selected_dir)
        st.sidebar.write(f"Selected directory: *{selected_path}*")
        st.sidebar.write()
        force_reset_metadata(selected_path)
