from pydantic import BaseModel, Field

class HospitalQueryInput(BaseModel):
    text: str

class HospitalQueryOutput(BaseModel):
    messages: list
