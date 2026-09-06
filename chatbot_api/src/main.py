from fastapi import FastAPI
from agents.hospital_rag_agent import hospital_rag_agent_ainvoke
from models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput
from utils.async_utils import async_retry
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

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
