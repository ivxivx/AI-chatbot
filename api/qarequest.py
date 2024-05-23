from pydantic import BaseModel, Field

class QARequest(BaseModel):

    question: str = Field()