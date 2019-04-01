import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot.orm.models import Base

# SQLite local database for development, hosted postgres database for production
if os.environ.get('DATABASE_URL'):
    engine = create_engine(os.environ.get('DATABASE_URL'), pool_size=35, max_overflow=0)
else:
    engine = create_engine('sqlite:///db.sqlite3', connect_args={'timeout': 15})

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, autoflush=False)

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine').addHandler(logging.FileHandler('db.log'))
