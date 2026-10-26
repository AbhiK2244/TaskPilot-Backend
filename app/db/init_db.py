from sqlmodel import SQLModel

from app.db.database import engine
from app.models import conversation, reminder, task  # noqa: F401


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
    print("Database tables are ready.")
