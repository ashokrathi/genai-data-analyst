from metadata.MetaData import MetaData
import streamlit as st
from loguru import logger

if 'metadata' not in st.session_state:
    st.session_state['metadata'] = ""

def get_metadata():
    metaobj = st.session_state['metadata']
    if (type(metaobj) != MetaData):
        logger.error("Incorrect type. Likely MetaData Object is not set yet.") 
    return metaobj

def set_metadata(folder_path):
    if st.session_state['metadata'] == "":
        meta = MetaData(folder_path)
        st.session_state['metadata'] = meta

def get_current_dataset_path():
    meta = st.session_state['metadata']
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
    st.session_state['metadata'] = ""

def force_reset_metadata(folder_path):
    st.session_state['metadata'] = ""
    set_metadata(folder_path)
    obj = get_metadata()
    logger.debug(f"force_reset_metadata: {obj}")
    return obj

def get_columnNamesWithDFs():
    metaObj = st.session_state['metadata']
    df_cols = metaObj.get_columns()
    list_str = []
    for df in df_cols.keys():
        str = f"{df}: "
        col_list = df_cols[df]
        str += ', '.join([name for name in col_list])
        list_str.append(str)
    logger.debug(f"get_columnNamesWithDFs: {list_str}")
    return list_str

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

def main(folder):
    force_reset_metadata(folder)
    logger.debug("Column List with DFs:")
    logger.debug(get_columnNamesWithDFs())
    
if __name__ == "__main__":
    main("../data/sales")
