from sqlalchemy import Column, String, DateTime, Enum, Integer, UUID, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Event(Base):
    __tablename__ = 'events'
    incident_id = Column(UUID, ForeignKey('incidents.incident_id'), nullable=False)
    event_id = Column(UUID, unique=True, primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    description = Column(String(255), nullable=False)

    incident = relationship('Incident', back_populates='events', uselist=False)
