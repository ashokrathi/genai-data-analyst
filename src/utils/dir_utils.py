from app_config import PYTHON_PROG_DIR
from pathlib import Path
from loguru import logger
import streamlit as st
from datetime import datetime

def create_temp_code_folder():
    # Create temporary sub-folder with timestamp
    app_path = st.session_state['app_path']
    logger.debug("app_path:"+app_path)

    # Get timestamp
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d-%H%M%S")

    # Get absolute path of 'prog' dir
    prog_dir = PYTHON_PROG_DIR
    if (PYTHON_PROG_DIR[0] != "/"):
        prog_dir = app_path + "/" + PYTHON_PROG_DIR

    temp_code_dir = prog_dir + "/" + "code-" + formatted_time
    directory_path = Path(temp_code_dir)
    if not directory_path.is_dir():
        directory_path.mkdir(parents=True, exist_ok=True)
        st.session_state['temp_code_dir'] = temp_code_dir
        logger.info(f"Temporary Code Folder created: {temp_code_dir}")

    return temp_code_dir


