from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import check_user_is_owner, get_admin_user, get_current_user
from app.db.database import get_db
from app.schemas.exceptions import ExceptionMessage
from app.schemas.user import (
    User,
    UserCreateWeb,
    UserListResponse,
    UserResponse,
)
from app.services import user_svc


router = APIRouter()


@router.put(
    "/set_password",
    response_model=UserResponse,
    responses={404: {"model": ExceptionMessage}},
)
async def set_password(
    password: str,
    password_confirm: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Changes the user's password
    """
    return user_svc.set_user_password(
        db=db,
        id=current_user.id,
        password=password,
        password_confirm=password_confirm,
    )


@router.put(
    "/activate/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ExceptionMessage}},
)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user),
):
    """
    Only admin

    Activates the user by user_id.
    Functionality with a perspective for the future.
    If you need a mechanism for approving/filtering new users
    """
    return user_svc.activate_user(db=db, id=user_id)


@router.get(
    "/all",
    response_model=UserListResponse,
    responses={404: {"model": ExceptionMessage}},
)
async def get_users(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_admin_user),
):
    """
    Only admin

    Returns information about all users
    """
    users = user_svc.get_users(db=db)

    users_response: list[UserResponse] = []

    for user in users:
        users_response.append(user)

    return UserListResponse(users=users_response)


@router.post(
    "/user/",
    response_model=UserResponse,
    status_code=201,
    responses={409: {"model": ExceptionMessage}},
)
async def create_web_user(
    payload: UserCreateWeb,
    db: Session = Depends(get_db),
):
    """
    Creates a user
    """
    return user_svc.create_web_user(db, payload)


@router.get(
    "/user/{email}",
    response_model=UserResponse,
    responses={
        404: {"model": ExceptionMessage},
        403: {"model": ExceptionMessage},  # нет прав
    },
)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Returns information about the user by his email
    """
    user = user_svc.get_user_by_email(db=db, email=email)

    # We check that this current user, or the request is executed by the administrator
    check_user_is_owner(current_user=current_user, user_id=user.id)

    return user


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """
    User Profile
    """
    return current_user
