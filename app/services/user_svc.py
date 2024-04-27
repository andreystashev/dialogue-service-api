from sqlalchemy.orm import Session

from app.core.security import password_hash, password_verify
from app.db.models.user import User
from app.db.repositories.user_repository import (
    create_user_repo,
    create_web_user_repo,
    get_all_users_repo,
    get_user_with_email_repo,
    get_user_with_id_repo,
    update_user_repo,
)
from app.exceptions import exceptions
from app.schemas.user import UserCreate, UserCreateWeb


def create_user(
    db: Session,
    payload: UserCreate,
) -> User:
    """
    Only for local (admin) scenarios
    """
    if payload.email is not None:
        user = get_user_with_email_repo(db=db, email=payload.email)
        if user:
            raise exceptions.UserExistException

    return create_user_repo(
        db=db,
        payload=UserCreate(
            email=payload.email,
            password=password_hash(password=payload.password),
            is_admin=payload.is_admin,
            is_active=payload.is_active,
        ),
    )


def create_web_user(
    db: Session,
    payload: UserCreateWeb,
) -> User:
    user = get_user_with_email_repo(db=db, email=payload.email)
    if user:
        raise exceptions.UserExistException

    return create_web_user_repo(
        db=db,
        payload=UserCreateWeb(
            email=payload.email,
            password=password_hash(password=payload.password),
        ),
    )


def get_user_by_id(db: Session, id: int) -> User:
    user = get_user_with_id_repo(db=db, id=id)
    if not user:
        raise exceptions.UserNotFoundException

    return user


def get_user_by_email(db: Session, email: str) -> User:
    user = get_user_with_email_repo(db=db, email=email)
    if not user:
        raise exceptions.UserNotFoundException

    return user


def get_users(db: Session) -> list[User]:
    return get_all_users_repo(db=db)


def set_user_password(db: Session, id: int, password: str, password_confirm: str):
    user = get_user_with_id_repo(db=db, id=id)
    if not user:
        raise exceptions.UserNotFoundException

    if password != password_confirm:
        raise exceptions.PasswordNotConfirmedException

    if len(password) < 8:  # noqa: PLR2004
        raise exceptions.PasswordIsNotSecureException

    update_user_repo(
        db=db, user_id=id, dict_for_update={"password": password_hash(password)}
    )
    return get_user_with_id_repo(db=db, id=id)


def activate_user(db: Session, id: int) -> User:
    user = get_user_with_id_repo(db=db, id=id)
    if not user:
        raise exceptions.UserNotFoundException

    update_user_repo(
        db=db,
        user_id=id,
        dict_for_update={
            "is_active": True,
        },
    )
    return get_user_with_id_repo(db=db, id=id)


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    user = get_user_with_email_repo(db=db, email=email)

    if not user or not password_verify(password, user.password):
        # Error to protect against login brute force
        raise exceptions.InvalidCredentialsException

    if not user.is_active:
        raise exceptions.InactiveUserProfileException

    return user
