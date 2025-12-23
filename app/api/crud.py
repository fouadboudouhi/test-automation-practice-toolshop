import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import UserORM
from app.api.schemas import UserCreate, UserUpdate

class DuplicateEmailError(Exception):
    pass

def create_user(db: Session, data: UserCreate) -> UserORM:
    user = UserORM(email=str(data.email), name=data.name, is_active=data.is_active)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise DuplicateEmailError from e
    db.refresh(user)
    return user

def get_user(db: Session, user_id: uuid.UUID) -> UserORM | None:
    return db.get(UserORM, user_id)

def update_user(db: Session, user: UserORM, data: UserUpdate) -> UserORM:
    if data.email is not None:
        user.email = str(data.email)
    if data.name is not None:
        user.name = data.name
    if data.is_active is not None:
        user.is_active = data.is_active

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise DuplicateEmailError from e

    db.refresh(user)
    return user

def delete_user(db: Session, user: UserORM) -> None:
    db.delete(user)
    db.commit()
