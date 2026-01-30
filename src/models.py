from sqlalchemy import Column, Integer, String, Text
from .database import Base

"""SQLAlchemy Model (for database)"""
class ClueItem(Base):
    __tablename__ = 'CROSSWORD_CLUES' # Table Name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    clue = Column(String(500), nullable=False)
    answer = Column(String(100), nullable=False)
    definition = Column(Text, nullable=True)


