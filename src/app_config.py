DATA_DIR = "data"
MIC_IMAGE_FILE  = 'resources/mic_icon.png'
usr_prompt_txt_key = 'User_Prompt'
PYTHON_PROG_DIR = "prog"
##########
# Additional Messages to enhance the prompt
##########
PROMPT_GOAL = "Goal: Generate Pandas and Matlibplot code."
PROMPT_COLORS = "Use Color Palette: red, green, blue, pink, yellow"
PROMPT_DATAFRAME_HEADERMSG = "Here are dataframes with respective column names:"
PROMPT_CODEGEN_MSG = "Make sure Python code has no errors. Make matplotlib code compatible with streamlit app. Make sure matplotlib and streamlit libraries are imported."
PROMPT_XMLFORMAT_HEADERMSG = "Generate response only in XML format as below."

PROMPT_XMLTAGS = """<root>
<prompt_id>
123455
</prompt_id>
<sample_data>
Sample data goes here...
</sample_data>
<sample_dataframe_init_code>
Sample Dataframe initialization related code goes here...
</sample_dataframe_init_code>
<list_merged_dataframes>
List all Dataframes in comm-separated format used in merge and other Pandas functions
</list_merged_dataframes>
<dataframe_relationship_code>
Dataframe relationship related code goes here...
</dataframe_relationship_code>
<matplotlib_code>
import all necessary libraries here...
matplot lib code goes here...
</matplotlib_code>
</root>
"""
PROMPT_XMLFORMAT_FOOTERMSG = """For pie charts, only use positive values.
Upon inference, exclude <sample_data> section in the response.
For pie charts, before applying nsmallest() function, filter dataframe to keep only positive values.
"""
