import streamlit as st
import os
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from src.utils.config import config
from dotenv import load_dotenv

class MongoDBConnector:
    def __init__(self):
        db_connection = st.secrets['MONGO_CONNECTION_STRING']
        os.environ["MONGODB_ATLAS_CONNECTION_STRING"] = db_connection
        
        self.database_name = "question_answering"
        self.collection_name = "wikipedia_documents"
        self.full_text_search_index = "full_text_index"
        self.document_store = self.connect_to_mongodb()
        
    def connect_to_mongodb(self):
        document_store = MongoDBAtlasDocumentStore(
            database_name=self.database_name,
            collection_name=self.collection_name,
            vector_search_index="vector_index",
            full_text_search_index=self.full_text_search_index
        )
        return document_store