import json

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.exceptions import exceptions


# FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
)

instrumentator = Instrumentator().instrument(app)


@app.on_event("startup")
async def _startup():
    instrumentator.expose(app)


@app.exception_handler(exceptions.DomainException)
async def domain_exception_handler(
    _: Request,
    e: exceptions.DomainException,
):
    return JSONResponse(
        status_code=e.status_code,
        content=e.to_dict(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _: Request,
    e: StarletteHTTPException,
):
    return JSONResponse(
        status_code=e.status_code,
        content={
            "status_code": e.status_code,
            "error_details": e.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, e: RequestValidationError):
    jsonsable_body = True
    try:
        json.dumps(e.body)
    except Exception:  # noqa: BLE001
        jsonsable_body = False

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error_details": "request validation error",
            "validation_errors": e.errors(),
            "request_body": e.body if jsonsable_body else "",
        },
    )


@app.get("/", include_in_schema=False)
def homepage():
    return RedirectResponse(url="/docs/")


# Routes
app.include_router(api_router, prefix=settings.API_V1_STR)
# app.include_router(api_router, prefix=settings.API_V2_STR)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Pagination Settings
add_pagination(app)
