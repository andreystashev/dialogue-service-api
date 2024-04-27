from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.models.jwt_token import JwtToken
from app.schemas.jwt_token import JWTTokenCreate


def create_token_repo(db: Session, payload: JWTTokenCreate):
    user = JwtToken(
        user_id=payload.user_id,
        token=payload.token,
        created_at=datetime.utcnow(),
        expires=payload.expires,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_token_repo(db: Session, token: str) -> JwtToken | None:
    return db.query(JwtToken).filter(JwtToken.token == token).first()


def get_token_by_id_repo(db: Session, id: int) -> JwtToken | None:
    return db.query(JwtToken).filter(JwtToken.id == id).first()


def delete_token_by_id_repo(db: Session, id: int) -> JwtToken | None:
    obj = (
        db.query(JwtToken)
        .filter(
            JwtToken.id == id,
        )
        .first()
    )
    db.delete(obj)
    db.commit()
    return obj


def activate_token_repo(db: Session, token: str):
    stmt_update = (
        update(JwtToken)
        .where(JwtToken.token == token)
        .values(is_active=True)
        .execution_options(synchronize_session=False)
        .returning(JwtToken)
    )
    result = db.scalars(stmt_update)
    db.commit()
    return result


def deactivate_token_repo(db: Session, token: str):
    stmt_update = (
        update(JwtToken)
        .where(JwtToken.token == token)
        .values(is_active=False)
        .execution_options(synchronize_session=False)
        .returning(JwtToken)
    )
    result = db.scalars(stmt_update)
    db.commit()
    return result
