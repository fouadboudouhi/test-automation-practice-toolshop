from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import UserORM
from app.api.schemas import UserCreate, UserUpdate
from app.api import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    users = db.query(UserORM).order_by(UserORM.created_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

@router.post("/users")
def ui_create(db: Session = Depends(get_db), email: str = "", name: str = ""):
    crud.create_user(db, UserCreate(email=email, name=name, is_active=True))
    return RedirectResponse(url="/", status_code=303)

@router.post("/users/{user_id}/update")
def ui_update(user_id: str, db: Session = Depends(get_db), email: str = "", name: str = ""):
    user = db.get(UserORM, user_id)
    if user:
        crud.update_user(db, user, UserUpdate(email=email or None, name=name or None))
    return RedirectResponse(url="/", status_code=303)

@router.post("/users/{user_id}/delete")
def ui_delete(user_id: str, db: Session = Depends(get_db)):
    user = db.get(UserORM, user_id)
    if user:
        crud.delete_user(db, user)
    return RedirectResponse(url="/", status_code=303)
