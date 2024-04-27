import pytest
from starlette import status
from starlette.testclient import TestClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_healthcheck_alive(
    client: TestClient,
):
    res = client.get(url=f"{settings.API_V1_STR}/healthcheck/")
    assert res.status_code == status.HTTP_200_OK
