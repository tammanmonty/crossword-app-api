from sqlalchemy import Column, Integer, String, Text
from .database import Base

class ClueItem(Base):
    __tablename__ = 'CROSSWORD_CLUES' # Table Name

    id = Column(Integer, primary_key=True, index=True)
    clue = Column(Text, nullable=False)
    answer = Column(String, nullable=False)
    definition = Column(Text, nullable=False)