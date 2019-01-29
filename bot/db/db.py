import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

# SQLite local database for development, hosted postgres database for production
if os.environ.get('DATABASE_URL'):
    engine = create_engine(os.environ.get('DATABASE_URL'), pool_size=35, max_overflow=0)
else:
    engine = create_engine('sqlite:///db.sqlite3', connect_args={'timeout': 15})

Base.metadata.create_all(bind=engine)
session_maker = sessionmaker(bind=engine, autoflush=False)


class Session:
    def __enter__(self):
        self.session = session_maker()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
