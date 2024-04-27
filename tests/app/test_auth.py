import pytest
from starlette import status
from starlette.testclient import TestClient

from app.core.config import settings
from app.db.models.user import User


@pytest.mark.asyncio
async def test_auth_valid(
    client: TestClient,
    admin_user: User,
):
    res = client.post(
        url=f"{settings.API_V1_STR}/auth/sign_in",
        data={
            "username": "admin@admin.com",
            "password": "admin",
        },
    )
    assert res.status_code == status.HTTP_200_OK
    assert "access_token" in res.json()
