"""Pydantic models for Hospital RAG query API.

This module defines the input and output schemas for the hospital RAG agent API endpoint.
"""

from pydantic import BaseModel, Field


class HospitalQueryInput(BaseModel):
    """Input model for hospital RAG queries.

    Attributes:
        text: The user's natural language question about hospital data,
              wait times, or patient reviews.
    """
    text: str = Field(description="The user's natural language question")

class HospitalQueryOutput(BaseModel):
    """Output model for hospital RAG query responses.

    Attributes:
        messages: A list of message dictionaries containing the agent's response.
                  Typically includes role ('ai'/'human') and content fields.
    """
    messages: list = Field(description="List of message dictionaries with the agent's response")
