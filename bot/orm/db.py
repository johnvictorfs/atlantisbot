import logging
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot.orm.models import Base

with open('bot/bot_settings.json', 'r') as f:
    settings = json.load(f)
    database_url = settings['BOT']['database_url']

if database_url:
    engine = create_engine(database_url, pool_size=35, max_overflow=0)
else:
    engine = create_engine('sqlite:///db.sqlite3', connect_args={'timeout': 15})

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, autoflush=False)

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine').addHandler(logging.FileHandler('db.log'))
