#!/bin/bash

# Run any setup steps or pre-processing tasks here
echo "Starting hospital RAG FastAPI service..."

# Wait for Neo4j to be ready before initializing vector index
echo "Waiting for Neo4j to be ready..."
until python -c "import config; config.graph.query('MATCH (n) RETURN count(n) LIMIT 1')" 2>/dev/null; do
    echo "Neo4j is unavailable - sleeping"
    sleep 2
done
echo "Neo4j is ready!"

# Start the main application
uvicorn main:app --host 0.0.0.0 --port 8000
