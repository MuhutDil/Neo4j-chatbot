import os
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_gigachat import GigaChat
from chains.hospital_review_chain import get_reviews_vector_chain
from chains.hospital_cypher_chain import get_hospital_cypher_chain
from tools.wait_times import (
    get_current_wait_times,
    get_most_available_hospital,
)

HOSPITAL_AGENT_MODEL = os.getenv("HOSPITAL_AGENT_MODEL")
KEY = os.getenv("LLM_API")
DEBUG_API = os.getenv("DEBUG_API", "False").lower() == "true"

@tool
def experiences(query: str) -> str:
    """Useful when you need to answer questions
    about patient experiences, feelings, or any other qualitative
    question that could be answered about a patient using semantic
    search. Not useful for answering objective questions that involve
    counting, percentages, aggregations, or listing facts. Use the
    entire prompt as input to the tool. For instance, if the prompt is
    "Are patients satisfied with their care?", the input should be
    "Are patients satisfied with their care?".
    """
    return get_reviews_vector_chain().invoke(query)
 
@tool
def graph(query: str) -> str:
    """Useful for answering questions about patients,
    physicians, hospitals, insurance payers, patient review
    statistics, and hospital visit details. Use the entire prompt as
    input to the tool. For instance, if the prompt is "How many visits
    have there been?", the input should be "How many visits have
    there been?".
    """
    return get_hospital_cypher_chain().invoke(query)
 
@tool
def waits(hospital_name: str = "all") -> str:
    """Use when asked about current wait times
    at a specific hospital. This tool can only get the current
    wait time at a hospital and does not have any information about
    aggregate or historical wait times. Do not pass the word "hospital"
    as input, only the hospital name itself. For example, if the prompt
    is "What is the current wait time at Jordan Inc Hospital?", the
    input should be "Jordan Inc".
    """
    return get_current_wait_times(hospital_name)
 
@tool
def availability(requirement: str = "") -> str:
    """Use when you need to find out which hospital has the shortest
    wait time. This tool does not have any information about aggregate
    or historical wait times. This tool returns a dictionary with the
    hospital name as the key and the wait time in minutes as the value.
    """
    return get_most_available_hospital(requirement)

@tool
def test_API() -> str:
    """If the query contains the word "test" or anything related
    to it, respond with a simple line: "Test successful!"
    """
    return "Test successful!"
 
tools = [experiences, graph, waits, availability]
if DEBUG_API:
    tools.append(test_API)

chat_model = GigaChat(
    credentials=KEY,
    verify_ssl_certs=False,
    model=os.getenv("HOSPITAL_QA_MODEL"),
    timeout=120, 
    temperature=0,
)

hospital_rag_agent = create_agent(
    model=chat_model,
    tools=tools,
    system_prompt="""You are a helpful hospital assistant that can
    answer questions about patients experiences, hospital relationships,
    wait times, and hospital availability"""
)

def hospital_rag_agent_invoke(query: str) -> dict[list]:
    return hospital_rag_agent.invoke(
        {"messages": [{'role': 'human', 'content': query}]}
    )

async def hospital_rag_agent_ainvoke(query: str) -> dict[list]:
    return await hospital_rag_agent.ainvoke(
        {"messages": [{'role': 'human', 'content': query}]}
    )
