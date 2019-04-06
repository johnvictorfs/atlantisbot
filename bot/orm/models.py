import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    player_id = Column(String)
    in_team = Column(Boolean)
    substitute = Column(Boolean, default=False)
    secondary = Column(Boolean, default=False)
    team = Column(Integer, ForeignKey('team.id', ondelete='CASCADE'))


class BotMessage(Base):
    __tablename__ = 'botmessage'
    id = Column(Integer, primary_key=True)
    message_id = Column(String)
    team = Column(Integer, ForeignKey('team.id', ondelete='CASCADE'))


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow())
    team_id = Column(String, unique=True)
    title = Column(String)
    size = Column(Integer)
    role = Column(String)
    role_secondary = Column(String)
    author_id = Column(String)
    invite_channel_id = Column(String)
    invite_message_id = Column(String)
    team_channel_id = Column(String)
    team_message_id = Column(String)
    secondary_limit = Column(Integer, nullable=True)

    players = relationship(Player, backref='parent', cascade="all,delete,delete-orphan")
    botmessages = relationship(BotMessage, backref='parent', cascade="all,delete,delete-orphan")

    def __repr__(self):
        return (f"Team(title={repr(self.title)}, "
                f"author={repr(self.author_id)}, "
                f"team_channel_id={repr(self.team_channel_id)})")


class RaidsState(Base):
    __tablename__ = 'raidsstate'
    id = Column(Integer, primary_key=True)
    notifications = Column(Boolean, default=False)
    time_to_next_message = Column(String, nullable=True)


class AdvLogState(Base):
    __tablename__ = 'advlogstate'
    id = Column(Integer, primary_key=True)
    messages = Column(Boolean, default=False)


class PlayerActivities(Base):
    __tablename__ = 'playeractivities'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    clan = Column(String)
    activities = Column(String, default="[]")


class AmigoSecretoPerson(Base):
    __tablename__ = 'amigosecreto'
    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True)
    discord_name = Column(String)
    ingame_name = Column(String)
    giving_to_id = Column(Integer, nullable=True, default=None, unique=True)
    giving_to_name = Column(String, nullable=True, default=None, unique=True)
    receiving = Column(Boolean, default=False)


class AmigoSecretoState(Base):
    __tablename__ = 'amigosecretostate'
    id = Column(Integer, primary_key=True)
    activated = Column(Boolean, default=False)
