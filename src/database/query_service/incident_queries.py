import uuid
from typing import Sequence, Optional

from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import Incident
from database import IncidentSeverity, IncidentStatus


async def get_incidents(
        session: AsyncSession,
        skip: int = 0, limit: int = 10,
        date_sort: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None
) -> Sequence[Incident]:
    sorting = desc(Incident.created_at) if date_sort in ('newest_first', None) else asc(Incident.created_at)

    base_query = select(Incident)

    if severity:
        severity_filters = {
            'default_severity': True,
            'high_severity': (Incident.severity == IncidentSeverity.High),
            'medium_severity': (Incident.severity == IncidentSeverity.Medium),
            'low_severity': (Incident.severity == IncidentSeverity.Low),
        }
        base_query = base_query.filter(severity_filters.get(severity, True))

    if status:
        status_filters = {
            'default_status': True,
            'new_status': (Incident.status == IncidentStatus.New),
            'approved_status': (Incident.status == IncidentStatus.Approved),
            'in_progress_status': (Incident.status == IncidentStatus.InProgress),
            'resolved_status': (Incident.status == IncidentStatus.Resolved),
            'closed_status': (Incident.status == IncidentStatus.Closed),
        }
        base_query = base_query.filter(status_filters.get(status, True))

    incidents_query = base_query.order_by(sorting).offset(skip).limit(limit)
    count_query = select(func.count()).select_from(base_query.subquery())

    incidents_result, count_result = await session.execute(incidents_query), await session.execute(count_query)
    incidents = incidents_result.scalars().all()
    incidents_count = count_result.scalar_one()

    return incidents, incidents_count


async def get_incident_by_id(session: AsyncSession, incident_id: uuid) -> Incident:
    query = (select(Incident)
             .where(Incident.incident_id == incident_id)
             .options(selectinload(Incident.events)))
    result = await session.execute(query)

    return result.scalar()


async def get_incident_by_key(session: AsyncSession, key: str):
    query = (select(Incident)
             .where(Incident.key == key)
             .options(selectinload(Incident.events)))
    result = await session.execute(query)

    return result.scalar()
