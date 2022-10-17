from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings
import sqlite3

_con = sqlite3.connect(settings.database_name)
cur = _con.cursor()

engine = create_engine(settings.database_url, connect_args={'check_same_thread': False})

Session = sessionmaker(engine, autocommit=False, autoflush=False)


def get_session() -> Session:
    session = Session()
    try:
        yield session
    finally:
        session.close()