from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, memories, structured_memories
from app.api.schemas import APIResponse, ErrorResponse
from app.infrastructure.database import close_database, initialize_database

app = FastAPI(
    title="Agent Long-term Memory API",
    description="LangGraph + LangMem + pgvector based Agent Long-term Memory system",
    version="0.2.0",
)

app.include_router(chat.router)
app.include_router(memories.router)
app.include_router(structured_memories.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/", response_model=APIResponse)
async def root() -> APIResponse:
    return APIResponse(success=True, message="Agent Long-term Memory API")


@app.get("/health", response_model=APIResponse)
async def health_check() -> APIResponse:
    return APIResponse(success=True, message="Service is healthy")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_response = ErrorResponse(success=False, error="Internal server error")
    return JSONResponse(status_code=500, content=error_response.model_dump())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
