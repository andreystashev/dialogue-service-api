from sqlalchemy.orm import Session

from app.db.models.history import History
from app.db.repositories.history_repository import (
    create_full_history_repo,
    get_by_dialog_id_repo,
    get_by_prompt_repo,
    get_by_user_id_repo,
)
from app.exceptions import exceptions
from app.schemas.history import HistoryFullCreate


def create_full_history(
    db: Session,
    payload: HistoryFullCreate,
) -> History:
    return create_full_history_repo(
        db=db,
        dialog_id=payload.dialog_id,
        user_id=payload.user_id,
        prompt=payload.prompt,
        result_text=payload.result_text,
    )


def get_by_prompt(db: Session, prompt: str) -> History:
    """
    Search for a dialog by prompt
    """
    return get_by_prompt_repo(db=db, prompt=prompt)


def get_by_dialog_id(db: Session, dialog_id: str) -> History:
    """
    Search for a dialog by dialog_id
    """
    dialog = get_by_dialog_id_repo(db=db, dialog_id=dialog_id)
    if not dialog:
        raise exceptions.DialogNotFoundException

    return dialog


def get_by_user_id(db: Session, user_id: int) -> list[History]:
    """
    Search all dialogs by user_id
    """
    dialogs = get_by_user_id_repo(db=db, user_id=user_id)
    if not dialogs:
        raise exceptions.DialogNotFoundException

    return dialogs
