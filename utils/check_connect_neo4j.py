"""Utility script to verify Neo4j database connectivity.

This script tests the connection to a Neo4j graph database by:
1. Loading connection credentials from environment variables
2. Establishing a driver connection
3. Running a SHOW DATABASES query to list available databases

Environment Variables:
    NEO4J_URI: The Neo4j database connection URI
    NEO4J_USERNAME: The username for Neo4j authentication
    NEO4J_PASSWORD: The password for Neo4j authentication

Usage:
    python check_connect_neo4j.py

Output:
    Prints each database name and its current status to stdout.
"""

import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
# Neo4j config
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
with driver.session() as session:
    result = session.run('SHOW DATABASES')
    for record in result:
        print(f"DB {record['name']}, status {record['currentStatus']}")
