from app.config.settings import get_settings


def get_database_conn_string() -> str:
    settings = get_settings()
    return (
        f"postgresql://{settings.db_user}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
