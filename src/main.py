from fastapi import FastAPI

app = FastAPI()

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

