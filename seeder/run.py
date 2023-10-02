from app.db import session


def drop_all_tables() -> None:
    session.drop_all_tables()
