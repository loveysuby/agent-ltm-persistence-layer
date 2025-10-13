from typing import Annotated

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.core.services import AgentService


def get_db_settings(settings: Annotated[Settings, Depends(get_settings)]) -> dict:
    return {
        "host": settings.db_host,
        "port": settings.db_port,
        "database": settings.db_name,
        "user": settings.db_user,
        "password": settings.db_password,
    }


def get_agent_service(user_id: str) -> AgentService:
    return AgentService(user_id=user_id)
