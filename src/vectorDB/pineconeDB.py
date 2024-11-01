import os
import sys

from langchain_openai import OpenAIEmbeddings
#from langchain.vectorstores import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document


from loguru import logger
from yaml_parser import KnowledgeDataset

###############################################
# Class to access Pinecone APIs
# 1. Creat and save embeddings, IDs, metadata,
#    namespace.
# 2. Query vectorDB for a given string and for
#    similarity score.
###############################################
class my_pinecone():
    def __init__(self, index_name):
        ###
        # Initialize API Keys
        ###
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if (not self.openai_api_key):
            err_msg = "OPENAI_API_KEY not found in environment. First set it up to proceed."
            logger.error(err_msg)
            raise ValueError(err_msg)

        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if (not self.pinecone_api_key):
            err_msg = "PINECONE_API_KEY not found in environment. First set it up to proceed."
            logger.error(err_msg)
            raise ValueError(err_msg)

        ###
        # Initialize embeddings model and vectore store
        # default OpenAIEmbeddings:
        #   uses "text-embedding-ada-002" model
        #   has dimension size = 1536
        ###
        self.index_name = index_name
        self.embeddings = OpenAIEmbeddings()
        logger.info(f"Embeddings Model: {self.embeddings}")
        #self.vectorstore = Pinecone(index_name=index_name, embedding=self.embeddings)
        self.vectorstore = PineconeVectorStore(index_name=index_name, embedding=self.embeddings)
        logger.info(f"Vector Store: {self.vectorstore}")

    def query_meta_documents(self, txt, namespace):
        doc_list = self.vectorstore.similarity_search_with_score(txt, namespace=namespace, k=4)
        return doc_list
    
    def load_meta_documents(self, yaml_filename, namespace):
        # path to an example text file
        kd = KnowledgeDataset(yaml_filename)
        kd.load_knowledge()
        #logger.info("Knowledge Dataset: {kd}")
        documents = []
        IDs = []
        logger.info(f"Vectors To Update: {len(kd.kd_rec_list)}")
        for rec in kd.kd_rec_list:
            metadata = rec.kv_tags
            metadata['namespace'] = namespace
            doc = Document(page_content=rec.txt, metadata=metadata)
            documents.append(doc)
            IDs.append(str(rec.id))
            print(f"ID Type: {rec.id}")
            #txt_embeddings = self.embeddings.embed_query(rec.txt)  # Create an embedding for the document
            #logger.info(f"Embeddings Size: {len(txt_embeddings)}")
            #vectors_update.append({"id":rec.id, "values":txt_embeddings, "metadata":metadata})
        logger.info(f"Documents Size to add: {len(documents)}, IDs size:{len(IDs)}")
        self.vectorstore.add_documents(documents=documents, ids=IDs, namespace=namespace)

######################################################
# Main Test Driver
######################################################
def main_driver(yaml_filename):
    index_name = "ik-capstone"
    try:
        pc = my_pinecone(index_name)
        #print(OpenAIEmbeddings())
    except ValueError as e:
        logger.error(f"Failed to connect with Pinecone DB: {e}")
        sys.exit(1)
    logger.info(f"About to loaded embeddings for: {yaml_filename}")
    #pc.load_meta_documents(yaml_filename, "meta_ds")
    #logger.info(f"Loaded embeddings for: {yaml_filename}")
    qry = "top agents by sales"
    qry_result = pc.query_meta_documents(qry, "meta_ds")
    logger.info(qry)
    for i,doc in enumerate(qry_result):
        logger.info(f"  Result({i}): Document = {doc[0]}, Score = {doc[1]}")

if __name__ == "__main__":
    #filename = '../../data/World_Top_Companies/RAG_Knowledge.yaml'
    yaml_filename = '../../data/Sales/RAG_Knowledge.yaml'
    if (len(sys.argv) > 1):
        yaml_filename = sys.argv[1]
    main_driver(yaml_filename)

