import os
from starlette.responses import JSONResponse
from fastapi import FastAPI
app = FastAPI()


@app.get('/')
async def root():
    return JSONResponse({'message': os.getenv('API_MESSAGE', 'Hello kubernetes!')}, status_code=200)


@app.get('/health')
async def health_check():
    return JSONResponse({'message': 'I\'m fine.'}, status_code=200)
