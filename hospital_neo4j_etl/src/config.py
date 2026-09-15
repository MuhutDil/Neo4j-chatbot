"""Configuration module for Neo4j graph database connection.

This module initializes the Neo4j connection using environment variables
and provides a graph driver instance for database operations.

Environment Variables:
    NEO4J_URI: The Neo4j database connection URI
    NEO4J_USERNAME: The username for Neo4j authentication
    NEO4J_PASSWORD: The password for Neo4j authentication

Attributes:
    NEO4J_URI (str): Neo4j database URI from environment
    NEO4J_USERNAME (str): Neo4j username from environment
    NEO4J_PASSWORD (str): Neo4j password from environment
    graph: Neo4j GraphDatabase driver instance
"""

import os

from neo4j import GraphDatabase

# Neo4j config
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

graph = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))