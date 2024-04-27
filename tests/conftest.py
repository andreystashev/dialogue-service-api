import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.db.database import SessionLocal
from app.db.models.user import User
from app.db.utils.utils import recreate_tables
from app.main import app
from app.schemas.user import UserCreate, UserCreateWeb
from app.services.user_svc import activate_user, create_user, create_web_user


@pytest.fixture()
def db_fixture() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests(db_fixture: Session):
    recreate_tables()


def create_web(
    db_fixture: Session,
    email: str,
    password: str,
) -> User:
    user = create_web_user(
        db=db_fixture,
        payload=UserCreateWeb(
            email=email,
            password=password,
        ),
    )
    return activate_user(db=db_fixture, id=user.id)


@pytest.fixture()
def admin_user(db_fixture: Session) -> User:
    return create_user(
        db=db_fixture,
        payload=UserCreate(
            email="admin@admin.com",
            password="admin",
            is_admin=True,
            is_active=True,
        ),
    )


@pytest.fixture()
def regular_user(db_fixture: Session) -> User:
    email = "user@user.com"
    password = "user"
    return create_web(db_fixture, email, password)


@pytest.fixture()
def regular_user2(db_fixture: Session) -> User:
    email = "user2@user.com"
    password = "user2"
    return create_web(db_fixture, email, password)
