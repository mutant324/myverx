import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# база лежит в файле db.sqlite3 рядом с manage.py
# (в задании сказали sqlalchemy, поэтому джанговский орм не трогаем)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

engine = create_engine(
    'sqlite:///' + DB_PATH,
    # sqlite по умолчанию запрещает юзать одно соединение из разных потоков,
    # а джанга у нас многопоточная поэтому так
    connect_args={'check_same_thread': False},
)

Base = declarative_base()

SessionMaker = sessionmaker(bind=engine)


def init_db():
    """создает таблицы если их еще нет.
    миграций у нас нет, просто create_all, для учебного проекта норм"""
    from . import models  # noqa импорт чтобы модели точно подхватились
    Base.metadata.create_all(engine)
