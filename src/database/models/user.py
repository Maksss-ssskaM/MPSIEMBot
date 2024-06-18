from datetime import datetime

from sqlalchemy import Column, VARCHAR, DateTime, String, ForeignKey, Boolean
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(BIGINT, unique=True, primary_key=True)
    username = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())
    password = Column(String(255))

    online_session = relationship('OnlineSession', back_populates='users', uselist=False)


class OnlineSession(Base):
    __tablename__ = 'online_sessions'
    user_id = Column(BIGINT, ForeignKey('users.user_id'), primary_key=True)
    online = Column(Boolean, default=False)
    scheduler_id = Column(String(255))
    expire_at = Column(DateTime, default=None)

    users = relationship('User', back_populates='online_session')
