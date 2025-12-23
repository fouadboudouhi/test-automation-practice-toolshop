from app.db.session import Base, engine

def init_db() -> None:
    # Portfolio choice: create tables at startup (simple & deterministic).
    # Production: replace with Alembic migrations.
    Base.metadata.create_all(bind=engine)
