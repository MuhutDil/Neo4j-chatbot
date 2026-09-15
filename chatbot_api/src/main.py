"""FastAPI application for the Hospital Chatbot.

This module provides the main API endpoints for the hospital RAG chatbot system.
It exposes endpoints for health checks and querying the hospital agent with
natural language questions about hospital data, wait times, and patient reviews.
"""

from agents.hospital_rag_agent import hospital_rag_agent_ainvoke
from fastapi import FastAPI
from models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital system graph RAG chatbot",
)

@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/hospital-rag-agent")
async def query_hospital_agent(query: HospitalQueryInput) -> HospitalQueryOutput:
    response = await hospital_rag_agent_ainvoke(query.text)
    return response
