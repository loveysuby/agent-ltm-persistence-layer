from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import memory
from app.api.schemas import APIResponse, ErrorResponse
from app.config.lifespan import lifespan

app = FastAPI(
    title="Agent Long-term Memory API",
    description="Agent Long-term Memory system",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(memory.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug", access_log=True)
