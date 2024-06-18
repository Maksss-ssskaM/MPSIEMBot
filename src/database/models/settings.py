from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, Boolean

from config_data import load_config
from database import Base


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pause_time = Column(Integer, default=3)
    time_zone = Column(Integer, default=3)
    reg_pass = Column(String(255), nullable=False)
    last_incident_time = Column(DateTime, default=datetime.now())

