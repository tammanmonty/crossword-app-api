from fastapi import FastAPI
import logging
from .config import get_settings
import sys
from pathlib import Path



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
app = FastAPI(
    title="CROSSWORD CLUES API",
    description="API for accessing crossword clues, answers, and definitions",
    version="1.0.0",
    author="Tamman Montanaro",
)

@app.get('/crossword')
def read_root():
    return {'Hello': 'World'}


@app.get('/crossword/items')
def read_clues():
    return {
        'clue': 'example clue',
        'answer': 'example answer',
        'definition': 'example definition',
        }


# if __name__ == '__main__':

