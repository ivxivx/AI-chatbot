from pydantic import BaseModel, Field

class QAResponse(BaseModel):
    
    answer: str = Field()