from datetime import datetime, timedelta
from uuid import UUID

import httpx
from config_data import load_config

config = load_config()

token_info = {'bearer_token': None, 'expiration_time': None}
token_refresh_threshold = timedelta(minutes=30)

DEFAULT_HEADER = {
    "User-Agent": "python-tg-bot",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "*/*"
}


async def get_siem_bearer_token():
    global token_info
    if token_info['bearer_token'] is None or datetime.now() > token_info['expiration_time'] - token_refresh_threshold:
        url = f"{config.settings.base_url}:3334/connect/token"
        data = {
            "username": config.settings.username,
            "password": config.settings.password,
            "client_id": config.settings.client_id,
            "client_secret": config.settings.client_secret,
            "grant_type": "password",
            "response_type": "code id_token",
            "scope": "authorization offline_access mpx.api ptkb.api"
        }

        headers = {
            **DEFAULT_HEADER,
            **{"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer undefined"}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                data=data,
                headers=headers,
            )
            response.raise_for_status()

            data = response.json()
            bearer_token = data.get('bearer_token')
            token_info['bearer_token'] = bearer_token
            token_info['expiration_time'] = datetime.now() + timedelta(seconds=data.get('expires_in', 0))
            return bearer_token
    else:
        return token_info['bearer_token']


async def get_siem_incidents(last_incident_time: datetime):
    if not last_incident_time:
        today = datetime.now()
        last_incident_time = (today - timedelta(days=1))

    url = f"{config.settings.base_url}:3334/api/v2/incidents"
    payload = {
        "offset": 0,
        "limit": 50,
        "groups": {"filterType": "no_filter"},
        "timeFrom": last_incident_time.isoformat(),
        "timeTo": None,
        "filterTimeType": "creation",
        "filter": {
            "select": ["key", "name", "category", "type", "status", "created", "assigned"],
            "orderby": [
                {"field": "created", "sortOrder": "descending"},
                {"field": "status", "sortOrder": "ascending"},
                {"field": "severity", "sortOrder": "descending"}
            ]
        },
        "queryIds": ["all_incidents"]
    }

    headers = {
        **DEFAULT_HEADER,
        **{'Content-Type': 'application/json', 'Authorization': f'Bearer {await get_siem_bearer_token()}'}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()['incidents']


async def get_siem_events_by_incident_id(incident_id: str):
    url = f"{config.settings.base_url}:3334/api/incidents/{incident_id}/events"
    headers = {
        **DEFAULT_HEADER,
        **{'Content-Type': 'application/json', 'Authorization': f'Bearer {await get_siem_bearer_token()}'}
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()


async def get_incident_by_incident_id(incident_id: UUID):
    url = f"{config.settings.base_url}:3334/api/incidentsReadModel/incidents/{incident_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {await get_siem_bearer_token()}"
    }
    async with httpx.AsyncClient() as client:
        return await client.get(url, headers=headers)


async def update_incident_by_incident_id(incident_data: dict):
    incident_id = incident_data["id"]
    url = f"{config.settings.base_url}:3334/api/incidents/{incident_id}"

    payload = {
        "assigned": incident_data.get("assigned", {}),
        "attackers": incident_data.get("attackers", {}),
        "description": incident_data.get("description", ""),
        "detected": incident_data.get("detected", ""),
        "events": incident_data.get("events", {}),
        "groups": incident_data.get("groups", {}),
        "influence": incident_data.get("influence", ""),
        "name": incident_data.get("name", ""),
        "parameters": incident_data.get("parameters", {}),
        "status": incident_data.get("status", ""),
        "severity": incident_data.get("severity", ""),
        "source": incident_data.get("source", ""),
        "targets": incident_data.get("targets", {}),
        "type": incident_data.get("type", ""),
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {await get_siem_bearer_token()}"
    }

    async with httpx.AsyncClient() as client:
        return await client.put(url, json=payload, headers=headers)
