import time
from collections.abc import Callable

from fastapi import APIRouter
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response

from app.api.api_v1.endpoints import auth, dialog, healthcheck, users
from app.utils.app_logger import app_logger


class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            app_logger.info(f"{request.method}: {request.url}")
            app_logger.info(f"request: {request}")
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            app_logger.info(f"duration: {duration}")
            app_logger.info(f"response: {response}")
            response.headers["X-Response-Time"] = str(duration)
            return response

        return custom_route_handler


api_router = APIRouter(route_class=TimedRoute)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authorization"],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)
api_router.include_router(
    dialog.router,
    prefix="/dialog",
    tags=["Dialog"],
)
api_router.include_router(
    healthcheck.router,
    prefix="/healthcheck",
    tags=["Healthcheck"],
)
