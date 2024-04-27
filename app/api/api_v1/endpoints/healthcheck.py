from fastapi import APIRouter, Response
from starlette import status


router = APIRouter()


@router.get("", include_in_schema=False)
async def healthcheck(response: Response):
    try:
        # test any
        return {"status": "alive"}

    except Exception as e:  # noqa: BLE001
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "dead", "error": str(e)}
