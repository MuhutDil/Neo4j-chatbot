import os
from dotenv import load_dotenv
from langchain_gigachat.embeddings import GigaChatEmbeddings


load_dotenv()
KEY = os.getenv("LLM_API")

llm = GigaChatEmbeddings(
        credentials=KEY, 
        verify_ssl_certs=False,
    )

try:
    resp = llm.embed_query('Test')
    print('Success!')
except Exception as e:
    print(f'Error: {e}')