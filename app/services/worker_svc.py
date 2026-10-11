from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.get_jokes.get_jokes import generate_joke_prompt
from app.schemas.history import HistoryFullCreate
from app.services.history_svc import create_full_history, get_by_prompt
from app.utils.app_logger import app_logger


@celery_app.task
def create_task_dialog(
    prompt: str,
    user_id: int,
):
    task_id = create_task_dialog.request.id
    db = SessionLocal()

    try:
        # Keep cache lookup and its early return inside the session lifetime.
        res_from_cache = get_by_prompt(db=db, prompt=prompt)
        if res_from_cache:
            create_full_history(
                db=db,
                payload=HistoryFullCreate(
                    dialog_id=task_id,
                    user_id=user_id,
                    prompt=prompt,
                    result_text=res_from_cache.result_text,
                ),
            )
            return {"dialog_id": task_id, "status": "success"}

        # get result from dialog service
        result_text = generate_joke_prompt(
            prompt=prompt,
        )
        # create history item with full params for image
        create_full_history(
            db=db,
            payload=HistoryFullCreate(
                dialog_id=task_id,
                user_id=user_id,
                prompt=prompt,
                result_text=result_text,
            ),
        )
        return {
            "dialog_id": task_id,
            "status": "success",
        }
    except Exception as ex:  # noqa: BLE001
        app_logger.error(
            f"create_task_dialog was performed unsuccessfully with an error {ex}"
        )
        return {
            "dialog_id": task_id,
            "status": "error",
        }
    finally:
        db.close()
