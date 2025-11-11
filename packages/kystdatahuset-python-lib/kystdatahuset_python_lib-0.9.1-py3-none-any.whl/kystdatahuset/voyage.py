from typing import List, Dict
from requests_cache import datetime
from kystdatahuset.api_client import post_api
from kystdatahuset.utils import date_range

def get_voyages_for_ships_by_mmsi(auth_jwt: str, mmsi_ids: List[int], start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Placeholder for getting voyages data for ships by MMSI.
    """
    date_ranges = date_range(start_date, end_date, "MS")
    for pair in date_ranges:
        print(pair)  # Debug print to verify date ranges    
        
    response = post_api(
        jwt_token=auth_jwt,
        fragment="api/voyage/for-ships/by-mmsi",
        payload={
            "mmsiIds": mmsi_ids,
            "startTime": start_date.isoformat(),
            "endTime": end_date.isoformat()
        },
    )
    
    if (response is None) or (not response["success"]):
        raise Exception(f"Failed to get voyages for ships by MMSI: {response['msg'] if response else 'No response'}")
    else:
        return response["data"]

