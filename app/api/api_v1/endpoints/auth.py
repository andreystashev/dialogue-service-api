from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_jwt_token, get_current_user
from app.db.database import get_db
from app.schemas.exceptions import ExceptionMessage
from app.schemas.jwt_token import (
    JWTTokenDisabledResponse,
    JWTTokenResponse,
    RefreshToken,
)
from app.schemas.user import UserResponse
from app.services.jwt_svc import (
    create_access_token,
    deactivate_token,
    refresh_access_token,
)
from app.services.user_svc import authenticate_user


router = APIRouter()


@router.post(
    "/sign_in",
    response_model=JWTTokenResponse,
    status_code=200,
    responses={
        409: {"model": ExceptionMessage},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> JWTTokenResponse:
    """
    Authorization of the current user by email and password

    We use OAuth2PasswordRequestForm so that we can
    conveniently test the service via openapi docs view
    """
    user = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )
    access_token = create_access_token(
        db=db,
        user_id=user.id,
    )

    return JWTTokenResponse(
        access_token=access_token,
    )


@router.post(
    "/refresh_token",
    response_model=JWTTokenResponse,
    status_code=200,
    responses={
        401: {"model": ExceptionMessage},
    },
)
async def refresh_token(
    refresh_token: RefreshToken,
    db: Session = Depends(get_db),
):
    """
    Updating an expired token
    """
    access_token = refresh_access_token(db=db, token=refresh_token.refresh_token)
    return JWTTokenResponse(access_token=access_token)


@router.post(
    "/logout",
    response_model=JWTTokenDisabledResponse,
    status_code=200,
    responses={
        403: {"model": ExceptionMessage},
    },
)
async def logout(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    jwt_token: str = Depends(get_current_jwt_token),
):
    """
    User Logout
    """
    jwt = deactivate_token(db=db, token_hash=jwt_token)
    return JWTTokenDisabledResponse(access_token_disabled=jwt.token)
