from metadata.MetaDataAPI import get_full_file_name,  get_column_list
from pathlib import Path
from loguru import logger

def df_pd_csv_code(df_name, file_str):
    df_template ="""
{} = pd.read_csv('{}', header=0)
"""
    return df_template.format(df_name, file_str)

def gen_imports_code():
    return """
import pandas as pd
import matplotlib as plt
import streamlit as st
"""

def genDF_code(df_name):
    ### Get Filename for the dataframe
    file_str = get_full_file_name(df_name)
    if file_str == None:
        logger.error(f"#File# Not found in the config for the Dataframe = {df_name}")
        return None
    logger.debug(f"file_str found = {file_str}")

    ### Get Column List  for the dataframe
    columns = get_column_list(df_name)
    if columns == None:
        logger.error(f"#Columns# Not found for the Dataframe = {df_name}")
        return None
    logger.debug(f"columns found = {columns}")

    ### Check if file exists
    file_path = Path(file_str)
    if not file_path.exists():
        logger.error(f"{file_path} does NOT exist.")
    logger.debug(f"File exists  = {file_path}")

    df_code = df_pd_csv_code(df_name, file_str)
    logger.debug(f"code generated for {df_name}: {df_code}")
    return df_code

def gen_human_feedback_code() -> str:
    code_hf = """
def get_human_feedback():
    st.subheader("Rate Your Experience")

    # Create two columns
    col1, col2 = st.columns([2,3])  # two columns with 50% each

    # Slider to receive human feedback score from 1 to 10 about the generated graphs.
    #user_score = 1
    with col1:
        for i in range(1):
            st.write("")
        user_score = st.slider("Rate your experience for the generated graphs: 1-Worst,  10-Best", min_value=1, max_value=10, value=7)
        st.write("**Rated:**", user_score)

    # Display the selected score
    with col2:
        feedback_txt = st.text_area("Feedback", value="", height=100)
        if st.button("Submit"):
            rating_msg = "Glad you had good experience!"
            if (user_score in range(1,4)):
                rating_msg = "Sorry for your bad experience. Will review your feedback to improve the App!"
            elif (user_score in range(8,11)):
                rating_msg = "So glad for your wonderful experience!"
            # Use markdown to display with larger font size
            st.markdown(f"<p style='font-size:24px;'>Thank you for your feedback with the Score = {user_score}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:24px;'>{rating_msg}</p>", unsafe_allow_html=True)

get_human_feedback()
"""
    return code_hf

