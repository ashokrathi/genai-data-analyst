from metadata.MetaDataAPI import get_columnNamesWithDFs, get_extraCommentsToLLM
from loguru import logger

from app_config import \
    PROMPT_GOAL, \
    PROMPT_COLORS, \
    PROMPT_DATAFRAME_HEADERMSG, \
    PROMPT_CODEGEN_MSG, \
    PROMPT_XMLFORMAT_HEADERMSG, \
    PROMPT_XMLTAGS, \
    PROMPT_XMLFORMAT_FOOTERMSG

def build_meta_data_prompt():
    df_col_list = get_columnNamesWithDFs()
    meta_data_msg = '     \n'.join([line for line in df_col_list])
    return "\n"+meta_data_msg+"\n"

def build_extra_comments_prompt():
    extra_comments = get_extraCommentsToLLM()
    meta_data_comments = '\n'.join([line for line in extra_comments])
    return "\n"+meta_data_comments+"\n"

def build_llm_prompt(user_prompt):
    meta_data_msg = build_meta_data_prompt()
    extra_comments = build_extra_comments_prompt()
    llm_prompt = f"{PROMPT_GOAL} {user_prompt}"
    llm_prompt += f"\n{PROMPT_DATAFRAME_HEADERMSG}"
    llm_prompt += f"\n{meta_data_msg}"
    llm_prompt += f"\n{extra_comments}"
    llm_prompt += f"\n{PROMPT_COLORS}"
    llm_prompt += f"\n{PROMPT_CODEGEN_MSG}"
    llm_prompt += f"\n{PROMPT_XMLFORMAT_HEADERMSG}"
    llm_prompt += f"\n{PROMPT_XMLTAGS}"
    llm_prompt += f"\n{PROMPT_XMLFORMAT_FOOTERMSG}"
    logger.debug(f"BUILT: {llm_prompt}")
        
    return llm_prompt

if __name__ == "__main__":
    user_prompt = "Generate Pandas code to create bar chart for total sales of each region"
    meta_data_msg = """
      SalesDF: agent_id, region_id, customer_id, sales_date, parts_id, parts_quantity, sales_amount
      AgentsDF: agent_id, agent_name
      RegionsDF: region_id, region_name
      PartsDF: part_id, part_name
      CustomersDF: cusotmer_id, customer_name
    """
    logger.debug("LLM_PROMPT:")
    logger.debug( build_llm_prompt(user_prompt) )
