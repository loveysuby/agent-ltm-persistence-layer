from app.config.settings import get_settings
from app.core.services import AgentService


def get_database_conn_string() -> str:
    settings = get_settings()
    return (
        f"postgresql://{settings.db_user}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


def get_agent_service(user_id: str) -> AgentService:
    return AgentService(user_id=user_id)
