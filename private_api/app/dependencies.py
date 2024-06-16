from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

API_KEYS = ["JflNaq4Pmsh8fhJq"]

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in API_KEYS:
        return api_key_header
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")