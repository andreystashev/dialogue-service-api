"""API and worker regressions with isolated dependencies; no database connection."""
import os
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch


# Public test values only. CI can override these for its disposable PostgreSQL.
TEST_ENV = {
    "COUNT_REQUESTS_PER_MINUTES": "100",
    "SECRET_KEY": "unit-test-secret",
    "OPENAI_URL": "http://localhost/unused",
    "OPENAI_TOKEN": "",
    "CELERY_BROKER_URL": "memory://",
    "CELERY_RESULT_BACKEND": "cache+memory://",
    "POSTGRES_HOSTNAME": "127.0.0.1",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "postgres",
    "POSTGRES_DB": "dialogue_test",
}
for key, value in TEST_ENV.items():
    os.environ.setdefault(key, value)

from fastapi.testclient import TestClient  # noqa: E402

from app.api.deps import get_current_user  # noqa: E402
from app.db.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas.user import PasswordChange, UserResponse  # noqa: E402
from app.services import worker_svc  # noqa: E402


class PasswordBodyTests(unittest.TestCase):
    def setUp(self):
        self.user = UserResponse(
            id=7,
            created_at=datetime(2024, 1, 1),
            email="user@example.com",
            is_active=True,
        )
        self.db = object()
        self.original_overrides = dict(app.dependency_overrides)
        app.dependency_overrides[get_current_user] = lambda: self.user
        app.dependency_overrides[get_db] = lambda: self.db
        self.addCleanup(self.restore_overrides)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def restore_overrides(self):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)

    def test_json_password_body_reaches_service(self):
        with patch(
            "app.api.api_v1.endpoints.users.user_svc.set_user_password",
            return_value=self.user,
        ) as change:
            response = self.client.put(
                "/api/v1/users/set_password",
                json={
                    "password": "example-password",
                    "password_confirm": "example-password",
                },
            )
        assert response.status_code == 200
        change.assert_called_once_with(
            db=self.db,
            id=7,
            password="example-password",
            password_confirm="example-password",
        )
        assert "example-password" not in response.text

    def test_query_only_passwords_are_rejected(self):
        with patch(
            "app.api.api_v1.endpoints.users.user_svc.set_user_password"
        ) as change:
            response = self.client.put(
                "/api/v1/users/set_password",
                params={
                    "password": "example-password",
                    "password_confirm": "example-password",
                },
            )
        assert response.status_code == 422
        change.assert_not_called()

    def test_invalid_body_does_not_echo_password(self):
        response = self.client.put(
            "/api/v1/users/set_password", json={"password": "private-test-value"}
        )
        assert response.status_code == 422
        assert "private-test-value" not in response.text
        assert "request_body" not in response.json()

    def test_unauthenticated_password_change_is_rejected(self):
        app.dependency_overrides.pop(get_current_user)
        with patch(
            "app.api.api_v1.endpoints.users.user_svc.set_user_password"
        ) as change:
            response = self.client.put(
                "/api/v1/users/set_password",
                json={
                    "password": "example-password",
                    "password_confirm": "example-password",
                },
            )
        assert response.status_code == 401
        change.assert_not_called()

    def test_password_schema_masks_values_in_repr(self):
        payload = PasswordChange(
            password="private-test-value", password_confirm="private-test-value"
        )
        assert "private-test-value" not in repr(payload)

    def test_openapi_defines_body_and_no_password_query_parameters(self):
        operation = app.openapi()["paths"]["/api/v1/users/set_password"]["put"]
        assert "application/json" in operation["requestBody"]["content"]
        assert not any(parameter.get("in") == "query" for parameter in operation.get("parameters", []))


class WorkerSessionTests(unittest.TestCase):
    def run_task(
        self, cache=None, lookup_error=None, history_error=None, generation_error=None
    ):
        db = Mock()
        with patch.object(worker_svc, "SessionLocal", return_value=db), patch.object(
            worker_svc, "get_by_prompt", return_value=cache, side_effect=lookup_error
        ), patch.object(
            worker_svc, "create_full_history", side_effect=history_error
        ) as history, patch.object(
            worker_svc,
            "generate_joke_prompt",
            return_value="new joke",
            side_effect=generation_error,
        ) as generate, patch.object(
            worker_svc.app_logger, "error"
        ):
            worker_svc.create_task_dialog.push_request(id="unit-task")
            try:
                result = worker_svc.create_task_dialog.run(
                    prompt="test prompt", user_id=7
                )
            finally:
                worker_svc.create_task_dialog.pop_request()
        db.close.assert_called_once()
        return result, history, generate

    def test_cache_hit_closes_session_without_generating(self):
        result, history, generate = self.run_task(
            cache=SimpleNamespace(result_text="cached joke")
        )
        assert result == {"dialog_id": "unit-task", "status": "success"}
        assert history.call_args.kwargs["payload"].result_text == "cached joke"
        generate.assert_not_called()

    def test_cache_miss_closes_session_after_success(self):
        result, history, generate = self.run_task()
        assert result["status"] == "success"
        assert history.call_args.kwargs["payload"].result_text == "new joke"
        generate.assert_called_once_with(prompt="test prompt")

    def test_cache_lookup_error_closes_session(self):
        result, _, generate = self.run_task(lookup_error=RuntimeError("lookup failed"))
        assert result["status"] == "error"
        generate.assert_not_called()

    def test_cached_history_error_closes_session(self):
        result, _, generate = self.run_task(
            cache=SimpleNamespace(result_text="cached joke"),
            history_error=RuntimeError("write failed"),
        )
        assert result["status"] == "error"
        generate.assert_not_called()

    def test_generation_error_closes_session(self):
        result, _, _ = self.run_task(generation_error=RuntimeError("generation failed"))
        assert result["status"] == "error"

    def test_new_history_error_closes_session(self):
        result, _, _ = self.run_task(history_error=RuntimeError("write failed"))
        assert result["status"] == "error"
