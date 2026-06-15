from pydantic import BaseModel


class AssistantQuery(BaseModel):
    question: str


class AssistantResponse(BaseModel):
    answer: str