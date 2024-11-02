###
# Open source Imports
###
import streamlit as st
from loguru import logger
from PIL import Image
import os

###
# Imports from the code-base
###
from components.speech2text import show_speaker
from components.directories import show_dirs
from app_config import usr_prompt_txt_key, MIC_IMAGE_FILE
from llm import prompt_langchain, prompt_openai
from utils.launch_python_proc import run_python_code
from utils.codegen import gen_human_feedback_code
from utils.dir_utils import create_temp_code_folder
from build_prompt import build_llm_prompt
from components.side_bar import show_side_bar
from vectorDB.pineconeDB import get_prompt_dataset_quality

##################################################################
# Main Driver
##################################################################
def main():
    logger.info("================ START OF Steamlit Application: VEDA  ================ ")

    markdown_divider_str = """
<hr style="border: 2px solid green; margin: 5px 0;">
"""

    # set absolute current path
    st.session_state['app_path'] = os.getcwd()

    # set wide layout
    st.set_page_config(layout="wide")

    ###
    # Display Title and Logo image
    ###
    col1, col2 = st.columns([1, 1])  # Adjust the width ratios if needed
    with col1:
        st.title("Voice-Enhanced Data Analyst")
        st.write("")
    with col2:
        mic_image = Image.open(MIC_IMAGE_FILE)  # Replace 'mic_icon.png' with the path to your microphone image
        st.image(mic_image, caption='', use_column_width=False)
    st.write("")

    ###
    # Initialize session states
    ###
    if usr_prompt_txt_key not in st.session_state:
        st.session_state[usr_prompt_txt_key] = ""
    if 'llm_prompt_option' not in st.session_state:
        st.session_state['llm_prompt_option'] = True
    if 'llm_response_option' not in st.session_state:
        st.session_state['llm_response_option'] = True
    if 'llm_code_option' not in st.session_state:
        st.session_state['llm_code_option'] = True
    if 'dataset_name' not in st.session_state:
        st.session_state['dataset_name'] = ""
    if 'pinecone_instance' not in st.session_state:
        st.session_state['pinecone_instance'] = ""

    ###
    # Display Sidebar
    ###
    show_side_bar()

    logger.info(f"LLM Prompt Status: {st.session_state['llm_prompt_option']}")
    logger.info(f"LLM Response Status: {st.session_state['llm_response_option']}")
    logger.info(f"LLM Code Status: {st.session_state['llm_code_option']}")

    ###   
    # Display directories list
    ###   
    show_dirs()

    ###
    # Display User Prompt section
    ###
    st.subheader("User Prompt", help="User enters prompt here.")
    st.markdown(markdown_divider_str, unsafe_allow_html=True) # Custom divider with reduced spacing

    ###   
    # Display speaker for voice prompt
    ###   
    st.write("")
    show_speaker()
    st.write("")

    ###   
    # Display Prompt Box and Submit button
    ###   
    col_submit_1, col_submit_2, col_dummy = st.columns([70,10,20])
    with col_submit_1:
        prompt_txt = st.text_area("**Enter Prompt Here:**", value=st.session_state[usr_prompt_txt_key], height=100)
    with col_submit_2:
        for i in range(6):
            st.write("")
        submit = st.button("Submit")
    if "submit_state" not in st.session_state:
        st.session_state.submit_state = False

    ###   
    # Slide bar to show progress of Prompt building, LLM response, parsing etc.
    # TBD: Not working well yet.
    ###   
    with st.container():
            slider_placeholder = st.empty()
            slider_placeholder.slider("Progress", min_value=0, max_value=100, value=0, disabled=True)
            slider_placeholder.progress = "hello"

    ##################################################################
    # Actions when Prompt is submitted.
    #   1. Select appropriate dataset
    #   2. Similarity check to identify appropriate dataset matching
    #      the prompt using PineconeDB as vectorDB.
    #   3. Build Full Prompt with the context about datasets
    #   4. Send Full Prompt to LLM
    #   5. Parse the LLM Response for Matplotlib "Code"
    #   6. Edit the Code - Insert code to open data files
    #      and create required Dataframes.
    #   7. Launch separate Streamlit process to display graphs/charts
    #   8. Launched process also seeks Human Feedback.
    ##################################################################
    if submit or st.session_state.submit_state:
        ###
        # Select appropriate dataset for graphs/charts
        ###
        selected_dataset = st.session_state['dataset_name']
        if selected_dataset:
            ###
            # Run similarity check between Prompt and the dataset
            ###
            metadata_score = get_prompt_dataset_quality(prompt_txt, selected_dataset)           # Use Pinecone DB for quality of the prompt.
            if selected_dataset.casefold() == metadata_score['dataset'].casefold():
                st.write(f"**Similarity Check: {metadata_score['dataset']}/{metadata_score['score']}**")
            else:
                col1, col2 = st.columns([45,55])
                with col1:
                    warn_msg = f"**Dataset Similarity Check FAILED:** Possibly incorrect dataset selected. Recommended dataset = **{metadata_score['dataset']}**, Similarity Score = {metadata_score['score']}"
                    st.markdown(f"<span style='color:red;'>{warn_msg}</span>", unsafe_allow_html=True)
                with col2:
                    pass

        st.session_state.submit_state = True
        create_temp_code_folder()

        ###
        # Build complete prompt with context
        ###
        llm_prompt = build_llm_prompt(prompt_txt)
        slider_placeholder.slider("Progress", min_value=0, max_value=100, value=10, disabled=True)
        slider_placeholder.progress = "hello2"
        st.subheader("Full Context", help="**Full Context with Prompt sent to LLM.**")
        if st.session_state['llm_prompt_option']:
            #st.write("Expander for LLM Prompt with Context")
            with st.expander("**LLM Prompt with Context (Click to expand):**"):
                # Inside the expander, can add text or any other content
                st.write(llm_prompt)

        slider_placeholder.slider("Progress", min_value=0, max_value=100, value=30, disabled=True)
        #pb.set_progress(30, "LLM Prompt Context Generated  Sending to LLM")

        ###
        # Send Prompt to LLM
        # Receive and parse response, 
        # Generate code lines
        ###
        code_lines = prompt_openai(llm_prompt)     # List[ line_str1, line_str2, ...].
        slider_placeholder.slider("Progress", min_value=0, max_value=100, value=80, disabled=True)
        #pb.set_progress(80, "LLM Prompt Context Generated  Sent to LLM  Response Received")

        ###
        # Add Human feedback related code
        ###
        # append code for the human feedback.
        feedback_code_str = gen_human_feedback_code()
        code_lines.append(feedback_code_str)

        ###
        # Display response and generanted code in different
        # expandable text boxes.
        ###
        if st.session_state['llm_response_option']:
            with st.expander("**LLM Response (Click to expand):**"):
                # Inside the expander, can add text or any other content
                for line in code_lines:
                    x = '\n'.join([l for l in line.splitlines()])
                    st.write(f"{x}\n")
        #pb.set_progress(100, "LLM Prompt+Context Generated  Sent to LLM  Response Received  Code Generated")
        slider_placeholder.slider("Progress", min_value=0, max_value=100, value=100, disabled=True)

        ###
        # Execute generanted Streamlit code in a separate process.
        ###
        run_python_code(code_lines, prompt_txt)
        #pb.set_progress(100, "LLM Prompt+Context=== Generated  Sent to LLM  Response Received  Code Generated  Code Executed...")

    # Process data and display chart if input is provided
    #if user_input:
    #    processed_data = process_data(user_input)
    #    show_chart(processed_data)

if __name__ == "__main__":
    main()
