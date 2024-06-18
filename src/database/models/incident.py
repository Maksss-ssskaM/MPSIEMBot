import enum

from sqlalchemy import Column, String, DateTime, Enum, UUID
from sqlalchemy.orm import relationship

from database import Base


class IncidentSeverity(enum.Enum):
    High = 'Высокий 🔴'
    Medium = 'Средний 🟠'
    Low = 'Низкий 🟡'


class IncidentStatus(enum.Enum):
    New = 'Новый'
    Approved = 'Утверждён'
    InProgress = 'В работе'
    Resolved = 'Разрешён'
    Closed = 'Закрыт'


class Incident(Base):
    __tablename__ = 'incidents'
    incident_id = Column(UUID, primary_key=True, unique=True, nullable=False)
    key = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Enum(IncidentStatus), nullable=False)
    type = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    severity = Column(Enum(IncidentSeverity), nullable=False)

    events = relationship('Event', back_populates='incident')




