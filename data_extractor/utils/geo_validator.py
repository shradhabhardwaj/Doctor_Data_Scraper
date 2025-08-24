# data_extractor/utils/geo_validator.py

import httpx
import asyncio # Import asyncio
from .config import PUNE_BOUNDING_BOX, REQUEST_TIMEOUT
from ..utils.logger import app_logger

async def get_coordinates(address: str, client: httpx.AsyncClient) -> dict | None:
    """
    Uses the free Nominatim (OpenStreetMap) API to get coordinates for an address.
    NOTE: This API has a strict usage policy (max 1 request/sec). A delay is added.
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "DoctorDataScraper/1.0 (shradha.bhardwaj9@gmail.com)"}

    try:
        # --- KEY FIX: Respect the API's rate limit ---
        await asyncio.sleep(1) 
        
        response = await client.get(base_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if data:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"])
            }
        return None
    except (httpx.RequestError, httpx.HTTPStatusError, IndexError, KeyError) as e:
        app_logger.warning(f"Geocoding failed for address '{address}': {e}")
        return None

def is_within_pune(lat: float, lon: float) -> bool:
    """Checks if the given coordinates fall within Pune's bounding box."""
    bbox = PUNE_BOUNDING_BOX
    return (bbox["min_lat"] <= lat <= bbox["max_lat"]) and \
           (bbox["min_lon"] <= lon <= bbox["max_lon"])