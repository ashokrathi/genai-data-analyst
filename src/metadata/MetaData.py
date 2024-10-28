from loguru import logger
import re

'''
[Facts],salesDF,sales.csv,"sales transactions"
[Dimensions],regionsDF,regions.csv,"regions areas zones regional"
[Dimensions],agentsDF,agents.csv,"agents reps representatives"
[Dimensions],customersDF,customers.csv,"customers clients"
[Dimensions],productsDF,products.csv,"products items"
[Columns],salesDF,sales_id,region_id,agent_id,customer_id,product_id,quantity,unit_price,amount
[Columns],regionsDF,region_id,region_name
[Columns],agentsDF,agent_id,agent_name
[Columns],customersDF,customer_id,customer_name
[Columns],productsDF,product_id,product_name
#[ExtraCommentsToLLM],Use given mapping between,Dataframe and columns.
#[ExtraCommentsToLLM],Strictly use given dataframe names and column names for PD.
facts: [
        { 'df': 'salesDF', 'file': 'sales.csv', 'aliases': ['sales', 'transactions']}
    ]
dims: [
        {'df': 'regionsDF', 'file': 'regions.csv','aliases': ['regions', 'areas']},
        {'df': 'agentsDF', 'file': 'agents.csv','aliases': ['agents', 'reps', 'representatives']},
        {'df': 'customersDF', 'file': 'customers.csv', 'aliases': ['customers', 'clients']},
        {'df': 'productsDF', 'file': 'products.csv', 'aliases': ['products', 'items']}
    ]
columns: {
        'salesDF': ['sales_id', 'region_id', 'agent_id', 'customer_id', 'product_id', 'quantity', 'unit_price', 'amount'],
        'regionsDF': ['region_id', 'region_name'],
        'agentsDF': ['agent_id', 'agent_name'],
        'customersDF': ['customer_id', 'customer_name'],
        'productsDF': ['product_id', 'product_name']
    }

facts: [
         {'df': 'salesDF', 'file': 'sales.csv', 'aliases': ['sales', 'transactions']}
    ]

dims: [
        {'df': 'regionsDF', 'file': 'regions.csv', 'aliases': ['regions', 'areas', 'zones', 'regional']},
        {'df': 'agentsDF', 'file': 'agents.csv', 'aliases': ['agents', 'reps', 'representatives']},
        {'df': 'customersDF', 'file': 'customers.csv', 'aliases': ['customers', 'clients']},
        {'df': 'productsDF', 'file': 'products.csv', 'aliases': ['products', 'items']}
    ]
columns: {
        'salesDF': ['sales_id', 'region_id', 'agent_id', 'customer_id', 'product_id', 'quantity', 'unit_price', 'amount'],
        'regionsDF': ['region_id', 'region_name'],
        'agentsDF': ['agent_id', 'agent_name'],
        'customersDF': ['customer_id', 'customer_name'],
        'productsDF': ['product_id', 'product_name']
    }
extraCommentsToLLM: []

'''

class MetaData:
    def read_metadata(self, folder_path):
        # Read config text file
        txt_file = f"{folder_path}/data_config.txt"
        with open(txt_file, 'r') as f:
            for line in f:
                line = line.strip()
                tokens = line.split(',')
                logger.debug(f"Tokens:{tokens} Len:{len(tokens)}")
                if tokens[0][0] == "#":
                    continue                # Ignore commented lines
                if tokens[0] == "[Facts]" and len(tokens) >= 4:
                    fact = {}
                    fact['df'] = tokens[1]
                    fact['file'] = tokens[2]
                    fact['aliases'] = tokens[3][1:-1].strip().split(" ")
                    self.facts.append(fact)
                elif tokens[0] == "[Dimensions]" and len(tokens) >= 4:
                    dim = {}
                    dim['df'] = tokens[1]
                    dim['file'] = tokens[2]
                    dim['aliases'] = tokens[3][1:-1].strip().split(" ")
                    self.dims.append(dim)
                elif tokens[0] == "[Columns]" and len(tokens) >= 3:
                    key = tokens[1]
                    cols = []
                    for t in tokens[2:]:
                        cols.append(t)
                    self.columns[key] = cols
                elif tokens[0] == "[ExtraCommentsToLLM]" and len(tokens) >= 2:
                    x = ' '.join([l for l in tokens[1:]])
                    self.extraCommentsToLLM.append(x)
                # e.g. [VirtualDimension],revenueDF,List of Specific Company Names,unique(name)
                elif tokens[0] == "[VirtualDimension]" and len(tokens) >= 4:
                    pass

    def __init__(self, folder_path):
        self.facts = []
        self.dims = []
        self.columns = {}
        self.extraCommentsToLLM = []
        self.folder_path = folder_path
        self.read_metadata(folder_path)

    def get_facts(self):
        return self.facts

    def get_dims(self):
        return self.dims

    def get_columns(self):
        return self.columns

    def get_extraCommentsToLLM(self):
        return self.extraCommentsToLLM

    def get_data_folderpath(self):
        return self.folder_path

    def _compare_case_insenstive(self,a,b):
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
    # Return: filename with the path
    ###
    def get_filename_without_path(self, df_name):
        for fact_kv in self.facts:
            if self._compare_case_insenstive(df_name, fact_kv['df']):
                file_str = fact_kv['file']
                return file_str    # Filename Found in Facts
        for dim_kv in self.dims:
            if self._compare_case_insenstive(df_name, dim_kv['df']):
                file_str = dim_kv['file']
                return file_str    # Filename Found in Dimensions
        logger.error(f"Filename NOT found in data_config.txt for DF = {df_name} in dataset = {self.folder_path}")
        return None                                    # Filename Not Found in Facts/Dimensions

    ###
    # Search in both Facts and Dimensions for
    # the filename corresponding to the input Dataframe
    # Return: filename with the path
    ###
    def get_filename_with_path(self, df_name):
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
        for fact_kv in self.facts:
            if self._compare_case_insenstive(file_name, fact_kv['file']):
                df_name = fact_kv['df']
                return df_name    # df_name Found in Facts
        for dim_kv in self.dims:
            if self._compare_case_insenstive(file_name, fact_kv['file']):
                df_name = dim_kv['df']
                return df_name    # df_name Found in Facts
        logger.error(f"Filename NOT found in data_config.txt for DF = {df_name} in dataset = {self.folder_path}")
        return None                                    # Filename Not Found in Dimensions

    ###
    # Return list of dfname's for Dimensions tables only.
    ###
    def get_dfnames_for_dims(self):
        dfnames_list = [dim_kv['df'] for dim_kv in self.dims]
        return dfnames_list

    ###
    # Return list of dfname's for Facts tables only.
    ###
    def get_dfnames_for_facts(self):
        dfnames_list = [fact_kv['df'] for fact_kv in self.facts]
        return dfnames_list

    ###
    # Search column list corresponding to the input Dataframe name
    # Return: column list with column names
    ###
    def get_columns_for_df(self, df_name):
        for col_df in self.columns.keys():
            if self._compare_case_insenstive(df_name, col_df):
                return self.columns[col_df]                # Column list Found
        return None                                        # Column list Not Found

    ###
    # Override method to return  values in string format of MetaData object
    ###
    def __str__(self):
        return \
            f"--- folder: {self.folder_path} ---\n" + \
            f"facts: {self.facts}\n" + \
            f"dims: {self.dims}\n" + \
            f"columns: {self.columns}\n" + \
            f"extraCommentsToLLM: {self.extraCommentsToLLM}" 

def main(folder):
    meta = MetaData(folder)
    logger.info(meta)
    
if __name__ == "__main__":
    main("../data/sales")
