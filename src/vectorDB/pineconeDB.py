###
# Open source Imports
###
import os
import sys
from langchain_openai import OpenAIEmbeddings
#from langchain.vectorstores import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
import streamlit as st
from loguru import logger

###
# Imports from the code base
###
from app_config import PINECONE_INDEX, RAG_META_YAML_FILENAME, NAMESPACE_METADATA, QUALITY_THRESHOLD, DATA_DIR
from metadata.MetaDataAPI import get_current_dataset_path
from vectorDB.yaml_parser import KnowledgeDataset

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

    ###
    # Query PineconeDB for similarity check
    ###
    def query_meta_documents(self, txt, namespace):
        doc_list = self.vectorstore.similarity_search_with_score(txt, namespace=namespace, k=4)
        return doc_list
    
    ###
    # Load Metadata texts, key/value tags info into PineconeDB
    # Note: This can be done in offline manner using the Main program below.
    ###
    def load_meta_documents(self, dataset_name, namespace):
        # path to RAG Yaml file
        yaml_filename = DATA_DIR + "/" + dataset_name + "/" + RAG_META_YAML_FILENAME
        kd = KnowledgeDataset(yaml_filename)
        kd.load_knowledge()
        #logger.info("Knowledge Dataset: {kd}")
        documents = []
        IDs = []
        logger.info(f"Vectors To Update: {len(kd.kd_rec_list)}")
        for i, rec in enumerate(kd.kd_rec_list):
            metadata = rec.kv_tags
            metadata['namespace'] = namespace
            metadata['dataset'] = dataset_name
            doc = Document(page_content=rec.txt, metadata=metadata)
            documents.append(doc)
            IDs.append(str(rec.id))
            if (i % 10 == 0):
                logger.info(f"Prepared for Insertion ({dataset_name}): {i+1}, ID = {rec.id}")
            #txt_embeddings = self.embeddings.embed_query(rec.txt)  # Create an embedding for the document
            #logger.info(f"Embeddings Size: {len(txt_embeddings)}")
            #vectors_update.append({"id":rec.id, "values":txt_embeddings, "metadata":metadata})
        logger.info(f"Documents Size to add: {len(documents)}, IDs size:{len(IDs)}")
        self.vectorstore.add_documents(documents=documents, ids=IDs, namespace=namespace)

######################################################
# Create or re-use cached My Pinecone instance
# Load Metadata texts, key/value tags info into PineconeDB
#
# Note: This can be done in offline manner using the
# Main program below.
######################################################
def get_my_pinecone_cached_instance() -> my_pinecone:
    if not st.session_state['pinecone_instance']:
            try:
                pc = my_pinecone(PINECONE_INDEX)
                st.session_state['pinecone_instance'] = pc
                logger.info("My Pinecone Instance/connection for Index = {PINECONE_INDEX} successfully created.")
            except ValueError as e:
                logger.error(f"Failed to connect with Pinecone DB: {e}")
                logger.error("My Pinecone Instance/connection FAILED for Index = {PINECONE_INDEX}.")
    return st.session_state['pinecone_instance']

######################################################
# Based on prompt, identify the dataset name
# from VectorDB (similarity check).
# Returns K/V pairs:
#   - dataset name
#   - page_content (Text)
#   - similarity score
######################################################
def get_prompt_dataset_quality(prompt:str, selected_dataset:str) -> {}:
    logger.info(f"In check_prompt_quality for prompt={prompt}...")
    pc = get_my_pinecone_cached_instance()
    ret_value = {"dataset":"NotKnown", "score":"0.0", "page_content":"Nothing"}
    docs_with_similarity_score = pc.query_meta_documents(prompt, NAMESPACE_METADATA)
    if pc and docs_with_similarity_score and len(docs_with_similarity_score) >= 1:
        result = docs_with_similarity_score[0]      # result is tuple 
        page_content = result[0].page_content       # First = data(page_content, metadata), Second = Score
        metadata = result[0].metadata
        similar_dataset = metadata['dataset']
        score = result[1]
        logger.info(f"similar_dataset = {similar_dataset}, similarity_score = {score}")
        ret_value = {}
        ret_value['dataset'] = similar_dataset
        ret_value['score'] = f"{score:.2f}"
        ret_value['page_content'] = page_content
        return ret_value
    
    logger.info(f"Return Value = {ret_value}")
    return ret_value

    #full_RAG_yaml_filename_path = get_current_dataset_path() + "/" + RAG_META_FILENAME
    #pc.load_meta_documents(full_RAG_yaml_filename_path, NAMESPACE_METADATA)

######################################################
# Main Test Driver
#
# Note: This can be used to load RAG content from each
# data folder. RAG content is in "RAG_Knowledge.yaml"
#
#  [progrma] -load [Dataset_Name]
#  [progrma] -query [Prompt_String]
######################################################
def main_driver(cmd, arg):
    index_name = PINECONE_INDEX
    try:
        pc = my_pinecone(index_name)
        #print(OpenAIEmbeddings())
    except ValueError as e:
        logger.error(f"Failed to connect with Pinecone DB: {e}")
        sys.exit(1)

    if cmd == "-load":
        dataset_name = arg
        logger.info(f"About to loaded embeddings for dataset: {dataset_name}")
        pc.load_meta_documents(dataset_name, NAMESPACE_METADATA)
        logger.info(f"Loaded embeddings for dataset: {dataset_name}")
    elif cmd == "-query":
        qry = arg
        qry_result = pc.query_meta_documents(qry, NAMESPACE_METADATA)
        logger.info(qry)
        for i,result in enumerate(qry_result):
            print(f"Type of doc {i}:", type(doc))
            print(f"Type of doc[0] {i}:", type(doc[0]))
            print(f"Type of doc[1] {i}:", type(doc[1]))
            page_content = result[0].page_content
            metadata = result[0].metadata
            score = result[1]
            logger.info(f"  Result({i}): page_content = {page_content}")
            logger.info(f"  Result({i}): Score = {score}")
            for k,v in metadata.items():
                logger.info(f"       {k}: {v}")

if __name__ == "__main__":
    #dataset_name = 'World_Top_Companies'
    if (len(sys.argv) > 2):
        main_driver(sys.argv[1], sys.argv[2])
        sys.exit(0)
    logger.info(
"""
Usage: sys.arv[0] [-load | -query] [ARG]
-load [dataset_name]
-prompt [Query string in double-quotes]
"""
    )
    sys.exit(1)
