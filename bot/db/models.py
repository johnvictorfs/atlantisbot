import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

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


class AdvLogState(Base):
    __tablename__ = 'advlogstate'
    id = Column(Integer, primary_key=True)
    messages = Column(Boolean, default=True)


class PlayerActivities(Base):
    __tablename__ = 'playeractivities'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    activities = Column(String, default="[]")


# class AmigoSecreto(Base):
#     __tablename__ = 'amigosecreto'
#     id = Column(Integer, primary_key=True)
#     discord_name = Column(String, )
#     ingame_name = ''
#     question = relationship('AmigoSecreto', remote_side=[id], backref=backref('name'), uselist=False)
