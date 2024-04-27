from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.models.history import History


def get_all_history(db: Session):
    return db.query(History).all()


def get_by_dialog_id_repo(
    db: Session,
    dialog_id: str,
):
    return (
        db.query(History)
        .filter(
            History.dialog_id == dialog_id,
        )
        .first()
    )


def get_by_user_id_repo(
    db: Session,
    user_id: int,
):
    return (
        db.query(History)
        .filter(
            History.user_id == user_id,
        )
        .all()
    )


def get_by_prompt_repo(
    db: Session,
    prompt: str,
):
    return (
        db.query(History)
        .filter(
            History.prompt == prompt,
        )
        .first()
    )


def create_history_repo(
    db: Session,
    dialog_id: str,
    user_id: int,
    prompt: str,
):
    history = History(
        dialog_id=dialog_id,
        user_id=user_id,
        prompt=prompt,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def create_full_history_repo(
    db: Session,
    dialog_id: str,
    user_id: int,
    prompt: str,
    result_text: str,
):
    history = History(
        dialog_id=dialog_id,
        user_id=user_id,
        prompt=prompt,
        result_text=result_text,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def update_history_repo(db: Session, dialog_id: str, dict_for_update: dict):
    stmt_update = (
        update(History)
        .where(History.dialog_id == dialog_id)
        .values(dict_for_update)
        .execution_options(synchronize_session=False)
        .returning(History)
    )
    result = db.scalars(stmt_update)
    db.commit()
    return result


def delete_history_repo(
    db: Session,
    dialog_id: str,
):
    obj = (
        db.query(History)
        .filter(
            History.dialog_id == dialog_id,
        )
        .first()
    )
    db.delete(obj)
    db.commit()
    return obj
