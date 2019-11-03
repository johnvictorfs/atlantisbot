from contextlib import contextmanager
from typing import ContextManager
import logging
import json
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, object_session
from sqlalchemy.event import listens_for
from sqlalchemy.orm.attributes import Event
from sqlalchemy.orm.session import Session as SqlASession
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper

from bot.orm.models import Base, User, IngameName


database_url = os.environ.get('DATABASE_URL')

if not database_url:
    try:
        with open('bot/bot_settings.json', 'r') as f:
            settings = json.load(f)
            database_url = settings['BOT']['database_url']
    except FileNotFoundError:
        print('No bot/bot_settings.json file found.')
        sys.exit(1)

if database_url:
    engine = create_engine(database_url, pool_size=35, max_overflow=0)
else:
    engine = create_engine('sqlite:///db.sqlite3', connect_args={'timeout': 15})

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, autoflush=False)

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine').addHandler(logging.FileHandler('db.log'))


@listens_for(User.ingame_name, 'set')
def add_ingame_name_update(target: User, value: str, oldvalue: str, initiator: Event):
    """
    Create new IngameName instance everytime the ingame_name of a User gets updated
    """
    if target.id:
        object_session(target).add(IngameName(name=value, user=target.id))


@listens_for(User, 'after_insert')
def add_ingame_name_creation(mapper: Mapper, connection: Connection, target: User):
    """
    Create new IngameName instance once the User is first created with its ingame_name
    """
    if target.id:
        object_session(target).add(IngameName(name=target.ingame_name, user=target.id))


@contextmanager
def db_session() -> ContextManager[SqlASession]:
    """
    http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
    Provide a transactional scope around a series of operations.
    """
    session: SqlASession = Session()

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
