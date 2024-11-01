import streamlit as st
import subprocess
from app_config import PYTHON_PROG_DIR
from datetime import datetime
from metadata.MetaDataAPI import get_current_dataset_name
import sys
import os

def python_program(file):
    subprocess.run(["python", file]) or subprocess.run([f"{sys.executable}", "script.py"])

def streamlit_program(file):
    command = ["streamlit", "run", file]
    subprocess.run(command)

file_id = 0

def run_python_code(codelines, prompt_txt):
    proc_id = os.getpid()
    global file_id
    file_id += 1
    temp_dir = st.session_state['temp_code_dir']
    temp_file = f"{temp_dir}/temp_{proc_id}_{file_id}.py"
    with open(temp_file, "w") as f:
        # Write first header info - particularly streamlit wide page layout
        f.write("""
import streamlit as st
# set wide layout
st.set_page_config(layout="wide")
""")

        # Get only the dataset name (not path)
        dataset_name = get_current_dataset_name()

        # Get timestamp
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d-%H:%M:%S")

        # Write user prompt as header
        only_temp_file_part = temp_file.split("/")[-1]
        meta_info = """
col_1, col_2 = st.columns([70,30])
with col_1:
    st.header("Prompt: {}")
with col_2:
    st.write("")
    st.write("")
    st.write("{} / {} / {}")
""".format(prompt_txt.replace("\n",""), dataset_name, only_temp_file_part, formatted_time)

        f.write(meta_info)

        # Write python code to the file 
        for line in codelines:
            f.write(f"{line}\n")

    #python_program(temp_file)
    streamlit_program(temp_file)

