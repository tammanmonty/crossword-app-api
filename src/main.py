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
    version=settings.version,
    author="Tamman Montanaro",
)

@app.get('/')
def base():
    # return {'Hello': 'World'}
    logger.debug("Base Endpoint called")
    return {
        "message": "Crossword Clues API",
        "environment": settings.environment,
        "docs": "/docs"
    }

@app.get('/healthcheck')
def healthcheck():
    logger.debug("Healthcheck Endpoint called")
    return {
        "application": "Crossword Clue API",
        "version": settings.version,
        "status": "healthy"
    }

@app.get('/clues', response_model=List[CluesResponse])
def clues(db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching all clues from database")
        clues = db.query(ClueItem).all()
        logger.info(f"Fetched retrieved all clues {len(clues)}")
        return clues
    except Exception as e:
        logger.error(f"Error fetching clues: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get('/clues/{clue_id}', response_model=CluesResponse)
def clue(clue_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching clue {clue_id} from database")
        clue = db.query(ClueItem).get(clue_id)
        if clue is None:
            logger.warning(f"Clue {clue_id} not found in database")
            raise HTTPException(status_code=404, detail=f"ClueId {clue_id} not found")
        logger.info(f"Successfully retrieved clue {clue_id} from database")
        return clue
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching clue on clueId: {clue_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server error while fetching clue")



# if __name__ == '__main__':

