from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.web.routes import router as web_router

def create_app() -> FastAPI:
    app = FastAPI(title="User Management API", version="0.1.0")
    app.include_router(api_router, prefix="/api")
    app.include_router(web_router, prefix="")

    # Placeholders for future static assets
    app.mount("/static", StaticFiles(directory="app/web/static", check_dir=False), name="static")
    return app

app = create_app()
