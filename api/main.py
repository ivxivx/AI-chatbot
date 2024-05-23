from fastapi import FastAPI
from api.router import api_router

def get_app() -> FastAPI:
    fast_app = FastAPI(title="chatbot", version="1", debug="false")
    fast_app.include_router(api_router, prefix="/api")

    return fast_app


app = get_app()
