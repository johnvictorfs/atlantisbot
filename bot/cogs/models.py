import os
import json

from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)
    title = Column(String)
    size = Column(Integer)
    role = Column(String)
    author_id = Column(String)

    invite_channel_id = Column(String)
    invite_message_id = Column(String)
    team_channel_id = Column(String)
    team_message_id = Column(String)

    def __repr__(self):
        return (f"Team(title={repr(self.title)}, "
                f"author={repr(self.author_id)}, "
                f"team_channel_id={repr(self.team_channel_id)})")


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    player_id = Column(String)
    team = Column(ForeignKey('team.id'))


class BotMessage(Base):
    __tablename__ = 'botmessage'
    id = Column(Integer, primary_key=True)
    message_id = Column(String)
    team = Column(ForeignKey('team.id'))


# SQLite local database for development, hosted postgres database for production
if os.environ.get('ATLBOT_HEROKU') == 'prod':
    engine = create_engine(os.environ.get('ATLBOT_DB_URI'))
else:
    engine = create_engine('sqlite:///teams.sqlite3', connect_args={'timeout': 15})

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


def write_example():
    """
    Write example::
        >>> session = Session()
        >>> team = Team()
        >>> team.id = 1
        >>> team.title = "Aod 15:00"
        >>> session.add(team)
        >>> session.commit()
        >>> session.close()
    """


def read_example():
    """
    Read example::
        >>> session = Session()
        >>> all_teams = session.query(Team).all()
        >>> first_team = session.query(Team).first()
        >>> first_team_messages = session.query(Team, id=first_team.id)
    """
