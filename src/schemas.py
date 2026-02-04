from pydantic import BaseModel

"""Pydantic Model (for API Response)"""
class CluesResponse(BaseModel):
    id: int
    clue: str
    answer: str
    definition: str

    class Config:
        from_attributes = True