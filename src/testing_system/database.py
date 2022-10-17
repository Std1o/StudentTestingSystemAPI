from contextlib import closing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings
import sqlite3


def make_query(sql, *args):
    con = sqlite3.connect(settings.database_name)
    with closing(con.cursor()) as cursor:
        cursor.execute(sql, args)
        con.commit()
        for row in cursor:
            return dict((column[0], row[index]) for index, column in enumerate(cursor.description))
        return None


engine = create_engine(settings.database_url, connect_args={'check_same_thread': False})

Session = sessionmaker(engine, autocommit=False, autoflush=False)


def get_session() -> Session:
    session = Session()
    try:
        yield session
    finally:
        session.close()