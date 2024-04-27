import pytest
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app.core.config import settings
from app.schemas.history import HistoryFullCreate
from app.schemas.user import User
from app.services.history_svc import create_full_history
from app.services.jwt_svc import create_access_token


@pytest.mark.asyncio
async def test_get_dialog(
    client: TestClient,
    admin_user: User,
    db_fixture: Session,
):
    # create item in history table
    create_full_history(
        db=db_fixture,
        payload=HistoryFullCreate(
            dialog_id="task_1",
            user_id=admin_user.id,
            prompt="prompt",
            result_text="result_text",
        ),
    )

    access_token = create_access_token(
        db=db_fixture,
        user_id=admin_user.id,
    )

    res = client.get(
        url=f"{settings.API_V1_STR}/dialog/result/task_1",
        headers={
            "Authorization": f"bearer {access_token}",
        },
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        "dialog_id": "task_1",
        "prompt": "prompt",
        "result_text": "result_text",
    }
