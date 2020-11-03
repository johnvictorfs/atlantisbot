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
    role = Column(String, nullable=True)
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
        return (
            f"Team(title={repr(self.title)}, "
            f"author={repr(self.author_id)}, "
            f"team_channel_id={repr(self.team_channel_id)})"
        )


class AdvLogState(Base):
    __tablename__ = 'advlogstate'
    id = Column(Integer, primary_key=True)
    messages = Column(Boolean, default=False)


class DisabledCommand(Base):
    __tablename__ = 'disabled_command'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class PlayerActivities(Base):
    __tablename__ = 'playeractivities'
    id = Column(Integer, primary_key=True)
    activities_id = Column(String, unique=True)


class VoiceOfSeren(Base):
    __tablename__ = 'voice_of_seren'
    id = Column(Integer, primary_key=True)
    current_voice_one = Column(String)
    current_voice_two = Column(String)
    message_id = Column(String)
    updated = Column(DateTime, default=datetime.datetime.utcnow())


class IngameName(Base):
    __tablename__ = 'ingame_name'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow())

    def __str__(self):
        return self.name
