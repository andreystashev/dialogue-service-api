from app.db.database import engine
from app.db.models.base import Base


def recreate_tables() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
