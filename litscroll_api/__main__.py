import uvicorn
from fastapi import FastAPI

from .routers.books import router as books_router
from .routers.quotes import router as quotes_router
from .routers.users import router as users_router

app = FastAPI(title='Books & Quotes API', version='1.0.0')
app.include_router(books_router)
app.include_router(quotes_router)
app.include_router(users_router)


@app.get('/health')
def health_check():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
