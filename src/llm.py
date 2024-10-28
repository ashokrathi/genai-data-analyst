import streamlit as st
import openai
from langchain_openai import OpenAI
from langchain.output_parsers import XMLOutputParser
from langchain_core.prompts import PromptTemplate
from app_config import OPENAI_API_KEY
from utils.parseXMLutil import parseXML
from loguru import logger

def prompt_langchain(prompt_str):
    # chain = prompt | model | parser
    #parser = XMLOutputParser()
    model = OpenAI(api_key = OPENAI_API_KEY)
    chain = model
    output = chain.invoke(prompt_str)
    if output:
        length = len(output)
        with st.expander(f"**Raw LLM Response, Size={length} (Click to expand):**"):
            # Inside the expander, can add text or any other content
            st.write(output)
    st.write(output)

def prompt_openai(prompt_str):
    model="gpt-4o-mini"
    client = openai.OpenAI(api_key = OPENAI_API_KEY)
    messages = [{"role": "user", "content": prompt_str}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    output = response.choices[0].message.content
    logger.debug("================ Response:================ ")
    logger.debug(output)
    temp_dir = st.session_state['temp_code_dir']
    llm_resp_file = temp_dir + "/" + "llm_response.txt"
    with open(llm_resp_file, "w") as f:
        # Write some text to the file
        f.write(f"{output}\n")
    if output:
        length = len(output)
        st.subheader("LLM Response", help="**Code Generated in LLM Response.**")
        if st.session_state['llm_response_option']:
            with st.expander(f"**Raw LLM Response, Size={length} (Click to expand):**"):
                st.write(f"{output}\n")
        code_blocks = parseXML(output)          # code_blocks is a List[str1, str2,..]
        if st.session_state['llm_code_option']:
            with st.expander(f"**Generated Code Block (Click to expand):**"):
                st.write(code_blocks)
        return code_blocks
    return output
