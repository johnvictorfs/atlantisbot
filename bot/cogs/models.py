import os
import datetime

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    player_id = Column(String)
    team = Column(Integer, ForeignKey('team.id', ondelete='CASCADE'))


class BotMessage(Base):
    __tablename__ = 'botmessage'
    id = Column(Integer, primary_key=True)
    message_id = Column(String)
    team = Column(ForeignKey('team.id', ondelete='CASCADE'))


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow())
    team_id = Column(Integer, unique=True)
    title = Column(String)
    size = Column(Integer)
    role = Column(String)
    author_id = Column(String)

    invite_channel_id = Column(String)
    invite_message_id = Column(String)
    team_channel_id = Column(String)
    team_message_id = Column(String)

    players = relationship(Player, backref='parent', passive_deletes=True)
    botmessages = relationship(BotMessage, backref='parent', passive_deletes=True)

    def __repr__(self):
        return (f"Team(title={repr(self.title)}, "
                f"author={repr(self.author_id)}, "
                f"team_channel_id={repr(self.team_channel_id)})")


class RaidsState(Base):
    __tablename__ = 'raidsstate'
    id = Column(Integer, primary_key=True)
    notifications = Column(Boolean, default=True)


# SQLite local database for development, hosted postgres database for production
if os.environ.get('ATLBOT_HEROKU') == 'prod':
    engine = create_engine(os.environ.get('ATLBOT_DB_URI'))
else:
    engine = create_engine('sqlite:///teams.sqlite3', connect_args={'timeout': 15})

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, autoflush=False)
