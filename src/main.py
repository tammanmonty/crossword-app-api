import sys
from sqlite3 import IntegrityError

import logging
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, DatabaseError
from typing import List
from pathlib import Path

from .config import get_settings
from .models import ClueItem
from .schemas import ClueBase, ClueCreate
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

@app.get('/clues', response_model=List[ClueBase])
def clues(db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching all clues from database")
        clues = db.query(ClueItem).all()
        logger.info(f"Fetched retrieved all clues {len(clues)}")
        return clues
    except Exception as e:
        logger.error(f"Error fetching clues: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get('/clues/{clue_id}', response_model=ClueBase)
def clue(clue_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching clue {clue_id} from database")
        clue = db.query(ClueItem).filter(
            ClueItem.id == clue_id
        ).first()
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

@app.post('/clues', response_model=ClueBase, status_code=status.HTTP_201_CREATED)
def create_clue(clue_data: ClueCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to create the new clue: {clue_data.clue[0:50]}...")

        #Check for duplicate clue/answer combination
        existing_clue = db.query(ClueItem).filter(
            ClueItem.clue == clue_data.clue,
            ClueItem.answer == clue_data.answer
        ).first()

        if existing_clue:
            logger.warning(f"Duplicate clue/answer combination attempted: {clue_data.clue}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A clue with this exact Id, text or answer already exists: {existing_clue.id}"
            )

        #Creat the new clue instance
        new_clue = ClueItem(
            clue=clue_data.clue,
            answer=clue_data.answer,
            definition=clue_data.definition,
        )

        # Add to the database session
        db.add(new_clue)

        # Commit the transaction
        db.commit()

        # Refresh to get the auto-generated ID
        db.refresh(new_clue)

        logger.info(f"Successfully created the new clue: {new_clue.id}...")
        return new_clue

    except HTTPException:
        # Re-raise the HTTPException as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating the clue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data integrity violation. The clue data conflicts with database constraints."
        )
    except DataError as e:
        db.rollback()
        logger.error(f"Data error creating the clue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid data format. Check that all fields meet size and type requirements."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating clue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating clue"
        )
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error creating clue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error posting clue(s) to database: {clues} - {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Bad Request Data. Please reference API docs for specifics."
        )

    finally:
        pass

# if __name__ == '__main__':

