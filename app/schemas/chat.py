from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    thread_id: str = Field(min_length=1, max_length=200)


class ChatResponse(BaseModel):
    thread_id: str
    response: str
