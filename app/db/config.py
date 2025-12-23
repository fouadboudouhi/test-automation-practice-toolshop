import os

def get_database_url() -> str:
    # Default to Postgres in docker-compose; allow override.
    return os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@db:5432/appdb")
