"""Hospital Cypher Chain module for querying Neo4j graph database.

This module provides a lazy-initialized GraphCypherQAChain for executing
Cypher queries against the hospital Neo4j graph database. It uses LangChain's
GraphCypherQAChain to convert natural language questions into Cypher queries
and return structured answers about hospital data.
"""

import config
from chains import prompts
from langchain_neo4j import GraphCypherQAChain

_hospital_cypher_chain = None

def _get_hospital_cypher_chain():
    """Create and configure a new GraphCypherQAChain instance.

    This internal function initializes a GraphCypherQAChain with the configured
    LLM, graph connection, and custom prompts for cypher generation and QA.

    Returns:
        GraphCypherQAChain: A configured chain for executing Cypher queries
            against the hospital graph database.
    """
    graph = config.graph
    graph.refresh_schema()

    hospital_cypher_chain = GraphCypherQAChain.from_llm(
        cypher_llm=config.llm,
        qa_llm=config.llm,
        graph=graph,
        verbose=True,
        qa_prompt=prompts.qa_generation_prompt,
        cypher_prompt=prompts.cypher_generation_prompt,
        validate_cypher=True,
        top_k=100,
        allow_dangerous_requests=config.CYPHER_DANGEROUS_REQUESTS,
    )

    return hospital_cypher_chain

def get_hospital_cypher_chain():
    """Get the singleton instance of GraphCypherQAChain.

    Uses lazy initialization to create the chain on first access, then caches
    it for subsequent calls to avoid recreation overhead.

    Returns:
        GraphCypherQAChain: The cached or newly created chain instance.
    """
    global _hospital_cypher_chain
    if _hospital_cypher_chain is None:
        _hospital_cypher_chain = _get_hospital_cypher_chain()
    return _hospital_cypher_chain
