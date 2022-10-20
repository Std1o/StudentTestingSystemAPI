from contextlib import closing
from typing import TypeVar, Type
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings
import sqlite3


T = TypeVar("T")
primitive = (int, str, bool, float)


def make_query(sql, data_class: Type[T] = None, *args):
    con = sqlite3.connect(settings.database_name)
    with closing(con.cursor()) as cursor:
        cursor.execute(sql, args)
        con.commit()
        for row in cursor:
            item = dict((column[0], row[index]) for index, column in enumerate(cursor.description))
            if not item:
                return None
            return data_class(**item)
        return None


def is_primitive(thing):
    return isinstance(thing, primitive)


def get_list(sql, data_class: Type[T], *args):
    con = sqlite3.connect(settings.database_name)
    with closing(con.cursor()) as cursor:
        cursor.execute(sql, args)
        data_list = []
        for row in cursor:
            data = dict((column[0], row[index]) for index, column in enumerate(cursor.description))
            if len(data.keys()) == 1:
                item = data[next(iter(data))]
            else:
                item = data_class(**data)
            data_list.append(item)
        return data_list


engine = create_engine(settings.database_url, connect_args={'check_same_thread': False})

Session = sessionmaker(engine, autocommit=False, autoflush=False)


def get_session() -> Session:
    session = Session()
    try:
        yield session
    finally:
        session.close()