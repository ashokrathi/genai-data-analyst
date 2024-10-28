import streamlit as st

def show_side_bar():
    # Sidebar for user input
    st.sidebar.header("LLM Options")

    # Multiple checkboxes
    a1 = st.sidebar.checkbox("Show Full LLM Prompt with Context", value=st.session_state['llm_prompt_option'])
    st.session_state['llm_prompt_option'] = a1

    a2 = st.sidebar.checkbox("Show LLM Response", value=st.session_state['llm_response_option'])
    st.session_state['llm_response_option'] = a2

    a3 = st.sidebar.checkbox("Show LLM Generated Code", value=st.session_state['llm_code_option'])
    st.session_state['llm_code_option'] = a3
