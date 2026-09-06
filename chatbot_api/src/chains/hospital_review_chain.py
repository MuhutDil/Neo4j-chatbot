import os
import uuid
from langchain_neo4j import Neo4jVector, Neo4jGraph
from langchain_gigachat.embeddings import GigaChatEmbeddings
from langchain_gigachat import GigaChat
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

def get_reviews_vector_chain():
    HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL")
    KEY = os.getenv("LLM_API")
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    
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

    # Limited the length to the number 128. 
    # Because GigaChatEmbeddings can’t handle a large number
    # of documents in one go (gigachat.exceptions.ServerError: 500).
    # Other embeddings might not have this problem.

    BATCH = 128

    records = graph.query("""
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
            f"{k}: {v}" for k, v in rec.items() if k != id and v
        )
        # if content.strip():
        #     docs.append(Document(page_content=content, metadata={"id": rec["id"]}))
        if content.strip():
            docs.append(Document(
                page_content=content, 
                metadata={"sourse_review_id": rec["id"], "id": str(uuid.uuid4())}
            ))

    neo4j_vector_index = Neo4jVector.from_documents(
        documents=docs[:BATCH],
        embedding=llm_embedding,
        url=os.getenv("NEO4J_URI"),
        database=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        index_name="reviews",
    )

    for i in range(BATCH, len(docs), BATCH):
        neo4j_vector_index.add_documents(docs[i:i+BATCH])

    retriever = neo4j_vector_index.as_retriever(search_kwargs={"k": 12})

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
        | llm
        | StrOutputParser()
    )

    return reviews_vector_chain
