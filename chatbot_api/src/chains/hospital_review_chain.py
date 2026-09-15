"""Hospital review chain module for semantic search over patient reviews.

This module provides functionality to create and query a Neo4j vector index
containing embedded patient hospital reviews. It enables semantic search over
unstructured review text using LangChain's Neo4jVector integration.

Key Components:
    - _create_reviews_vector_index(): Builds vector index from Review nodes
    - _get_reviews_vector_index(): Lazy initialization of the vector index
    - get_reviews_vector_chain(): Creates a retrieval chain for querying reviews

The module uses a module-level variable to cache the vector index for efficient
reuse across multiple queries.
"""

import uuid

import config
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_neo4j import Neo4jVector

# Module-level variable to hold the vector index (initialized lazily)
_neo4j_vector_index = None

def _create_reviews_vector_index():
    """Create a Neo4j vector index from hospital review documents.

    Queries all Review nodes from the Neo4j database and converts them into
    LangChain Document objects. Each document contains review metadata such as
    physician name, patient name, review text, and hospital name. The documents
    are then embedded and stored in a Neo4j vector index for semantic search.

    Returns:
        Neo4jVector: A configured Neo4j vector index containing embedded review documents.

    Note:
        Documents are added in batches according to config.BATCH to manage memory usage.
    """
    records = config.graph.query("""
        MATCH (r:Review)
        RETURN elementId(r) AS id,
            r.physician_name AS physician_name,
            r.patient_name AS patient_name,
            r.text AS text,
            r.hospital_name AS hospital_name
    """)

    docs = []
    for rec in records:
        content = "\n".join(
            f"{k}: {v}" for k, v in rec.items() if k != "id" and v
        )
        if content.strip():
            docs.append(Document(
                page_content=content,
                metadata={"source_review_id": rec["id"], "id": str(uuid.uuid4())}
            ))

    neo4j_vector_index = Neo4jVector.from_documents(
        documents=docs[:config.BATCH],
        embedding=config.llm_embedding,
        url=config.NEO4J_URI,
        database=config.NEO4J_USERNAME,
        password=config.NEO4J_PASSWORD,
        index_name="reviews",
    )

    for i in range(config.BATCH, len(docs), config.BATCH):
        neo4j_vector_index.add_documents(docs[i:i+config.BATCH])

    return neo4j_vector_index

def _get_reviews_vector_index():
    """Get or create the vector index (lazy initialization)."""
    global _neo4j_vector_index
    if _neo4j_vector_index is None:
        _neo4j_vector_index = _create_reviews_vector_index()
    return _neo4j_vector_index

def get_reviews_vector_chain():
    """Create and return a retrieval chain for querying hospital reviews.

    Initializes a Neo4j vector index for reviews (if not already created) and
    constructs a LangChain retrieval chain that uses semantic search to find
    relevant patient reviews and generate answers to user questions.

    Returns:
        Runnable: A LangChain chain that takes a question as input and returns
            a natural language answer based on retrieved patient reviews.

    The chain uses the review template to instruct the LLM to answer questions
    using only the provided context from patient reviews, without fabricating
    information.
    """
    neo4j_vector_index = _get_reviews_vector_index()
    retriever = neo4j_vector_index.as_retriever(
        search_kwargs={"k": config.DOCUMENTS_TO_RETURN}
    )

    review_template = """
    Your job is to use patient
    reviews to answer questions about their experience at a hospital. Use
    the following context to answer questions. Be as detailed as possible, but
    don't make up any information that's not from the context. If you don't know
    an answer, say you don't know.

    Context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(review_template)


    reviews_vector_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | config.llm
        | StrOutputParser()
    )

    return reviews_vector_chain
