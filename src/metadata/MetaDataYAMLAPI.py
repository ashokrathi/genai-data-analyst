from metadata.MetaDataYAML import MetaDataInfoDataset, ColumnRecord, FactRecord, DimensionRecord
import streamlit as st
from loguru import logger

if 'metadatainfo' not in st.session_state:
    st.session_state['metadatainfo'] = ""

def get_metadata():
    metaobj = st.session_state['metadatainfo']
    if (type(metaobj) != MetaDataInfoDataset):
        logger.error("Incorrect type. Likely MetaDataInfoDataset Object is not set yet.") 
    return metaobj

def set_metadata(folder_path):
    if st.session_state['metadatainfo'] == "":
        meta = MetaDataInfoDataset(folder_path)
        st.session_state['metadatainfo'] = meta

def get_current_dataset_path():
    meta = st.session_state['metadatainfo']
    if meta:
        dataset_path = meta.get_data_folderpath()
        return dataset_path
    return ""

def get_current_dataset_name():
    dataset_path = get_current_dataset_path()
    if dataset_path:
        return dataset_path.split("/")[-1]
    return ""

def clear_metadata():
    st.session_state['metadatainfo'] = ""

def force_reset_metadata(folder_path):
    st.session_state['metadatainfo'] = ""
    set_metadata(folder_path)
    obj = get_metadata()
    logger.debug(f"force_reset_metadata: {obj}")
    return obj

def get_columnNamesWithDFs():
    metaObj : MetaDataInfoDataset = st.session_state['metadatainfo']
    #df_names = metaObj.get_dfnames_for_dims()
    list_str = []

    fact_list = metaObj.fact_list
    for fct in fact_list:
        str = f"{fct.df}: "
        str += ', '.join([col.col_name for col in fct.column_list])
        list_str.append(str)

    dim_list = metaObj.dimension_list
    for dim in dim_list:
        str = f"{dim.df}: "
        str += ', '.join([col.col_name for col in dim.column_list])
        list_str.append(str)

    logger.debug(f"get_columnNamesWithDFs: {list_str}")
    return list_str

def get_extraCommentsToLLM():
    metaObj = st.session_state['metadatainfo']
    return metaObj.get_extraCommentsToLLM()

def get_full_file_name(df_name):
    metaObj = get_metadata()
    file_str = metaObj.get_filename_with_path(df_name)
    logger.debug(f"Filename in Meta repo={file_str} for df={df_name}")
    return file_str

def get_column_list(df_name):
    metaObj = get_metadata()
    col_list = metaObj.get_columns_for_df(df_name)
    logger.debug(f"Column List in Meta repo={col_list} for df={df_name}")
    return col_list

def get_all_dims_filenames():
    metaObj = get_metadata()
    dims_list = metaObj.get_dims()
    logger.debug(f"Column List in Meta repo={col_list} for df={df_name}")
    return col_list

############################### MAIN - Test Driver #############################
def MAIN_meta_yaml_api(folder):
    force_reset_metadata(folder)
    logger.debug("Column List with DFs:")
    logger.debug(get_columnNamesWithDFs())
    logger.debug("get_column_list('salesDF')")
    logger.debug(get_column_list('salesDF'))
    logger.debug("get_full_file_name('salesDF')")
    logger.debug(get_full_file_name('salesDF'))
    logger.debug("get_current_dataset_path()")
    logger.debug(get_current_dataset_path())
    logger.debug("get_current_dataset_name()")
    logger.debug(get_current_dataset_name())

if __name__ == "__main__":
    MAIN_meta_yaml_api("../../data/Sales")
