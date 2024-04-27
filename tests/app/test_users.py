import pytest
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app.core.config import settings
from app.schemas.user import User
from app.services.jwt_svc import create_access_token


@pytest.mark.asyncio
async def test_get_all(
    client: TestClient,
    admin_user: User,
    db_fixture: Session,
):
    access_token = create_access_token(
        db=db_fixture,
        user_id=admin_user.id,
    )

    res = client.get(
        url=f"{settings.API_V1_STR}/users/all",
        headers={
            "Authorization": f"bearer {access_token}",
        },
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["users"][0] == {
        "created_at": str(admin_user.created_at).replace(" ", "T"),
        "email": admin_user.email,
        "id": admin_user.id,
        "is_active": admin_user.is_active,
    }


@pytest.mark.asyncio
async def test_me(
    client: TestClient,
    admin_user: User,
    db_fixture: Session,
):
    access_token = create_access_token(
        db=db_fixture,
        user_id=admin_user.id,
    )

    res = client.get(
        url=f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"bearer {access_token}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        "created_at": str(admin_user.created_at).replace(" ", "T"),
        "email": admin_user.email,
        "id": admin_user.id,
        "is_active": admin_user.is_active,
    }
