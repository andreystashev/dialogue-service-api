from fastapi import Depends
from jose import jwt
from jose.exceptions import JWTError
from slowapi import Limiter
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.config import settings
from app.core.security import oauth2_scheme
from app.db.database import get_db
from app.exceptions import exceptions
from app.schemas.user import User
from app.services.jwt_svc import is_active_token
from app.services.user_svc import get_user_with_id_repo


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: None | int = payload.get("user_id")
        if user_id is None:
            raise exceptions.JwtInvalidTokenException
    except JWTError:
        raise exceptions.JwtInvalidTokenException

    user = get_user_with_id_repo(
        db=db,
        id=user_id,
    )
    if user is None or not user.is_active:
        raise exceptions.JwtInvalidTokenException

    is_active_token(db, token)

    return user


def get_current_jwt_token(token: str = Depends(oauth2_scheme)) -> str:
    return token


def get_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise exceptions.AccessDeniedException

    return user


def check_user_is_owner(current_user: User, user_id: int):
    if not current_user.is_admin and (
        user_id != current_user.id or current_user.is_active is False
    ):
        raise exceptions.AccessDeniedException


def get_remote_auth_token(request: Request) -> str:
    return request.headers.get("authorization").split()[1] or " "


limiter = Limiter(key_func=get_remote_auth_token)
