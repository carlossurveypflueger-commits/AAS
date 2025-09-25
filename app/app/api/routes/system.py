from fastapi import APIRouter
from app.core.config import settings, check_api_keys

router = APIRouter()

@router.get("/status")
async def system_status():
    """Verifica o status do sistema"""
    api_status = check_api_keys()
    
    return {
        "system": "online",
        "version": settings.version,
        "debug_mode": settings.debug,
        "integrations": {
            "openai_configured": api_status["openai"],
            "anthropic_configured": api_status["anthropic"],
            "meta_configured": api_status["meta"]
        }
    }