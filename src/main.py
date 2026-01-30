import sys
import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from .config import get_settings
from .models import ClueItem
from .schemas import CluesResponse
from .database import get_db, engine, Base

settings = get_settings()

# Add file handler if enabled
if settings.log_to_file:
    # Create logs directory if it doesn't exist
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

""" Configure the Logger Information"""
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=settings.log_level.upper(),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_file)
    ]
)

logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="CROSSWORD CLUES API",
    description="API for accessing crossword clues, answers, and definitions",
    version="1.0.0",
    author="Tamman Montanaro",
)

@app.get('/')
def get_root():
    # return {'Hello': 'World'}
    logger.debug("Base Endpoint called")
    return {
        "message": "Crossword Clues API",
        "environment": settings.environment,
        "docs": "/docs"
    }

@app.get('/clues', response_model=List[CluesResponse])
def get_clues(db: Session = Depends(get_db)):
    # return {
    #     'clue': 'example clue',
    #     'answer': 'example answer',
    #     'definition': 'example definition',
    #     }
    try:
        logger.info(f"Fetching all clues from database")
        clues = db.query(ClueItem).all()
        logger.info(f"Fetched retrieved all clues {len(clues)}")
        return clues
    except Exception as e:
        logger.error(f"Error fetching clues: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")






# if __name__ == '__main__':

