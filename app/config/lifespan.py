from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI

from app.infrastructure.database import close_database, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Agent Long-term Memory system...")
    print("API docs: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print(f"Startup time: {datetime.now().isoformat()}")
    try:
        await initialize_database()
        print("Database connected successfully")

    except Exception as e:
        print(f"Initialization failed: {e}")
        raise

    yield

    print("Shutting down system...")
    try:
        await close_database()
        print("Database connection closed")
    except Exception as e:
        print(f"Cleanup failed: {e}")
