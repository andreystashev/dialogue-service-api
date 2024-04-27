import time

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Request
from fastapi_pagination import LimitOffsetPage, Page, paginate
from sqlalchemy.orm import Session

from app.api.deps import check_user_is_owner, get_current_user, limiter
from app.core.config import settings
from app.db.database import get_db
from app.schemas.dialog import (
    GenerationRequest,
    GenerationResult,
    GenerationResultAll,
    GenerationResultText,
    GenerationStatus,
)
from app.schemas.exceptions import ExceptionMessage
from app.schemas.user import UserResponse
from app.services.history_svc import get_by_dialog_id, get_by_user_id
from app.services.worker_svc import create_task_dialog


router = APIRouter()


@router.post(
    "/create",
    response_model=GenerationResult,
    status_code=200,
    responses={
        409: {"model": ExceptionMessage},
    },
)
@limiter.limit(f"{settings.COUNT_REQUEST_DIALOG_PER_MINUTES}/minute")
async def create_dialog(
    request: Request,
    gen_req: GenerationRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Creating a request to receive text from the input prompt.
    Celery is used for simplicity. Tasks are being performed on hold,
    on the client side it is necessary to monitor the status of the task
    and get the result after achieving a successful status.

    In the future, it is necessary to use kafka as a transport
    of tasks to a separate ml server
    """
    start = time.time()

    task = create_task_dialog.apply_async(
        args=(
            gen_req.prompt,
            current_user.id,
        ),
        queue="default",
    )

    elapsed = time.time() - start
    return GenerationResult(dialog_id=task.id, time=elapsed)


@router.get(
    "/status/{dialog_id}",
    response_model=GenerationStatus,
    status_code=200,
    responses={
        404: {"model": ExceptionMessage},
        403: {"model": ExceptionMessage},
        409: {"model": ExceptionMessage},
    },
)
async def get_status(
    dialog_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Getting the status of a celery task according to id
    """
    task_result = AsyncResult(dialog_id)
    task_status = task_result.status

    return GenerationStatus(
        dialog_id=dialog_id,
        status=task_status,
    )


@router.get(
    "/result/{dialog_id}",
    response_model=GenerationResultText,
    status_code=200,
    responses={
        404: {"model": ExceptionMessage},
        403: {"model": ExceptionMessage},
        409: {"model": ExceptionMessage},
    },
)
async def get_result(
    dialog_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Getting the result of generation after achieving a successful status in the task
    """
    task_result = get_by_dialog_id(
        db=db,
        dialog_id=dialog_id,
    )

    # We check that the dialog refers to the current user, or the request is executed by the administrator
    check_user_is_owner(current_user=current_user, user_id=task_result.user_id)

    return GenerationResultText(
        dialog_id=dialog_id,
        prompt=task_result.prompt,
        result_text=task_result.result_text,
    )


@router.get("/history", response_model=Page[GenerationResultAll])
@router.get(
    "/history/limit-offset", response_model=LimitOffsetPage[GenerationResultAll]
)
async def get_user_dialogs(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Getting the dialog history for a given user with pagination.
    A third-party library is used for pagination.
    In the future, it is necessary to implement its own mechanism
    """

    # We check that the request refers to the current user, or the request is executed by the administrator
    check_user_is_owner(current_user=current_user, user_id=user_id)

    user_dialog_list = list(
        get_by_user_id(
            db=db,
            user_id=user_id,
        )
    )

    return paginate(user_dialog_list)
