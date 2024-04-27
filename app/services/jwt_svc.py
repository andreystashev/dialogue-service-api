from datetime import datetime, timedelta

from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.jwt_token import JwtToken
from app.db.repositories.jwt_token_repository import (
    activate_token_repo,
    create_token_repo,
    deactivate_token_repo,
    delete_token_by_id_repo,
    get_token_by_id_repo,
    get_token_repo,
)
from app.exceptions import exceptions
from app.schemas.jwt_token import JWTTokenCreate


def refresh_access_token(db: Session, token: str) -> str:
    jwttoken = is_active_token(
        db=db,
        token_hash=token,
    )

    deactivate_token(
        db=db,
        token_hash=token,
    )

    t = jwttoken.expires + timedelta(minutes=settings.ACCESS_TOKEN_REFRESH_MINUTES)
    if t < datetime.utcnow():
        raise exceptions.JwtExpiredTokenException

    return create_access_token(
        db=db,
        user_id=jwttoken.user_id,
    )


def create_access_token(
    db: Session,
    user_id: int,
    expire_minutes: int | None = None,
) -> str:
    minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    if expire_minutes is not None:
        minutes = expire_minutes

    expire = datetime.utcnow() + timedelta(minutes=minutes)

    encoded = jwt.encode(
        claims={
            "user_id": user_id,
            "exp": expire,
            "expiration_time": str(expire),
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    create_token(
        db=db,
        payload=JWTTokenCreate(
            user_id=user_id,
            token=encoded,
            expires=expire,
        ),
    )

    return encoded


def create_token(db: Session, payload: JWTTokenCreate) -> JwtToken:
    token = get_token_repo(
        db=db,
        token=payload.token,
    )
    if token:
        deactivate_token(
            db=db,
            token_hash=payload.token,
        )

    create_token_repo(
        db=db,
        payload=payload,
    )
    return get_token_repo(
        db=db,
        token=payload.token,
    )  # @todo


def is_active_token(db: Session, token_hash: str) -> JwtToken:
    token = get_token_repo(
        db=db,
        token=token_hash,
    )
    if not token or not token.is_active:
        raise exceptions.JwtInactiveTokenException

    return token


def activate_token(db: Session, token_hash: str) -> JwtToken:
    token = get_token_repo(
        db=db,
        token=token_hash,
    )
    if not token:
        raise exceptions.JwtTokenNotExistsException

    activate_token_repo(
        db=db,
        token=token_hash,
    )
    return get_token_repo(
        db=db,
        token=token_hash,
    )  # @todo


def deactivate_token(db: Session, token_hash: str) -> JwtToken:
    token = get_token_repo(
        db=db,
        token=token_hash,
    )
    if not token:
        raise exceptions.JwtTokenNotExistsException

    deactivate_token_repo(
        db=db,
        token=token_hash,
    )
    return get_token_repo(
        db=db,
        token=token_hash,
    )  # @todo


def delete_token_by_id(db: Session, id: int) -> None:
    token = get_token_by_id_repo(
        db=db,
        id=id,
    )
    if not token:
        raise exceptions.JwtTokenNotExistsException

    delete_token_by_id_repo(
        db=db,
        id=id,
    )
