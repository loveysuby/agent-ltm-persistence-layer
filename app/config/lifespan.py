from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Agent Long-term Memory system...")
    print("API docs: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print(f"Startup time: {datetime.now().isoformat()}")
    yield

    print("Shutting down system...")
