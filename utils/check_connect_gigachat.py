"""Utility script to verify GigaChat LLM API connectivity.

This script tests the connection to the GigaChat embedding model by:
1. Loading the API key from environment variables
2. Initializing the GigaChatEmbeddings client
3. Sending a test embedding request

Environment Variables:
    LLM_API: The GigaChat API key for authentication

Usage:
    python check_connect_gigachat.py

Output:
    Prints 'Success!' if the embedding request succeeds, or an error message
    describing the failure.
"""

import os

from dotenv import load_dotenv
from gigachat.exceptions import BadRequestError
from langchain_gigachat.embeddings import GigaChatEmbeddings

load_dotenv()
KEY = os.getenv("LLM_API")

llm = GigaChatEmbeddings(
        credentials='KEY', 
        verify_ssl_certs=False,
    )

try:
    resp = llm.embed_query('Test')
    print('Success!')
except BadRequestError:
    print('Invalid KEY!')