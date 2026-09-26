from fastapi import APIRouter, Depends
from app.config import Settings, get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def check_health(settings: Settings = Depends(get_settings)):
    """
    Liveness check endpoint.
    Verifies that the FastAPI process is running and configuration settings are active.
    """
    return HealthResponse(
        status="UP",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV
    )