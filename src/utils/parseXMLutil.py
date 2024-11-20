from utils.parseXMLTags import ParseXMLTags
from utils.codegen import genDF_code, gen_imports_code
from loguru import logger
import streamlit as st
import re

####
# Define XML Tags:
#     <prompt_id> 
#     <sample_dataframe_init_code>
#     <list_merged_dataframes>
#     <dataframe_relationship_code>
#     <matplotlib_code>
####
TAG_prompt_id                   = 'prompt_id'
TAG_sample_dataframe_init_code  = 'sample_dataframe_init_code'
TAG_list_merged_dataframes      = 'list_merged_dataframes'
TAG_dataframe_relationship_code = 'dataframe_relationship_code'
TAG_matplotlib_code             = 'matplotlib_code'
xml_tags = [
    TAG_prompt_id,
#    TAG_sample_dataframe_init_code,
    TAG_list_merged_dataframes,
    TAG_dataframe_relationship_code,
    TAG_matplotlib_code
    ]

global_xml_indent_length_per_tag = 0

###
# Remove 4 leading spaces (for 2-level XML tree) from each line of the multi-line text
# OpenAI indents XML values by 2-spaces for each XML level. We have 2 levels, hence 4 spaces need to be removed.
###
def trim_leading_spaces_multiline(text):
    # Split the string into lines, remove 4 leading spaces from each line, and join them back
    len_spaces = global_xml_indent_length_per_tag * 2   # Indent for two tags
    spaces_to_trim = ' '*len_spaces
    logger.debug(f"Spaces To Trim:{spaces_to_trim}:{len_spaces}")
    return '\n'.join([line[len_spaces:] if line.startswith(spaces_to_trim) else line for line in text.splitlines()])

def parseXML(llm_response:str):
    ###
    # Trim undesired characters at start and end
    ###
    if (llm_response[0:6] == "```xml" and llm_response[-3:] == "```"):
        llm_response = llm_response[6:]      # trim first 6 characters
        llm_response = llm_response[:-3]     # trim last 3 characters
    
    ###
    # Replace XML special chars, so parser does not FAIL.
    ###
    llm_response = llm_response.replace('&', '(##XXREPLACE_ANDXX##)')
    llm_response = llm_response.replace('>=', '(##XXREPLACE_GEXX##)')
    llm_response = llm_response.replace(' <= ', '(##XXREPLACE_SP_GE_SPXX##)')
    llm_response = llm_response.replace(' \\', '(##XXREPLACE_SP_BACKSLASHXX##)')
    llm_response = llm_response.replace(' > ', '(##XXREPLACE_SP_GT_SPXX##)')
    llm_response = llm_response.replace(' < ', '(##XXREPLACE_SP_LT_SPXX##)')

    logger.debug("AFTER SPECIAL CHARACTER Replacment (&):" + llm_response)
        
    ###
    # determine leading spaces per tag after the <root> tag
    ###
    global global_xml_indent_length_per_tag
    global_xml_indent_length_per_tag = 0
    space_start = -1
    bTag = False
    for i in range(len(llm_response)):
        if (not bTag) and llm_response[i] == "<":         # start of xml tag, expected: <root>
            bTag = True
        if space_start == -1 and llm_response[i] == ' ':
            space_start = i
        if space_start > 0 and llm_response[i] != ' ':
            global_xml_indent_length_per_tag = i - space_start
            break

    logger.info("global_xml_indent_length_per_tag:", global_xml_indent_length_per_tag)

    logger.info(llm_response)

    xml_parser = ParseXMLTags(xml_tags)
    response_kv = xml_parser.parse_xml_response(llm_response)

    ###
    # Output code lines for each section from the LLM response.
    # TBD: Replace code for DFs etc. using keys
    ###
    output_code_blocks = []
    for k in response_kv.keys():
        #code_imports = ""
        #code_all_df = ""
        if k == TAG_list_merged_dataframes:
            code_imports = "###### Following Imports Inserted by Application after Inference ######\n" + gen_imports_code()
            code_all_df = ""
            logger.debug(f"Listed DFs To be Generated: {response_kv[k]}")
            # Keep only comma-separated accetable DF names (for now, also keep spaces)
            cleaned_df_names = re.sub(r'[^_,A-Za-z0-9\s]', '', response_kv[k])
            my_df_list = [item.strip() for item in cleaned_df_names.split(",")]
            logger.debug(f"Generate Code for this List: {my_df_list}")
            for df in my_df_list:
                logger.debug(f"Generate Code for: {df}")
                code_df = genDF_code(df)
                code_all_df += "\n" + f"###### Following Code Generated Dynamically Based on the inferred Dataframe = {df} ######\n" + code_df
            logger.debug(code_imports)
            logger.debug(code_all_df)
            output_code_blocks.append(code_imports)
            output_code_blocks.append(code_all_df)
        output_code_blocks.append(f"#======================== {k} ========================")
        code_block = trim_leading_spaces_multiline(response_kv[k])
        ###
        # Undo previous replacement - XML special chars, so parser does not FAIL.
        ###
        code_block = code_block.replace('(##XXREPLACE_ANDXX##)', '&')
        code_block = code_block.replace('(##XXREPLACE_GEXX##)', '>=')
        code_block = code_block.replace('(##XXREPLACE_SP_GE_SPXX##)', ' <= ')
        code_block = code_block.replace('(##XXREPLACE_SP_BACKSLASHXX##)', ' \\')
        code_block = code_block.replace('(##XXREPLACE_SP_GT_SPXX##)', ' > ')
        code_block = code_block.replace('(##XXREPLACE_SP_LT_SPXX##)', ' < ')

        output_code_blocks.append(code_block)

    temp_dir = st.session_state['temp_code_dir']
    llm_python_code_text_file = temp_dir + "/" + "llm_python_code.txt.txt"
    with open(llm_python_code_text_file, "w") as f:
        # Write some text to the file
        for line in output_code_blocks:
            f.write(f"{line}\n")
    return output_code_blocks

def xml_main():
    xml_test_response1 = "```xml<root>    <prompt_id> PROMPT_ID = '123455' </prompt_id>    <sample_data>        SalesDF:        | agent_id | region_id | customer_id | sales_date | parts_id | parts_quantity | sales_amount |        |----------|-----------|--------------|-------------|----------|----------------|---------------|        | 1        | 1         | 101          | 2023-01-01  | 201      | 2              | 200           |        | 2        | 1         | 102          | 2023-01-02  | 202      | 1              | 150           |        | 3        | 2         | 103          | 2023-01-03  | 203      | 3              | 300           |        | 1        | 2         | 104          | 2023-01-04  | 204      | 1              | 100           |        | 2        | 3         | 105          | 2023-01-05  | 205      | 4              | 400           |        AgentsDF:        | agent_id | agent_name |        |----------|-------------|        | 1        | Alice       |        | 2        | Bob         |        | 3        | Charlie     |        RegionsDF:        | region_id | region_name |        |-----------|--------------|        | 1         | North        |        | 2         | South        |        | 3         | East         |        PartsDF:        | part_id | part_name |        |---------|-----------|        | 201     | Part A   |        | 202     | Part B   |        | 203     | Part C   |        | 204     | Part D   |        | 205     | Part E   |        CustomersDF:        | customer_id | customer_name |        |-------------|----------------|        | 101         | Customer 1     |        | 102         | Customer 2     |        | 103         | Customer 3     |        | 104         | Customer 4     |        | 105         | Customer 5     |    </sample_data>    <sample_dataframe_init_code>        import pandas as pd        SalesDF = pd.DataFrame({            'agent_id': [1, 2, 3, 1, 2],            'region_id': [1, 1, 2, 2, 3],            'customer_id': [101, 102, 103, 104, 105],            'sales_date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),            'parts_id': [201, 202, 203, 204, 205],            'parts_quantity': [2, 1, 3, 1, 4],            'sales_amount': [200, 150, 300, 100, 400]        })        AgentsDF = pd.DataFrame({            'agent_id': [1, 2, 3],            'agent_name': ['Alice', 'Bob', 'Charlie']        })        RegionsDF = pd.DataFrame({            'region_id': [1, 2, 3],            'region_name': ['North', 'South', 'East']        })        PartsDF = pd.DataFrame({            'part_id': [201, 202, 203, 204, 205],            'part_name': ['Part A', 'Part B', 'Part C', 'Part D', 'Part E']        })        CustomersDF = pd.DataFrame({            'customer_id': [101, 102, 103, 104, 105],            'customer_name': ['Customer 1', 'Customer 2', 'Customer 3', 'Customer 4', 'Customer 5']        })    </sample_dataframe_init_code>    <list_merged_dataframes>        SalesDF, AgentsDF, RegionsDF    </list_merged_dataframes>    <dataframe_relationship_code>        merged_df = SalesDF.merge(AgentsDF, on='agent_id').merge(RegionsDF, on='region_id')        total_sales_by_region = merged_df.groupby('region_name')['sales_amount'].sum().reset_index()    </dataframe_relationship_code>    <matplotlib_code>        import matplotlib.pyplot as plt        plt.figure(figsize=(10, 6))        plt.bar(total_sales_by_region['region_name'], total_sales_by_region['sales_amount'], color=['red', 'green', 'blue', 'pink', 'yellow'])        plt.title('Total Sales by Region')        plt.xlabel('Region')        plt.ylabel('Total Sales Amount')        plt.xticks(rotation=45)        plt.tight_layout()        plt.show()    </matplotlib_code></root>```"
    output_code_blocks = parseXML(xml_test_response1)
    for line in output_code_blocks:
        logger.info("Line:", line)

if __name__ == "__main__":
    xml_main()
