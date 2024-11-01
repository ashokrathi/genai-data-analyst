import yaml
from typing import List, Union
from loguru import logger 
import sys
import os

######################################################
# Internal Data Structure for RAG content
# For one RAG Input file, it would create
#     KnowledgeDataset:
#       --> filename
#       --> dataset name
#       --> (*) KnowledgeRecord
#         --> ID
#         --> Tags (Dictionary of Key/Values)
#         --> Text Content (for embeddings)
# Eventually, in other module, this data structure would
# be used to create embeddings for VectorDB.
######################################################
class KnowledgeRecord:
    def __init__(self, id, txt, kv_tags):
        self.id = id
        self.txt = txt
        self.kv_tags = kv_tags

    def __str__(self):
        return f"id = {self.id}, txt={self.txt}"

######################################################
# Primary data structure of Knowledge content for one file
# ######################################################
class KnowledgeDataset:
    def __init__(self, filename):
        if not os.path.isfile(filename):
            err_msg = f"File = {filename} does NOT exist. Failed to create 'KnowledgeDataset' object instance."
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
        self.filename = filename        # Filepath for RAG content
        self.dataset_name = ""          # dataset name matching data/<FolderName>
        self.kd_rec_list: List[KnowledgeRecord] = []           # Will contain list of IDs, KV tags, Text

    def load_knowledge(self):
        # Read the YAML file
        with open(self.filename, 'r') as file:
            try:
              data = yaml.safe_load(file)
            except Exception as e:
              err_msg = f"YAML parsing of File = {filename} failed {e}."
              logger.error(err_msg)
              return

        # Accessing data from the parsed YAML
        logger.info("Knowledge Dataset Name:", data['knowledge']['dataset_name'])
        self.dataset_name = data['knowledge']['dataset_name']
        #print("Len(Records):", len(config['records']))
        for record in data['knowledge']['records']:
            # print(f"-- ID: {record['id']}")
            # print(f"   Text: {record['text']}")
            kd_rec = KnowledgeRecord(record['id'], record['text'], {})
            self.kd_rec_list.append(kd_rec)

    def __str__(self):
        str = f"filename = {self.filename}, dataset_name = {self.dataset_name}\n"
        for rec in self.kd_rec_list:
            str += f"  {rec}\n"
        return str

######################################################
# Main Test Driver
######################################################
if __name__ == "__main__":
    #filename = '../../data/World_Top_Companies/RAG_Knowledge.yaml'
    filename = '../../data/Sales/RAG_Knowledge.yaml'
    if (len(sys.argv) > 1):
        filename = sys.argv[1]
    kd = KnowledgeDataset(filename)
    kd.load_knowledge()
    print(kd)

'''
# Sample YAML Input format
knowledge:
  dataset_name: World_Top_Companies
  records:
    - id: 1
      text: Use this for ranking of company's around the world in different countries across financial metrics, such as, revenue, dividend, dividend yield, earnings, profits, PE ratio, market cap, stock symbols.
    - id: 2
      text: Top or best N companies by revenue or profit or PE ratio or market cap or dividend
    - id: 3
      text: Bottom or worst N companies by revenue or profit or PE ratio or market cap or dividend
    - id: 4
      text: Companies in the "United States" or "China" by revenue or profit or PE ratio or market cap or dividend
'''

