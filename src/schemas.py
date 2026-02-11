from pydantic import BaseModel, Field, field_validator
from typing import Optional

"""Pydantic Model (for API Response)"""
class ClueBase(BaseModel):
    id: int
    clue: str
    answer: str
    definition: str

    class Config:
        from_attributes = True

"""Pydanctic Model (for API Request - Creating new clues)"""
class ClueCreate(BaseModel):
    clue: str = Field(..., min_length=1, max_length=500, description="The crossword clue text")
    answer: str = Field(..., min_length=1, max_length=100, description="The answer to the crossword clue")
    definition: Optional[str] = Field(None, description="The definition of the clue")
    answer: str
    definition: str

    class Config:
        json_schema = {
            "example": {
                "clue": "Capital of France (5)",
                "answer": "PARIS",
                "definition": "The capital and largest city of France"
            }
        }
