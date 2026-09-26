from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import get_settings
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api import ingest, query

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("=" * 50)
    print(f" [{settings.APP_NAME}] Starting up in {settings.APP_ENV} mode...")
    print(f" Target Ollama Instance: {settings.OLLAMA_BASE_URL}")
    print(f" Target Qdrant Instance: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    print(f" Repository Base Path: {settings.BASE_REPO_PATH}")
    print("=" * 50)

    yield  # Application is now running and accepting requests

    # Shutdown actions
    print(f" [{settings.APP_NAME}] Shutting down gracefully...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Local Code-RAG Ingestion and Retrieval Engine for Spring Boot codebases",
    lifespan=lifespan
)

# Register sub-routers
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(query.router)


@app.get("/")
async def root():
    """Default root endpoint routing to docs."""
    return {
        "message": f"{settings.APP_NAME} Service is running.",
        "docs_url": f"http://{settings.HOST}:{settings.PORT}/docs"
    }