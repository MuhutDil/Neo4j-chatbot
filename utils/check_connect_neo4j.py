import os
import logging
from retry import retry
from neo4j import GraphDatabase

from dotenv import load_dotenv
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
