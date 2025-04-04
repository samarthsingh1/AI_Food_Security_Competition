# app/main.py

from fastapi import FastAPI
from app.routes.trigger import router as trigger_router

app = FastAPI()

app.include_router(trigger_router)
