import httpx

from config_data import load_config

config = load_config()


async def submit_new_incidents_to_server(incidents):
    async with httpx.AsyncClient() as client:
        response = await client.post(f'{config.web_app.api_url}/incidents/submit-new-incidents', json=incidents)
        return response.json()
