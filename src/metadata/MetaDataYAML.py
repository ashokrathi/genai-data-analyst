import yaml
from typing import List, Union
from loguru import logger 
import sys
import os
import re

######################################################
# Internal Data Structure for MetaDataInfo content for each file
# For one MetaDataInfo file, it would create
#    data_metainfo:
#      --> facts:
#        (*)
#          --> df: salesDF
#          --> file: sales.csv
#          --> format: csv
#          --> desc: sales transactions
#          --> columns:
#            - sales_id
#            - date
#            - region_id
#            - agent_id
#            - customer_id
#            - product_id
#            - quantity
#            - unit_price
#            - amount
#      --> dimensions:
#        (*) df: regionsDF
#          file: regions.csv
#          format: csv
#          desc: regions areas zones regional
#          columns:
#            - region_id
#            - region_name
#      --> (*) extra_comments_to_LLM:
#        - For by-month, you can extract month from the date - e.g. from 2023-03-05 you can extract 2023-03.
#        - For by-year, you can extract year from the date - e.g. from 2023-03-05, you can extract 2023.
#        - Strictly use given dataframe names and column names for PD.
######################################################
class ColumnRecord:
    def __init__(self, col_name : str):
        self.col_name = col_name

    def __str__(self):
        return f"{self.col_name}"

class FactRecord:
    def __init__(self, df, file, format, desc, column_list:List[ColumnRecord]):
        self.df = df
        self.file = file
        self.format = format
        self.desc = desc
        self.column_list = column_list

    def __str__(self):
        col_names = ""
        for c in self.column_list:
            col_names += f"{c},"
        return f"df = {self.df}, file={self.file}, format={self.format}, desc={self.desc}, column_list:{col_names}"

class DimensionRecord:
    def __init__(self, df:str, file:str, format:str, desc:set, column_list:List[ColumnRecord]):
        self.df = df
        self.file = file
        self.format = format
        self.desc = desc
        self.column_list = column_list

    def __str__(self):
        col_names = ""
        for c in self.column_list:
            col_names += f"{c},"
        return f"df = {self.df}, file={self.file}, format={self.format}, desc={self.desc}, column_list:{col_names}"

######################################################
# Primary data structure of DataConfig Meta Info for one dataset
######################################################
class MetaDataInfoDataset:
    def load_meta_data_info(self):
        # Read the YAML file
        with open(self.full_filename, 'r') as file:
            try:
              data = yaml.safe_load(file)
            except Exception as e:
              err_msg = f"YAML parsing of File = {self.full_filename} failed {e}."
              logger.error(err_msg)
              return

        ###
        # Parse Facts
        ###
        if data['data_metainfo']['facts']:
            for fct in data['data_metainfo']['facts']:
                df = fct['df']
                file = fct['file']
                format = fct['format']
                desc = fct['desc']
                col_list : List[ColumnRecord] = []
                for col in fct['columns']:          # parse columns
                    col_list.append( ColumnRecord(col) )
                fct_rec = FactRecord(df, file, format, desc, col_list)
                self.fact_list.append(fct_rec)
        else:
            logger.info(f"No Facts exist in dataset file = {self.full_filename}")

        ###
        # Parse dimensions
        ###
        if data['data_metainfo']['dimensions']:
            for dim in data['data_metainfo']['dimensions']:
                df = dim['df']
                file = dim['file']
                format = dim['format']
                desc = dim['desc']
                col_list : List[ColumnRecord] = []
                for col in dim['columns']:          # parse columns
                    col_list.append( ColumnRecord(col) )
                dim_rec = DimensionRecord(df, file, format, desc, col_list)
                self.dimension_list.append(dim_rec)
        else:
            logger.info(f"No Dimensions exist in dataset file = {self.full_filename}")

        ###
        # Parse Extra comments for LLM
        ###
        if data['data_metainfo']['extra_comments_to_LLM']:
            for comm in data['data_metainfo']['extra_comments_to_LLM']:
                self.extra_comments.append(comm)
        else:
            logger.info(f"No Extra Comments-To-LLM exist in dataset file = {self.full_filename}")

    def __init__(self, folder_path:str):
        self.filename = "data_config.yaml"
        self.full_filename = folder_path + "/" + self.filename
        if not os.path.isfile(self.full_filename):
            err_msg = f"File = {self.full_filename} does NOT exist. Failed to create 'MetaDataInfoDataset' object instance."
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
        self.folder_path = folder_path
        self.fact_list: List[FactRecord] = []           # Will contain list of Facts
        self.dimension_list: List[DimensionRecord] = [] # Will contain list of Dimensions
        self.extra_comments: List[str] =  []                       # Will contain list of comments
        self.load_meta_data_info()
    """
    def get_facts(self):
        return self.fact_list

    def get_dims(self):
        return self.dimension_list
    """
    def get_extraCommentsToLLM(self):
        return self.extra_comments

    def get_data_folderpath(self):
        return self.folder_path

    def _compare_case_insenstive(self,a:str,b:str):
        a = a.casefold()
        b = b.casefold()
        if a == b:
            return True
        a = "".join(re.findall("[a-zA-Z]", a))
        b = "".join(re.findall("[a-zA-Z]", b))
        # compare by removing special charactersk
        return a == b

    ###
    # Search in both Facts and Dimensions for
    # the filename corresponding to the input Dataframe
    # Return: filename without the path
    ###
    def get_filename_without_path(self, df_name:str):
        for dim in self.dimension_list:
            if self._compare_case_insenstive(dim.df, df_name):
                return dim.file
        for fact in self.fact_list:
            if self._compare_case_insenstive(fact.df, df_name):
                return fact.file
        logger.error(f"Filename NOT found in data_config.yaml for DF = {df_name} in dataset = {self.folder_path}")
        return None                                    # Filename Not Found in Facts/Dimensions

    ###
    # Search in both Facts and Dimensions for
    # the filename corresponding to the input Dataframe
    # Return: filename with the path
    ###
    def get_filename_with_path(self, df_name:str):
        file_str = self.get_filename_without_path(df_name)
        if file_str != None:
            return self.folder_path + "/" + file_str    # Filename Found in Facts
        return None                                     # Filename Not Found in Dimensions

    ###
    # Search in both Facts and Dimensions for
    # the filename corresponding to the input Dataframe
    # Return: filename with the path
    ###
    def get_dfname_by_filename(self, file_name):
        for dim in self.dimension_list:
            if self._compare_case_insenstive(dim.file, file_name):
                return dim.df
        for fact in self.fact_list:
            if self._compare_case_insenstive(fact.file, file_name):
                return fact.df

        logger.error(f"DF NOT found in data_config.yaml for filename = {file_name} in dataset = {self.folder_path}")
        return None         # No DF found


    ###
    # Return list of dfname's for Dimensions tables only.
    ###
    def get_dfnames_for_dims(self):
        #dfnames_list = [dim_kv['df'] for dim_kv in self.dims]
        dfnames_list = [dim.df for dim in self.dimension_list]
        return dfnames_list

    ###
    # Return list of dfname's for Facts tables only.
    ###
    def get_dfnames_for_facts(self):
        dfnames_list = [fact.df for fact in self.fact_list]
        return dfnames_list

    ###
    # Search column list corresponding to the input Dataframe name
    # Return: column list with column names
    ###
    def get_columns_for_df(self, df_name):
        for dim in self.dimension_list:
            if (dim.df == df_name):
                return [col.col_name for col in dim.column_list]
        for fact in self.fact_list:
            if (fact.df == df_name):
                return [col.col_name for col in fact.column_list]
        return None         # No columns defined for the given DF

    def __str__(self):
        str = f"filename = {self.filename}\n"
        str += f"Facts:\n"
        for rec in self.fact_list:
            str += f"  {rec}\n"

        str += f"Dimensions:\n"
        for rec in self.dimension_list:
            str += f"  {rec}\n"

        str += f"Extra Comments for LLM:\n"
        for rec in self.extra_comments:
            str += f"  {rec}\n"
        return str

######################################################
# Main Test Driver
######################################################
def main_meta_yaml():
    folderpath = '../../data/Sales'
    if (len(sys.argv) > 1):
        filename = sys.argv[1]
    meta = MetaDataInfoDataset(folderpath)
    print(meta)
  
    print("================== MetaData YAML Object Testing ================")
    print("Folder path:", meta.get_data_folderpath())
    df_name = "salesDF"
    print(f"Filename with path for {df_name}:", meta.get_filename_with_path(df_name))
    print(f"Filename without path for salesDF:", meta.get_filename_without_path(df_name))
    print(f"Columns for {df_name}:", meta.get_columns_for_df(df_name))

    df_name = "productsDF"
    print("Columns for {df_name}:", meta.get_columns_for_df(df_name))
    print("DF Names for Facts:", meta.get_dfnames_for_facts())
    print("DF Names for Dimensions:", meta.get_dfnames_for_dims())

    data_file = "regions.csv"
    print(f"DF Name for data filename {data_file}:", meta.get_dfname_by_filename(data_file))

    #print("Get Facts:", meta.get_facts())
    #print("Get Dims:", meta.get_dims())
    print("Extra Comments to LLM:", meta.get_extraCommentsToLLM())

if __name__ == "__main__":
    main_meta_yaml()
