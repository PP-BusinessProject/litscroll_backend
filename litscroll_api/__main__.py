import uvicorn
from fastapi import FastAPI

from .routers.books import router as books_router


app = FastAPI(title='Books & Quotes API', version='1.0.0')
app.include_router(books_router)


@app.get('/health')
def health_check():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
