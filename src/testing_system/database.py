from contextlib import closing
from typing import TypeVar, Type
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings
import sqlite3
import pymysql.cursors

T = TypeVar("T")


def _get_item(cursor, row, data_class: Type[T] = None):
    data = dict((column[0], row[index]) for index, column in enumerate(cursor.description))
    if len(data.keys()) == 1:
        item = data[next(iter(data))]
    else:
        item = data_class(**data)
    return item


def insert_and_get_id(sql, *args):
    con = sqlite3.connect(settings.database_name)
    with closing(con.cursor()) as cursor:
        cursor.execute(sql, args)
        con.commit()
        return cursor.lastrowid


def make_query(sql, data_class: Type[T] = None, *args):


    # Connect to the database
    con = pymysql.connect(host='127.0.0.1',
                                 port=3306,
                                 user='root',
                                 password='mysql_pass',
                                 database='db_name', )
    #con.execute("PRAGMA foreign_keys = ON")
    with closing(con.cursor()) as cursor:
        cursor.execute(sql, args)
        con.commit()
        for row in cursor:
            item = _get_item(cursor, row, data_class)
            if item is None:
                return None
            return item
        return None


def get_list(sql, data_class: Type[T], *args):
    con = sqlite3.connect(settings.database_name)
    with closing(con.cursor()) as cursor:
        cursor.execute(sql, args)
        data_list = []
        for row in cursor:
            item = _get_item(cursor, row, data_class)
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
