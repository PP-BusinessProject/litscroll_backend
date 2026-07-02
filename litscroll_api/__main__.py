import uvicorn
from fastapi import FastAPI


app = FastAPI(title='Books & Quotes API', version='1.0.0')


@app.get('/health')
def health_check():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
