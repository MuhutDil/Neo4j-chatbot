"""Hospital graph database ETL module for loading CSV data into Neo4j.

This module provides functionality to load structured hospital data from CSV files
into a Neo4j graph database following a specific ontology. It handles:
- Creating uniqueness constraints on node labels
- Loading nodes (Hospital, Payer, Physician, Patient, Visit, Review, Question)
- Creating relationships between nodes (AT, WRITES, TREATS, COVERED_BY, HAS, EMPLOYS)
- Setting up vector indexes for semantic search on reviews

The module uses configuration-driven approach with NODE_CONFIGS and RELATIONSHIP_CONFIGS
to generically process different node types and relationships.

Environment Variables:
    HOSPITALS_CSV_PATH: Path to hospitals CSV file
    PAYERS_CSV_PATH: Path to payers CSV file
    PHYSICIANS_CSV_PATH: Path to physicians CSV file
    PATIENTS_CSV_PATH: Path to patients CSV file
    VISITS_CSV_PATH: Path to visits CSV file
    REVIEWS_CSV_PATH: Path to reviews CSV file

Typical Usage:
    >>> from hospital_bulk_csv_write import load_hospital_graph_from_csv
    >>> load_hospital_graph_from_csv()
"""

import logging
import os

import config
from neo4j_graphrag.indexes import create_vector_index
from retry import retry

# Paths to CSV files containing hospital data
HOSPITALS_CSV_PATH = os.getenv("HOSPITALS_CSV_PATH")
PAYERS_CSV_PATH = os.getenv("PAYERS_CSV_PATH")
PHYSICIANS_CSV_PATH = os.getenv("PHYSICIANS_CSV_PATH")
PATIENTS_CSV_PATH = os.getenv("PATIENTS_CSV_PATH")
VISITS_CSV_PATH = os.getenv("VISITS_CSV_PATH")
REVIEWS_CSV_PATH = os.getenv("REVIEWS_CSV_PATH")

# Configure the logging module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


LOGGER = logging.getLogger(__name__)

NODES = ["Hospital", "Payer", "Physician", "Patient", "Visit", "Review", "Question"]

# Whitelist of valid node labels to prevent Cypher injection
VALID_NODE_LABELS = frozenset(NODES)

# Configuration for loading nodes from CSV files
# Each entry contains: (label, csv_path_var, merge_properties, additional_properties)
NODE_CONFIGS: list[dict] = [
    {
        "label": "Hospital",
        "csv_path_var": HOSPITALS_CSV_PATH,
        "merge_props": {"id": "toInteger(hospitals.hospital_id)"},
        "additional_props": {
            "name": "hospitals.hospital_name",
            "state_name": "hospitals.hospital_state",
        },
        "alias": "hospitals",
    },
    {
        "label": "Payer",
        "csv_path_var": PAYERS_CSV_PATH,
        "merge_props": {"id": "toInteger(payers.payer_id)"},
        "additional_props": {"name": "payers.payer_name"},
        "alias": "payers",
    },
    {
        "label": "Physician",
        "csv_path_var": PHYSICIANS_CSV_PATH,
        "merge_props": {"id": "toInteger(physicians.physician_id)"},
        "additional_props": {
            "name": "physicians.physician_name",
            "dob": "physicians.physician_dob",
            "grad_year": "physicians.physician_grad_year",
            "school": "physicians.medical_school",
            "salary": "toFloat(physicians.salary)",
        },
        "alias": "physicians",
    },
    {
        "label": "Patient",
        "csv_path_var": PATIENTS_CSV_PATH,
        "merge_props": {"id": "toInteger(patients.patient_id)"},
        "additional_props": {
            "name": "patients.patient_name",
            "sex": "patients.patient_sex",
            "dob": "patients.patient_dob",
            "blood_type": "patients.patient_blood_type",
        },
        "alias": "patients",
    },
    {
        "label": "Visit",
        "csv_path_var": VISITS_CSV_PATH,
        "merge_props": {"id": "toInteger(visits.visit_id)"},
        "additional_props": {
            "room_number": "toInteger(visits.room_number)",
            "admission_type": "visits.admission_type",
            "admission_date": "visits.date_of_admission",
            "test_results": "visits.test_results",
            "status": "visits.visit_status",
        },
        "on_create_set": {"chief_complaint": "visits.chief_complaint"},
        "on_match_set": {"chief_complaint": "visits.chief_complaint"},
        "alias": "visits",
    },
    {
        "label": "Review",
        "csv_path_var": REVIEWS_CSV_PATH,
        "merge_props": {"id": "toInteger(reviews.review_id)"},
        "additional_props": {
            "text": "reviews.review",
            "patient_name": "reviews.patient_name",
            "physician_name": "reviews.physician_name",
            "hospital_name": "reviews.hospital_name",
        },
        "alias": "reviews",
    },
]

# Configuration for loading relationships from CSV files
# Each entry contains: (relationship_name, csv_path_var, source_node, target_node, 
#                       source_id_field, target_id_field, additional_properties)
RELATIONSHIP_CONFIGS: list[dict] = [
    {
        "name": "AT",
        "csv_path_var": VISITS_CSV_PATH,
        "source_label": "Visit",
        "target_label": "Hospital",
        "source_id": "toInteger(trim(row.`visit_id`))",
        "target_id": "toInteger(trim(row.`hospital_id`))",
        "alias": "row",
    },
    {
        "name": "WRITES",
        "csv_path_var": REVIEWS_CSV_PATH,
        "source_label": "Visit",
        "target_label": "Review",
        "source_id": "toInteger(reviews.visit_id)",
        "target_id": "toInteger(reviews.review_id)",
        "alias": "reviews",
    },
    {
        "name": "TREATS",
        "csv_path_var": VISITS_CSV_PATH,
        "source_label": "Physician",
        "target_label": "Visit",
        "source_id": "toInteger(visits.physician_id)",
        "target_id": "toInteger(visits.visit_id)",
        "alias": "visits",
    },
    {
        "name": "COVERED_BY",
        "csv_path_var": VISITS_CSV_PATH,
        "source_label": "Visit",
        "target_label": "Payer",
        "source_id": "toInteger(visits.visit_id)",
        "target_id": "toInteger(visits.payer_id)",
        "alias": "visits",
        "on_create_set": {
            "service_date": "visits.discharge_date",
            "billing_amount": "toFloat(visits.billing_amount)",
        },
    },
    {
        "name": "HAS",
        "csv_path_var": VISITS_CSV_PATH,
        "source_label": "Patient",
        "target_label": "Visit",
        "source_id": "toInteger(visits.patient_id)",
        "target_id": "toInteger(visits.visit_id)",
        "alias": "visits",
    },
    {
        "name": "EMPLOYS",
        "csv_path_var": VISITS_CSV_PATH,
        "source_label": "Hospital",
        "target_label": "Physician",
        "source_id": "toInteger(visits.hospital_id)",
        "target_id": "toInteger(visits.physician_id)",
        "alias": "visits",
    },
]


def _set_uniqueness_constraints(tx, node):
    """Create uniqueness constraint for a node label.
    
    Args:
        tx: Neo4j transaction object
        node: Node label string
        
    Raises:
        ValueError: If node label is not in the whitelist
    """
    if node not in VALID_NODE_LABELS:
        raise ValueError(f"Invalid node label: {node}. Must be one of {VALID_NODE_LABELS}")
    
    # Use parameterized query for safety - node label must be validated and interpolated
    # since Neo4j doesn't support parameters for labels, we validate against whitelist
    query = """CREATE CONSTRAINT IF NOT EXISTS FOR (n:`%s`)
        REQUIRE n.id IS UNIQUE;""" % node
    _ = tx.run(query, {})


def _build_merge_query(config: dict) -> str:
    """Build a Cypher MERGE query from node configuration.
    
    Args:
        config: Dictionary containing node configuration
        
    Returns:
        Cypher query string for loading nodes from CSV
    """
    label = config["label"]
    csv_path = config["csv_path_var"]
    merge_props = config["merge_props"]
    additional_props = config.get("additional_props", {})
    on_create_set = config.get("on_create_set", {})
    on_match_set = config.get("on_match_set", {})
    alias = config["alias"]
    
    # Build MERGE clause properties
    merge_clause_parts = []
    for prop, value in merge_props.items():
        merge_clause_parts.append(f"{prop}: {value}")
    merge_clause = ", ".join(merge_clause_parts)
    
    # Build additional properties for MERGE
    additional_clause_parts = []
    for prop, value in additional_props.items():
        additional_clause_parts.append(f"{prop}: {value}")
    additional_clause = ",\n                            ".join(additional_clause_parts)
    
    # Build the base MERGE query
    if additional_clause:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{csv_path}' AS {alias}
        MERGE (n:{label} {{{merge_clause},
                            {additional_clause}
                            }});
        """
    else:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{csv_path}' AS {alias}
        MERGE (n:{label} {{{merge_clause}}});
        """
    
    # Add ON CREATE SET clauses
    if on_create_set:
        for prop, value in on_create_set.items():
            query = query.replace("});", f"}})\n            ON CREATE SET n.{prop} = {value}")
    
    # Add ON MATCH SET clauses
    if on_match_set:
        for prop, value in on_match_set.items():
            query = query.replace("});", f"}})\n            ON MATCH SET n.{prop} = {value}")
    
    # Fix any double closing braces from replacements
    query = query.replace("}})", "})")
    
    return query


def _build_relationship_query(config: dict) -> str:
    """Build a Cypher relationship creation query from configuration.
    
    Args:
        config: Dictionary containing relationship configuration
        
    Returns:
        Cypher query string for loading relationships from CSV
    """
    rel_name = config["name"]
    csv_path = config["csv_path_var"]
    source_label = config["source_label"]
    target_label = config["target_label"]
    source_id = config["source_id"]
    target_id = config["target_id"]
    alias = config["alias"]
    on_create_set = config.get("on_create_set", {})
    
    # Build the base relationship query
    query = f"""
        LOAD CSV WITH HEADERS FROM '{csv_path}' AS {alias}
        MATCH (source: `{source_label}` {{ `id`: {source_id} }})
        MATCH (target: `{target_label}` {{ `id`: {target_id} }})
        MERGE (source)-[r: `{rel_name}`]->(target)
        """
    
    # Add ON CREATE SET clauses if present
    if on_create_set:
        set_clauses = []
        for prop, value in on_create_set.items():
            set_clauses.append(f"r.{prop} = {value}")
        query += "\n            ON CREATE SET\n                " + ",\n                ".join(set_clauses)
    
    return query


@retry(tries=100, delay=10)
def load_hospital_graph_from_csv() -> None:
    """Load structured hospital CSV data into Neo4j graph database.

    This function performs a complete ETL process to populate a Neo4j graph
    with hospital system data. It follows these steps:
    1. Creates a vector index on Review nodes for semantic search
    2. Sets up uniqueness constraints on all node types
    3. Loads nodes from CSV files (Hospital, Payer, Physician, Patient, Visit, Review)
    4. Creates relationships between nodes based on relationship configurations

    The function uses retry logic (100 retries with 10 second delays) to handle
    transient database connection issues.

    Raises:
        Exception: If the database operations fail after all retry attempts.

    Note:
        This function requires environment variables to be set for CSV file paths
        and Neo4j connection credentials (see config module).
    """

    driver = config.graph
    create_vector_index(
        driver,
        name="reviews",
        label="Review",
        embedding_property="vectorProperty",
        dimensions=1024,
        similarity_fn="cosine",
    )

    LOGGER.info("Setting uniqueness constraints on nodes")
    with driver.session() as session:
        for node in NODES:
            session.execute_write(_set_uniqueness_constraints, node)

    # Load all nodes using generic function
    for node_config in NODE_CONFIGS:
        label = node_config["label"]
        LOGGER.info("Loading %s nodes", label.lower())
        with driver.session() as session:
            query = _build_merge_query(node_config)
            _ = session.run(query, {})

    # Load all relationships using generic function
    for rel_config in RELATIONSHIP_CONFIGS:
        rel_name = rel_config["name"]
        LOGGER.info("Loading '%s' relationships", rel_name)
        with driver.session() as session:
            query = _build_relationship_query(rel_config)
            _ = session.run(query, {})


if __name__ == "__main__":
    load_hospital_graph_from_csv()
