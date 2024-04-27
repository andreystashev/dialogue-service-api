from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.schemas.user import UserCreate, UserCreateWeb


def get_user_with_email_repo(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_with_id_repo(db: Session, id: int) -> User | None:
    return db.query(User).filter(User.id == id).first()


def get_all_users_repo(db: Session) -> list[User] | None:
    return db.query(User).all()


def create_user_repo(db: Session, payload: UserCreate) -> User:
    user = User(
        email=payload.email,
        password=payload.password,
        created_at=datetime.utcnow(),
        is_admin=payload.is_admin,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_web_user_repo(db: Session, payload: UserCreateWeb) -> User:
    user = User(
        email=payload.email,
        password=payload.password,
        created_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_repo(db: Session, user_id: int, dict_for_update: dict) -> User | None:
    stmt_update = (
        update(User)
        .where(User.id == user_id)
        .values(dict_for_update)
        .execution_options(synchronize_session=False)
        .returning(User)
    )
    result = db.scalars(stmt_update)
    db.commit()
    return result
