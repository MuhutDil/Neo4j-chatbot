"""Configuration module for the Hospital Chatbot API.

This module centralizes all configuration settings including Neo4j database
connections, LLM model settings, and application-wide constants. It initializes
shared instances of Neo4jGraph, GigaChat LLM, and GigaChatEmbeddings that are
used throughout the application.

Environment Variables:
    NEO4J_URI: Neo4j database connection URI
    NEO4J_USERNAME: Neo4j database username
    NEO4J_PASSWORD: Neo4j database password
    HOSPITAL_QA_MODEL: Name of the GigaChat model to use for QA tasks
    LLM_API: API key for GigaChat service
    CYPHER_DANGEROUS_REQUESTS: Allow potentially dangerous Cypher queries (default: False)
    DEBUG_API: Enable debug mode for the API (default: False)

Constants:
    BATCH: Maximum number of documents to process in one embedding batch (128).
           Limited due to GigaChatEmbeddings memory constraints.
    DOCUMENTS_TO_RETURN: Number of patient reviews to return from vector index (12).
"""

import os

from langchain_gigachat import GigaChat
from langchain_gigachat.embeddings import GigaChatEmbeddings
from langchain_neo4j import Neo4jGraph

# Neo4j config
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# LLM config
HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL")
KEY = os.getenv("LLM_API")
# Limited the length to the number 128. 
# Because GigaChatEmbeddings can’t handle a large number
# of documents in one go (gigachat.exceptions.ServerError: 500).
# Other embeddings might not have this problem.
BATCH = 128

CYPHER_DANGEROUS_REQUESTS = os.getenv("CYPHER_DANGEROUS_REQUESTS", "False").lower() == "true"
DEBUG_API = os.getenv("DEBUG_API", "False").lower() == "true"

# Optimal amount of patient reviews to return in vector_index (hospital_review_chain)
DOCUMENTS_TO_RETURN = 12

graph = Neo4jGraph(url=NEO4J_URI, database=NEO4J_USERNAME, password=NEO4J_PASSWORD)
llm = GigaChat(
    credentials=KEY,
    verify_ssl_certs=False,
    model=HOSPITAL_QA_MODEL,
    timeout=120, 
    temperature=0,
)
llm_embedding = GigaChatEmbeddings(
        credentials=KEY, 
        verify_ssl_certs=False,
    )
